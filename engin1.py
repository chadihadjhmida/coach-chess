from re import findall
from stockfish import Stockfish
from chess import *
import chess.engine
from stockfish import Stockfish
import os
from groq import Groq
import gtts
from pydub import AudioSegment
from pydub.playback import play
import whisper
import subprocess
import cv2

# Load the tiny English model
model = whisper.load_model("tiny.en")

# the directury where the qestion.mp3 will be there
directory = "path/to/your/folder"

# Specify the file name
file_name = "question.mp3"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# i'm just tasting the how stockfish work idk i'm just testing
engine = chess.engine.SimpleEngine.popen_uci(
    r"/home/chadi/projects/tsyp/stockfish/src/stockfish"
)
board = Board()
print(board)
# this is stockfish say hello
stockfish = Stockfish(path=r"/home/chadi/projects/tsyp/stockfish/src/stockfish")
stockfish.set_skill_level(10)


def posiblemove(name, board):
    l = []
    for move in moves:
        h = str(move)
        if (name in h) and (h.index(name) == 0):
            l.append(h[len(name) : len(name) + 2])
    return l


def find_move(fen1, fen2):
    """
    Takes two FEN strings and returns the move that transitions from the first
    FEN to the second, along with its legality.
    """
    board = chess.Board(fen1)  # Create a board from the first FEN
    next_board = chess.Board(fen2)  # Create a board from the second FEN

    for move in board.legal_moves:
        # Apply each legal move to a copy of the board
        temp_board = board.copy()
        temp_board.push(move)

        # Check if applying the move matches the second FEN
        if temp_board.fen().split(" ")[0] == next_board.fen().split(" ")[0]:
            return move, True

    # If no legal move matches the second FEN, return None and False
    return None, False


def find_illegal_move(fen1, fen2):
    """
    Takes two FEN strings and returns the move that transitions from the first
    FEN to the second, whether it's legal or illegal.
    """
    board = chess.Board(fen1)  # Create a board from the first FEN
    next_board = chess.Board(fen2)  # Create a board from the second FEN

    # Iterate over all possible moves (legal or not) from the first board
    for move in chess.SQUARES:
        for target in chess.SQUARES:
            move_obj = chess.Move(move, target)

            # Check if the move is valid for the pieces' movement rules
            if board.is_pseudo_legal(move_obj):
                temp_board = board.copy()
                temp_board.push(move_obj)
                # Compare the FENs
                if temp_board.fen().split(" ")[0] == next_board.fen().split(" ")[0]:
                    return move_obj


image = "pic.jpg"


def takepic(output_path="captured_image.jpg", camera_index=0):
    """
    Captures a picture from the specified camera and saves it.

    Parameters:
        output_path (str): The path where the captured image will be saved.
        camera_index (int): The index of the camera to use (0 for default).

    Returns:
        str: The path of the saved image if successful, None otherwise.
    """
    # Open the camera
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return None

    # Capture a single frame
    ret, frame = camera.read()

    if ret:
        # Save the captured frame
        cv2.imwrite(output_path, frame)
        print(f"Image saved as {output_path}")
        result = output_path
    else:
        print("Error: Could not capture an image.")
        result = None

    # Release the camera
    camera.release()

    return result


chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"you Ask the user if he want to play black or white.",
        }
    ],
    model="llama3-70b-8192",
)
res = chat_completion.choices[0].message.content
print(res)
t1 = gtts.gTTS(res)
t1.save("welcome.mp3")
song = AudioSegment.from_mp3("welcome.mp3")
play(song)
if os.path.isfile(question_path):
    q = model.transcribe("question.mp3")
    q = q.lower()
    if "lua" in q:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"asnwer only with :'black' or 'white' using this answer {q}. witch colore the user want to play ?",
                }
            ],
            model="llama3-70b-8192",
        )
        ans = chat_completion.choices[0].message.content
if ans.lower() == "white":
    playercolore = 0
else:
    playercolore = 1


question_path = os.path.join(directory, file_name)
fen = board.fen()

