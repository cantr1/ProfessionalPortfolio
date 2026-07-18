"""
Main file for gameplay loop
"""
from movement_strategy import MovementException
from position import Position
from board import Board
from enum import Enum
import subprocess


class AlphaPosition(Enum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5
    F = 6
    G = 7
    H = 8

def clear_screen() -> None:
    try:
        subprocess.run(["clear"], check=True)
    except subprocess.CalledProcessError:
        print("Error clearing the screen")

def convert_user_input_to_position(user_input: str) -> Position:
    x_pos: int = AlphaPosition[user_input[0]].value
    y_pos: int = int(user_input[1])
    return Position(x_pos, y_pos)

def main() -> None:
    board = Board()
    board.setup_game()
    print("Welcome to Chess\n")
    
    game_on = True
    current_player_turn = "white"
    while game_on:
        try:
            print(board)

            # Parse user input into position changes TODO: validatate / sanitize inputs
            user_input: str = input(f"{current_player_turn.title()} to Move\nChoose your move in the following format: B1 C3\n").upper()
            split_input: str = user_input.split(" ")
            starting_pos: Position = convert_user_input_to_position(split_input[0])
            target_pos: Position = convert_user_input_to_position(split_input[1])

            #DEBUG
            #print(f"Attempting to move {starting_pos} -> {target_pos}")

            # Check that attempted piece movement matches current users turn
            piece_color: str = board.get_piece_color_at(starting_pos)
            if piece_color != current_player_turn:
                raise MovementException("Invalid move - Cannot move other players pieces")

            board.move_piece(starting_pos, target_pos)

            clear_screen()

            if current_player_turn == "white":
                current_player_turn = "black"
            else:
                current_player_turn = "white"
        except MovementException as e:
            print(f"{e}")
        
        


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")