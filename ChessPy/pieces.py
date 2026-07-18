"""
Main file for building game pieces
"""
from position import Position
from movement_strategy import MovementException, MovementBehavior

class Piece:
    def __init__(self, mb: MovementBehavior, color: str = "white", has_moved: bool = False):
        self.mb = mb
        self.has_moved = has_moved
        self.color = color

    def check_valid_move(self, current_pos: Position, target: Position) -> bool:
        return self.mb.check_valid_move(current_pos, target, self.color, self.has_moved)
    
    def validate_move(self, current_pos: Position, target: Position) -> None:
        if not self.check_valid_move(current_pos, target):
            raise MovementException("Invalid Move")

    def mark_moved(self) -> None:
        self.has_moved = True
    
    def captured(self):
        raise NotImplementedError
