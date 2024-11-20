# Magician
import time  # For delays
import argparse

# Function to control the gripper
import time  # For delays


# Function to control the gripper
def control_gripper(api, state, i):
    """
    Control the gripper state.

    :param api: The API object for the robotic arm.
    :param state: 1 to close the gripper, 0 to open it.
    :param i: The mode or parameter for the gripper control (specific to the SDK).
    """
    # Log action based on the state
    print("Closing gripper" if state else "Opening gripper")

    # Activate the gripper action
    dType.SetEndEffectorGripper(
        api, state, i
    )  # Enable or disable gripper based on state

    # Add delay to ensure the gripper completes its action
    time.sleep(0.3)

    # Reset the gripper state (optional, depending on the SDK and requirements)
    dType.SetEndEffectorGripper(api, 0, i)


# Function to move the robotic arm only in the Z direction
def move_z(api, z_target, x, y, rHead):
    print("Moving to Z: {z_target}")
    dType.SetPTPCmd(
        api, 2, x, y, z_target, rHead, 1
    )  # PTP mode 2: Cartesian coordinate move
    time.sleep(1)  # Allow time for the movement to complete


# Function to move the robotic arm to a specified position
def move_to_position(api, x, y, z, rHead):
    print("Moving to position X: {x}, Y: {y}, Z: {z}")
    dType.SetPTPCmd(api, 2, x, y, z, rHead, 1)
    time.sleep(2)  # Allow time for the movement to complete


# Function to pick and place a chess piece
def pick_and_place(api, start_case, end_case, chessboard):
    """
    Perform a pick-and-place operation for a chess piece.
    :param api: The API object for the robotic arm.
    :param start_case: Chessboard start position (e.g., "A2").
    :param end_case: Chessboard end position (e.g., "A4").
    :param chessboard: Dictionary mapping chessboard positions to coordinates.
    """
    start_coords = chessboard[start_case]
    end_coords = chessboard[end_case]

    # Move above the starting position
    move_to_position(api, start_coords[0], start_coords[1], 70, start_coords[3])

    # Open the gripper to release the piece
    control_gripper(api, 1, 0)

    # Move down to pick the piece
    move_z(api, 18, start_coords[0], start_coords[1], start_coords[3])

    # Close the gripper to pick the piece
    control_gripper(api, 1, 1)

    # Move back up
    move_z(api, 70, start_coords[0], start_coords[1], start_coords[3])

    # Move above the target position
    move_to_position(api, end_coords[0], end_coords[1], 70, end_coords[3])

    # Move down to place the piece
    move_z(api, 18, end_coords[0], end_coords[1], end_coords[3])

    # Open the gripper to release the piece
    control_gripper(api, 1, 0)

    # Move back up
    move_z(api, 70, end_coords[0], end_coords[1], end_coords[3])


