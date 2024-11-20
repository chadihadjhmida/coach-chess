import gtts
from pydub import AudioSegment
from pydub.playback import play
import os
from groq import Groq
import whisper
import subprocess


# Load the tiny English model
model = whisper.load_model("tiny.en")

# the directury where the qestion.mp3 will be there
directory = "path/to/your/folder"

# Specify the file name
file_name = "question.mp3"

question_path = os.path.join(directory, file_name)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"you Ask the user which level they want to play: Easy, Medium, or Hard.",
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
                    "content": f"asnwer only with :'hard','easy'or'midum' using this answer {q}. witch defficulity the user want to play ?",
                }
            ],
            model="llama3-70b-8192",
        )
        ans = chat_completion.choices[0].message.content

if ans.lower() == "hard":
    command = ["python3", "engine3.py"]
    subprocess.run(command)
elif ans.lower() == "midum":
    command = ["python3", "engine2.py"]
    subprocess.run(command)
else:
    command = ["python3", "engine1.py"]
    subprocess.run(command)
