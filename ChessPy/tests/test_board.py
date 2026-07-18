import unittest

from board import Board
from pieces import Piece
from position import Position
from movement_strategy import MovementException, KnightMovement, PawnMovement, RookMovement


class TestBoard(unittest.TestCase):
    def test_board_has_64_squares(self):
        board = Board()
        self.assertEqual(len(board.squares), 64)

    def test_place_piece(self):
        board = Board()
        piece = Piece(KnightMovement())
        pos = Position(2, 1)

        board.place_piece(piece, pos)

        self.assertIs(board.get_piece_at(pos), piece)

    def test_print_empty_board(self):
        board = Board()
        expected = "\n".join([
            "  A B C D E F G H",
            "8 . . . . . . . .",
            "7 . . . . . . . .",
            "6 . . . . . . . .",
            "5 . . . . . . . .",
            "4 . . . . . . . .",
            "3 . . . . . . . .",
            "2 . . . . . . . .",
            "1 . . . . . . . .",
        ])

        self.assertEqual(str(board), expected)

    def test_print_board_with_pieces(self):
        board = Board()
        board.place_piece(Piece(RookMovement()), Position(1, 1))
        board.place_piece(Piece(KnightMovement()), Position(2, 1))
        board.place_piece(Piece(PawnMovement()), Position(3, 2))

        expected = "\n".join([
            "  A B C D E F G H",
            "8 . . . . . . . .",
            "7 . . . . . . . .",
            "6 . . . . . . . .",
            "5 . . . . . . . .",
            "4 . . . . . . . .",
            "3 . . . . . . . .",
            "2 . . P . . . . .",
            "1 R N . . . . . .",
        ])

        self.assertEqual(str(board), expected)

    def test_move_piece_updates_board_positions(self):
        board = Board()
        piece = Piece(KnightMovement())
        current_pos = Position(2, 1)
        target = Position(3, 3)
        board.place_piece(piece, current_pos)

        board.move_piece(current_pos, target)

        self.assertIsNone(board.get_piece_at(current_pos))
        self.assertIs(board.get_piece_at(target), piece)
        self.assertTrue(piece.has_moved)

    def test_move_piece_requires_piece_at_current_position(self):
        board = Board()

        with self.assertRaises(MovementException):
            board.move_piece(Position(2, 1), Position(3, 3))

    def test_knight_movement_is_not_blocked(self):
        board = Board()
        knight = Piece(KnightMovement())
        current_pos = Position(2, 1)
        board.place_piece(knight, current_pos)

        blocking_pawn = Piece(PawnMovement())
        pawn_pos = Position(2, 2)
        board.place_piece(blocking_pawn, pawn_pos)

        target_pos = Position(3, 3)
        board.move_piece(current_pos, Position(3, 3))

        self.assertIsNone(board.get_piece_at(current_pos))
        self.assertIs(board.get_piece_at(target_pos), knight)
        self.assertTrue(knight.has_moved)
        self.assertIs(board.get_piece_at(pawn_pos), blocking_pawn)
        self.assertFalse(blocking_pawn.has_moved)

    def test_move_piece_captures_occupied_target(self):
        board = Board()
        current_pos = Position(2, 1)
        target_pos = Position(3, 3)
        knight = Piece(KnightMovement())
        board.place_piece(knight, current_pos)
        board.place_piece(Piece(PawnMovement()), target_pos)

        board.move_piece(current_pos, target_pos)
        
        self.assertIsNone(board.get_piece_at(current_pos))
        self.assertIs(board.get_piece_at(target_pos), knight)
        self.assertTrue(knight.has_moved)

    def test_pawn_capture(self):
        board = Board()
        current_pos = Position(3, 3)
        target_pos = Position(4, 4)

        pawn = Piece(PawnMovement())
        knight = Piece(KnightMovement())

        board.place_piece(pawn, current_pos)
        board.place_piece(knight, target_pos)

        board.move_piece(current_pos, target_pos)

        self.assertIsNone(board.get_piece_at(current_pos))
        self.assertIs(board.get_piece_at(target_pos), pawn)
        self.assertIsNot(board.get_piece_at(target_pos), knight)
        self.assertTrue(pawn.has_moved)

    def test_black_pawn_capture(self):
        board = Board()
        current_pos = Position(3, 6)
        target_pos = Position(4, 5)

        pawn = Piece(PawnMovement(), color="black")
        knight = Piece(KnightMovement(), color="white")

        board.place_piece(pawn, current_pos)
        board.place_piece(knight, target_pos)

        board.move_piece(current_pos, target_pos)

        self.assertIsNone(board.get_piece_at(current_pos))
        self.assertIs(board.get_piece_at(target_pos), pawn)
        self.assertIsNot(board.get_piece_at(target_pos), knight)
        self.assertTrue(pawn.has_moved)

    def test_pawn_cannot_capture_empty_diagonal_square(self):
        board = Board()
        current_pos = Position(3, 3)
        target_pos = Position(4, 4)
        board.place_piece(Piece(PawnMovement()), current_pos)

        with self.assertRaises(MovementException):
            board.move_piece(current_pos, target_pos)

    def test_pawn_cannot_move_forward_into_occupied_square(self):
        board = Board()
        current_pos = Position(3, 3)
        target_pos = Position(3, 4)
        board.place_piece(Piece(PawnMovement()), current_pos)
        board.place_piece(Piece(KnightMovement()), target_pos)

        with self.assertRaises(MovementException):
            board.move_piece(current_pos, target_pos)

    def test_move_piece_rejects_blocked_path(self):
        board = Board()
        current_pos = Position(1, 1)
        target = Position(1, 4)
        board.place_piece(Piece(RookMovement()), current_pos)
        board.place_piece(Piece(PawnMovement()), Position(1, 2))

        with self.assertRaises(MovementException):
            board.move_piece(current_pos, target)


if __name__ == "__main__":
    unittest.main()
