import unittest
from pieces import Piece
from position import Position
from movement_strategy import MovementException, OffBoardException, RookMovement

def create_rook(has_moved = False):
    return Piece(RookMovement(), has_moved=has_moved)

class TestRook(unittest.TestCase):
    def test_move_off_board1(self):
        p = create_rook()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=1, y_pos=1)
            target_pos = Position(x_pos=-1, y_pos=1)
            p.validate_move(current_pos, target_pos)
    
    def test_move_off_board2(self):
        p = create_rook()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=8, y_pos=1)
            target_pos = Position(x_pos=8, y_pos=9)
            p.validate_move(current_pos, target_pos)

    def test_invalid_move_both_axis(self):
        p = create_rook()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=3, y_pos=4)
            target_pos = Position(x_pos=4, y_pos=5)
            p.validate_move(current_pos, target_pos)
    
    def test_invalid_movement_none(self):
        p = create_rook()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=4)
            target_pos = Position(x_pos=6, y_pos=4)
            p.validate_move(current_pos, target_pos)
    
    def test_valid_move_y(self):
        p = create_rook()
        current_pos = Position(x_pos=3, y_pos=4)
        target_pos = Position(x_pos=3, y_pos=8)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_valid_move_x(self):
        p = create_rook()
        current_pos = Position(x_pos=3, y_pos=4)
        target_pos = Position(x_pos=7, y_pos=4)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
