"""
File for the board class - holds position of all pieces
"""
from typing import Optional

from position import Position
from pieces import Piece
from movement_strategy import (
    MovementException,
    PawnMovement,
    RookMovement,
    KnightMovement,
    BishopMovement,
    QueenMovement,
    KingMovement
)

class Square:
    def __init__(self, pos: Position, piece: Piece = None):
        self.pos = pos
        self.piece = piece


class Board:
    def __init__(self):
        self.squares = {
            Position(x, y): Square(Position(x,y))
            for x in range(1, 9)
            for y in range(1, 9)
        }

    def get_piece_at(self, pos: Position) -> Optional[Piece]:
        return self.squares[pos].piece
    
    def get_piece_color_at(self, pos: Position) -> Optional[str]:
        return self.squares[pos].piece.color

    def is_empty(self, pos: Position) -> bool:
        return self.get_piece_at(pos) is None

    def place_piece(self, piece: Piece, pos: Position) -> None:
        self.squares[pos].piece = piece

    def move_piece(self, current_pos: Position, target: Position) -> None:
        piece = self.get_piece_at(current_pos)
        if piece is None:
            raise MovementException("No piece at current position")

        piece.validate_move(current_pos, target)
        if not self.is_path_clear(current_pos, target):
            raise MovementException("Path is blocked")
        self.validate_target_for_piece(piece, current_pos, target)

        self.squares[target].piece = piece
        self.squares[current_pos].piece = None
        piece.mark_moved()

    def validate_target_for_piece(self, piece: Piece, current_pos: Position, target: Position) -> None:
        if isinstance(piece.mb, PawnMovement):
            x_diff = target.x_pos - current_pos.x_pos
            if x_diff == 0 and not self.is_empty(target):
                raise MovementException("Pawn cannot move forward into an occupied square")
            if x_diff != 0 and self.is_empty(target):
                raise MovementException("Pawn cannot move diagonally without capturing")
    
    def path_between(self, current_pos: Position, target: Position) -> list[Position]:
        x_diff = target.x_pos - current_pos.x_pos
        y_diff = target.y_pos - current_pos.y_pos

        if abs(x_diff) <= 1 and abs(y_diff) <= 1:
            return []
        if x_diff != 0 and y_diff != 0 and abs(x_diff) != abs(y_diff):
            return []

        x_step = 0 if x_diff == 0 else x_diff // abs(x_diff)
        y_step = 0 if y_diff == 0 else y_diff // abs(y_diff)

        positions = []
        next_pos = Position(current_pos.x_pos + x_step, current_pos.y_pos + y_step)
        while next_pos != target:
            positions.append(next_pos)
            next_pos = Position(next_pos.x_pos + x_step, next_pos.y_pos + y_step)
        return positions

    def is_path_clear(self, current_pos: Position, target: Position) -> bool:
        return all(self.is_empty(pos) for pos in self.path_between(current_pos, target))
    
    def setup_game(self) -> None:
        self.setup_pawns()
        self.setup_rooks()
        self.setup_knights()
        self.setup_bishops()
        self.setup_queens()
        self.setup_kings()

    def setup_pawns(self) -> None:
        # Set white pawns
        for x in range(1, 9):
            self.place_piece(Piece(PawnMovement(), "white"), Position(x, 2))
        
        # Set black pawns
        for x in range(1, 9):
            self.place_piece(Piece(PawnMovement(), "black"), Position(x, 7))

    def setup_rooks(self) -> None:
        self.place_piece(Piece(RookMovement(), "white"), Position(1, 1))
        self.place_piece(Piece(RookMovement(), "white"), Position(8, 1))
        self.place_piece(Piece(RookMovement(), "black"), Position(1, 8))
        self.place_piece(Piece(RookMovement(), "black"), Position(8, 8))
    
    def setup_knights(self) -> None:
        self.place_piece(Piece(KnightMovement(), "white"), Position(2, 1))
        self.place_piece(Piece(KnightMovement(), "white"), Position(7, 1))
        self.place_piece(Piece(KnightMovement(), "black"), Position(2, 8))
        self.place_piece(Piece(KnightMovement(), "black"), Position(7, 8))

    def setup_bishops(self) -> None:
        self.place_piece(Piece(BishopMovement(), "white"), Position(3, 1))
        self.place_piece(Piece(BishopMovement(), "white"), Position(6, 1))
        self.place_piece(Piece(BishopMovement(), "black"), Position(3, 8))
        self.place_piece(Piece(BishopMovement(), "black"), Position(6, 8))
    
    def setup_queens(self) -> None:
        self.place_piece(Piece(QueenMovement(), "white"), Position(4, 1))
        self.place_piece(Piece(QueenMovement(), "black"), Position(4, 8))
    
    def setup_kings(self) -> None:
        self.place_piece(Piece(KingMovement(), "white"), Position(5, 1))
        self.place_piece(Piece(KingMovement(), "black"), Position(5, 8))

    def piece_symbol(self, piece: Optional[Piece]) -> str:
        if piece is None:
            return "."

        symbols = {
            PawnMovement: "P",
            RookMovement: "R",
            KnightMovement: "N",
            BishopMovement: "B",
            QueenMovement: "Q",
            KingMovement: "K",
        }
        return symbols[type(piece.mb)]

    def __str__(self):
        """Prints the board to the terminal"""
        rows = ["  A B C D E F G H"]
        for y in range(8, 0, -1):
            row = [str(y)]
            for x in range(1, 9):
                piece = self.get_piece_at(Position(x, y))
                row.append(self.piece_symbol(piece))
            rows.append(" ".join(row))
        return "\n".join(rows)