allmoves = []
round = 1
while not board.is_game_over():
    if os.path.isfile(question_path):
        q = model.transcribe("question.mp3")
        q = q.lower()
        if "lua" in q:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"asnwer only with yes or no . is this quesion about chess : '{q}' ?",
                    }
                ],
                model="llama3-70b-8192",
            )
            ans = chat_completion.choices[0].message.content
            if ans.lower() == "yes":
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": f"anser this question in a paragraph of less then 100 word in a clear answer about chess : {q}",
                        }
                    ],
                    model="llama3-70b-8192",
                )
            res = chat_completion.choices[0].message.content
            print(res)
            t1 = gtts.gTTS(res)
            t1.save("welcome.mp3")
            song = AudioSegment.from_mp3("welcome.mp3")
            play(song)
        else:
            res = "i'm sorry ,I answer only  chess related question"
            t1 = gtts.gTTS(res)
            t1.save("welcome.mp3")
            song = AudioSegment.from_mp3("welcome.mp3")
            play(song)
            print(res)
        os.remove(question_path)

    ev1 = stockfish.get_evaluation()
    if round % 2 == playercolore:
        takepic(image)
        command = ["python3", "chess_cv.py", "pic.jpg"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        fen2 = result.stdout
        move, legal = find_move(fen, fen2)
        while not legal:
            move = str(find_illegal_move(fen, fen2))
            # this is for the led
            l = posiblemove(move[:2], board)
            command = ["sudo", "screen", "/dev/ttyACM0", "9600"]
            subprocess.run(command)
            command = ["echo", l, ">", "/dev/ttyACM0"]
            subprocess.run(command)

            content = f"this is the fen of the game {fen}, explain why this move is ilalegal and explain how that peace move acourding to chess rules in short pargraph"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(res)
            t1 = gtts.gTTS(res)
            t1.save("welcome.mp3")
            song = AudioSegment.from_mp3("welcome.mp3")
            play(song)
            takepic(image)
            command = ["python3", "chess_cv.py", "pic.jpg"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            fen2 = result.stdout
            move, legal = find_move(fen, fen2)
    else:
        best_move = stockfish.get_best_move_time(1000)
        move = chess.Move.from_uci(best_move)
        command = ["python3", "armcode.py", "pic.jpg"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    allmoves.append(move)
    board.push(move)
    fen = board.fen()
    stockfish.set_fen_position(fen)
    ev2 = stockfish.get_evaluation()
    print(ev1)
    print(ev2)
    print(move)
    res = ""
    if round % 2 == playercolore:
        if (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev2["value"] - ev1["value"] > 50
            and ev1["value"] >= 0
            and ev2["value"] >= 0
        ):
            mev = "verry good"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)
        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev2["value"] - ev1["value"] >= 0
            and ev1["value"] >= 0
            and ev2["value"] >= 0
        ):
            mev = "good"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)
        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev2["value"] - ev1["value"] < 50
            and ev1["value"] >= 0
            and ev2["value"] >= 0
        ):
            mev = "bad but you still wining"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] >= 0
            and ev2["value"] <= 0
            and abs(abs(ev1["value"]) - ev2["value"]) <= 50
        ):
            mev = "bad you did lose your winging postion"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] >= 0
            and ev2["value"] <= 0
            and abs(abs(ev1["value"]) - ev2["value"]) >= 50
        ):
            mev = "very bad"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif ev1["type"] == "cp" and ev2["type"] == "mate" and ev2["value"] >= 0:
            mev = "good you have mate"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif ev1["type"] == "cp" and ev2["type"] == "mate" and ev2["value"] <= 0:
            mev = "you are losing with mate "
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "mate"
            and ev2["type"] == "cp"
            and ev2["value"] > 0
            and ev1["value"] > 0
        ):
            mev = "you did miss your mate but you still wining"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "mate"
            and ev2["type"] == "cp"
            and ev1["value"] < 0
            and (ev2["value"] > 0 or ev2["value"] < 0)
        ):
            mev = "good you escape mate"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "mate"
            and ev2["type"] == "mate"
            and ev1["value"] >= 0
            and ev2["value"] >= 0
        ):
            mev = "winging position"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)
        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and abs(ev2["value"]) - abs(ev1["value"]) >= 0
            and ev1["value"] <= 0
            and ev2["value"] <= 0
        ):
            mev = "verry bad"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)
        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and abs(ev2["value"]) - abs(ev1["value"]) <= 0
            and ev1["value"] <= 0
            and ev2["value"] <= 0
        ):
            mev = "good but you are in losing postion"
            if round == 7:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that White is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for white make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)
        else:
            print("explain this")
    else:
        if (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and abs(ev1["value"] - ev2["value"]) > 50
            and ev1["value"] <= 0
            and ev2["value"] <= 0
        ):
            mev = "verry good"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for Black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev2["value"] - ev1["value"] <= 0
            and ev1["value"] <= 0
            and ev2["value"] <= 0
        ):
            mev = "good"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for Black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev2["value"] - ev1["value"] >= 0
            and ev1["value"] <= 0
            and ev2["value"] <= 0
        ):
            mev = "bad but you still wining"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for Black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] <= 0
            and ev2["value"] >= 0
            and ev2["value"] - ev1["value"] >= 0
        ):
            mev = "bad you did lose your winging postion"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for Black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] <= 0
            and ev2["value"] >= 0
            and ev2["value"] - ev1["value"] >= 50
        ):
            mev = "very bad"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for Black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif ev1["type"] == "cp" and ev2["type"] == "mate" and ev2["value"] <= 0:
            mev = "good you have mate"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for Black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif ev1["type"] == "cp" and ev2["type"] == "mate" and ev2["value"] >= 0:
            mev = "you are losing with mate "
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that Black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "mate"
            and ev2["type"] == "cp"
            and ev2["value"] < 0
            and ev1["value"] < 0
        ):
            mev = "you did miss your mate but you still wining"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "mate"
            and ev2["type"] == "cp"
            and ev1["value"] > 0
            and (ev2["value"] < 0 or ev2["value"] > 0)
        ):
            mev = "good you escape mate"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] >= 0
            and ev2["value"] >= 0
            and ev2["value"] - ev1["value"] >= 0
        ):
            mev = "bad"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] >= 0
            and ev2["value"] >= 0
            and ev2["value"] - ev1["value"] <= 0
        ):
            mev = "good"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)
        elif (
            ev1["type"] == "cp"
            and ev2["type"] == "cp"
            and ev1["value"] >= 0
            and ev2["value"] <= 0
            and ev2["value"] - ev1["value"] <= 0
        ):
            mev = "very good"
            if round == 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        elif (
            ev1["type"] == "mate"
            and ev2["type"] == "mate"
            and ev1["value"] < 0
            and ev2["value"] < 0
        ):
            mev = "winging position"
            if round <= 12:
                content = f"This is the FEN of the game: '{fen}'. Briefly explain the opening that black is playing in short pargraph."
            else:
                content = f"this is the FEN OF THE GAME :'{fen}' explain why {move} was a {mev} move  for black make it in one pargraph simple and short but at the point "

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
            res = chat_completion.choices[0].message.content
            print(mev)
            print(res)

        else:
            print("explain this")
    t1 = gtts.gTTS(res)
    t1.save("welcome.mp3")
    song = AudioSegment.from_mp3("welcome.mp3")
    play(song)

    round += 1
    print(board)
    print("\n")

if board.result() == "1-0":
    games = "White win"
    print("White win ")
elif board.result() == "0-1":
    games = "Black win"
    print("Black win")
else:
    games = "Drow"
    print("Drow")
content = f"this how the game did end white the state {games} and here is the all the move in that have been played in this game{allmoves} explain in short pargraph this game and how did it led to {games}."
chat_completion = client.chat.completions.create(
    messages=[{"role": "user", "content": content}],
    model="llama3-70b-8192",
)
res = chat_completion.choices[0].message.content
t1 = gtts.gTTS(res)
t1.save("welcome.mp3")
song = AudioSegment.from_mp3("welcome.mp3")
play(song)
