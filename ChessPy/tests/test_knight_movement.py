import unittest
from pieces import Piece
from position import Position
from movement_strategy import MovementException, OffBoardException, KnightMovement

def create_knight(has_moved = False):
    return Piece(KnightMovement(), has_moved=has_moved)

class TestKnight(unittest.TestCase):
    def test_move_off_board1(self):
        p = create_knight()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=2, y_pos=1)
            target_pos = Position(x_pos=-1, y_pos=-1)
            p.validate_move(current_pos, target_pos)
    
    def test_move_off_board2(self):
        p = create_knight()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=8, y_pos=1)
            target_pos = Position(x_pos=9, y_pos=3)
            p.validate_move(current_pos, target_pos)

    def test_invalid_movement1(self):
        p = create_knight()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=2, y_pos=1)
            target_pos = Position(x_pos=5, y_pos=8)
            p.validate_move(current_pos, target_pos)
    
    def test_invalid_movement2(self):
        p = create_knight()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=3, y_pos=6)
            target_pos = Position(x_pos=2, y_pos=5)
            p.validate_move(current_pos, target_pos)
    
    def test_invalid_movement3(self):
        p = create_knight()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=4)
            target_pos = Position(x_pos=4, y_pos=4)
            p.validate_move(current_pos, target_pos)
    
    def test_invalid_movement_none(self):
        p = create_knight()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=4)
            target_pos = Position(x_pos=6, y_pos=4)
            p.validate_move(current_pos, target_pos)

    def test_valid_move1(self):
        p = create_knight()
        current_pos = Position(x_pos=2, y_pos=1)
        target_pos = Position(x_pos=3, y_pos=3)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_valid_move2(self):
        p = create_knight()
        current_pos = Position(x_pos=7, y_pos=1)
        target_pos = Position(x_pos=6, y_pos=3)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_valid_move3(self):
        p = create_knight()
        current_pos = Position(x_pos=6, y_pos=3)
        target_pos = Position(x_pos=4, y_pos=4)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