# Chessboard coordinates dictionary
chessboard = {
    "A1": [323.85, -39.1, 70.0, 0.0],
    "A2": [300.5, -39.8, 70.0, 0.0],
    "A3": [273.75, -50.65, 70.0, 0.0],
    "A4": [247.5, -54.35, 70.0, 0.0],
    "A5": [220.0, -58.82, 70.0, 0.0],
    "A6": [195, -64.3, 70.0, 0.0],
    "A7": [167.7, -72.75, 70.0, 0.0],
    "A8": [139.0, -80.15, 70.0, 0.0],
    "B1": [320.0, -5.2, 70.0, 0.0],
    "B2": [295.0, -15.7, 70.0, 0.0],
    "B3": [270.15, -22.25, 70.0, 0.0],
    "B4": [244.7, -28.16, 70.0, 0.0],
    "B5": [255.7665, -74.3979, 70.0, 0.0],
    "B6": [190.0, -40.25, 70.0, 0.0],
    "B7": [164.4, -43.67, 70.0, 0.0],
    "B8": [139.65, -54.6, 70.0, 0.0],
    "C1": [316.5, -18.0, 70.0, 0.0],
    "C2": [292.0, 13.25, 70.0, 0.0],
    "C3": [265.0, 5.15, 70.0, 0.0],
    "C4": [240.0, -1.25, 70.0, 0.0],
    "C5": [213.75, -3.65, 70.0, 0.0],
    "C6": [187.2, -10.65, 70.0, 0.0],
    "C7": [158.5, -13.2, 70.0, 0.0],
    "C8": [137.35, -22.9, 70.0, 0.0],
    "D1": [157.0, -110.0, 70.0, 0.0],
    "D2": [164.0, -107.0, 70.0, 0.0],
    "D3": [171.0, -104.0, 70.0, 0.0],
    "D4": [178.0, -101.0, 70.0, 0.0],
    "D5": [261.2073, -17.3252, 70.0, 0.0],
    "D6": [234.1602, -14.9493, 70.0, 0.0],
    "D7": [206.9872, -11.9730, 70.0, 0.0],
    "D8": [206.0, -89.0, 70.0, 0.0],
    "E1": [157.0, -110.0, 70.0, 0.0],
    "E2": [283.4, -72.1, 70.0, 0.0],
    "E3": [171.0, -104.0, 70.0, 0.0],
    "E4": [292.6446, 7.8751, 70.0, 0.0],
    "E5": [205.8, 54.9, 70.0, 0.0],
    "E6": [237.8207, 14.3306, 70.0, 0.0],
    "E7": [210.0422, 16.3227, 70.0, 0.0],
    "E8": [206.0, -89.0, 70.0, 0.0],
    "F1": [157.0, -110.0, 70.0, 0.0],
    "F2": [164.0, -107.0, 70.0, 0.0],
    "F3": [318.6513, 34.3015, 70.0, 0.0],
    "F4": [178.0, -101.0, 70.0, 0.0],
    "F5": [202.0, 83.56, 70.0, 0.0],
    "F6": [241.1599, 40.0348, 70.0, 0.0],
    "F7": [213.6793, 47.8857, 70.0, 0.0],
    "F8": [186.5928, 51.0026, 70.0, 0.0],
    "G1": [157.0, -110.0, 70.0, 0.0],
    "G2": [164.0, -107.0, 70.0, 0.0],
    "G3": [171.0, -104.0, 70.0, 0.0],
    "G4": [178.0, -101.0, 70.0, 0.0],
    "G5": [185.0, -98.0, 70.0, 0.0],
    "G6": [192.0, -95.0, 70.0, 0.0],
    "G7": [199.0, -92.0, 70.0, 0.0],
    "G8": [189.0955, 79.7544, 70.0, 0.0],
    "H1": [157.0, -110.0, 70.0, 0.0],
    "H2": [164.0, -107.0, 70.0, 0.0],
    "H3": [171.0, -104.0, 70.0, 0.0],
    "H4": [178.0, -101.0, 70.0, 0.0],
    "H5": [272.9025, 95.8607, 70.0, 0.0],
    "H6": [192.0, -95.0, 70.0, 0.0],
    "H7": [219.1617, 103.1308, 70.0, 0.0],
    "H8": [206.0, -89.0, 70.0, 0.0],
    "out": [257.1534, -155.8773, 70.0, 0.0],
    "out2": [255.7702, 136.4424, 70.0, 0.0],
    "rest": [192.1275, -7.7733, 1011042, 0.0],
}


# Set movement parameters
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, 0)
dType.SetPTPCoordinateParams(api, 200, 200, 200, 200, 0)
dType.SetPTPJumpParams(api, 10, 200, 0)
dType.SetPTPCommonParams(api, 100, 100, 0)


pick_and_place(api, "G8", "F6", chessboard)
if args.command == "move":
    pick_and_place(api, args.x, args.y, chessboard)

# Example usage
# Initialize the robotic arm API (replace with actual initialization)
# api = dType.ConnectDevice()

# 1 Move a piece from A2 to A4
