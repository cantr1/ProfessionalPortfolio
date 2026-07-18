import unittest
from pieces import Piece
from position import Position
from movement_strategy import PawnMovement, OffBoardException, MovementException

def create_pawn(has_moved = False):
    return Piece(PawnMovement(), has_moved=has_moved)

class TestPawn(unittest.TestCase):
    def test_move_off_board1(self):
        p = create_pawn()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=6, y_pos=8)
            target_pos = Position(x_pos=6, y_pos=9)
            p.validate_move(current_pos, target_pos)
    
    def test_move_off_board2(self):
        p = create_pawn()
        with self.assertRaises(OffBoardException):
            current_pos = Position(x_pos=1, y_pos=1)
            target_pos = Position(x_pos=1, y_pos=0)
            p.validate_move(current_pos, target_pos)

    def test_invalid_movement_large_forward(self):
        p = create_pawn()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=1, y_pos=2)
            target_pos = Position(x_pos=1, y_pos=8)
            p.validate_move(current_pos, target_pos)
    
    def test_invalid_movement_backwards(self):
        p = create_pawn()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=3, y_pos=6)
            target_pos = Position(x_pos=3, y_pos=5)
            p.validate_move(current_pos, target_pos)

    def test_valid_movement_backwards_black_pawn(self):
        p = Piece(PawnMovement(), color="black")
        current_pos = Position(x_pos=4, y_pos=7)
        target_pos = Position(x_pos=4, y_pos=6)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))

    def test_valid_movement_backwards_black_pawn2(self):
        p = Piece(PawnMovement(), color="black")
        current_pos = Position(x_pos=4, y_pos=7)
        target_pos = Position(x_pos=4, y_pos=5)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
        
    def test_valid_movement_diagonal_capture_black_pawn(self):
        p = Piece(PawnMovement(), color="black")
        current_pos = Position(x_pos=4, y_pos=6)
        target_pos = Position(x_pos=5, y_pos=5)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_invalid_movement_none(self):
        p = create_pawn()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=2)
            target_pos = Position(x_pos=6, y_pos=2)
            p.validate_move(current_pos, target_pos)
    
    def test_valid_movement_diagonal_capture_shape(self):
        p = create_pawn()
        current_pos = Position(x_pos=4, y_pos=6)
        target_pos = Position(x_pos=5, y_pos=7)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_invalid_movement_sideways(self):
        p = create_pawn()
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=8)
            target_pos = Position(x_pos=5, y_pos=8)
            p.validate_move(current_pos, target_pos)

    def test_invalid_movement_forward2(self):
        p = create_pawn(has_moved=True)
        with self.assertRaises(MovementException):
            current_pos = Position(x_pos=6, y_pos=3)
            target_pos = Position(x_pos=6, y_pos=5)
            p.validate_move(current_pos, target_pos)

    def test_valid_movement_forward2(self):
        p = create_pawn()
        current_pos = Position(x_pos=1, y_pos=2)
        target_pos = Position(x_pos=1, y_pos=4)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))
    
    def test_valid_movement_forward1(self):
        p = create_pawn()
        current_pos = Position(x_pos=1, y_pos=3)
        target_pos = Position(x_pos=1, y_pos=4)
        self.assertTrue(p.check_valid_move(current_pos, target_pos))


if __name__ == "__main__":
    unittest.main()
