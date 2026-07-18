import unittest
from pieces import Piece
from position import Position
from movement_strategy import MovementException, OffBoardException, KingMovement

def create_king(has_moved = False):
    return Piece(KingMovement(), has_moved=has_moved)

class TestKing(unittest.TestCase):
    def test_move_off_board1(self):
        p = create_king()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=1, y_pos=1)
            target_pos = Position(x_pos=-1, y_pos=1)
            p.validate_move(current_pos, target_pos)
    
    def test_move_off_board2(self):
        p = create_king()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=8, y_pos=1)
            target_pos = Position(x_pos=8, y_pos=9)
            p.validate_move(current_pos, target_pos)
    
    def test_invalid_movement_none(self):
        p = create_king()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=4)
            target_pos = Position(x_pos=6, y_pos=4)
            p.validate_move(current_pos, target_pos)

    def test_valid_movement_forward(self):
        p = create_king()
        current_pos = Position(x_pos=1, y_pos=3)
        target_pos = Position(x_pos=1, y_pos=4)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_valid_movement_backwards(self):
        p = create_king()
        current_pos = Position(x_pos=5, y_pos=4)
        target_pos = Position(x_pos=5, y_pos=3)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_valid_movement_sideways(self):
        p = create_king()
        current_pos = Position(x_pos=5, y_pos=4)
        target_pos = Position(x_pos=6, y_pos=4)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))

    def test_valid_movement_diagonal(self):
        p = create_king()
        current_pos = Position(x_pos=5, y_pos=4)
        target_pos = Position(x_pos=4, y_pos=5)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
