"""
Movement Behavior, follwing strategy design pattern
"""
from abc import ABC, abstractmethod
from position import Position

def on_the_board(p: Position) -> bool:
    if p.x_pos > 8 or p.y_pos > 8 or p.x_pos < 1 or p.y_pos < 1:
        return False
    return True


class MovementException(Exception):
    pass


class OffBoardException(Exception):
    pass


class MovementBehavior(ABC):
    @abstractmethod
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        pass


class PawnMovement(MovementBehavior):
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        # test move is on board (8x8)
        if not on_the_board(target):
            raise OffBoardException
        
        x_diff: int = target.x_pos - current_pos.x_pos
        y_diff: int = target.y_pos - current_pos.y_pos
        direction = -1 if color == "black" else 1

        if x_diff != 0:
            return abs(x_diff) == 1 and y_diff == direction
            
        if y_diff == 0:
            return False
        if y_diff == direction:
            return True
        if y_diff == 2 * direction and not has_moved:
            return True
        return False
            

class RookMovement(MovementBehavior):
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        # test move is on board (8x8)
        if not on_the_board(target):
            raise OffBoardException
        # test move is not on both x and y axis
        if (current_pos.x_pos != target.x_pos) and (current_pos.y_pos != target.y_pos):
            return False
        
        if current_pos.x_pos == target.x_pos and current_pos.y_pos == target.y_pos:
            return False
        
        return True


class KnightMovement(MovementBehavior):
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        # test move is on board (8x8)
        if not on_the_board(target):
            raise OffBoardException
        # Knights are tricky, can move  y + 1 then x +- 2 or y + 2 then x +- 1
        x_diff: int = abs(target.x_pos - current_pos.x_pos)
        y_diff: int = abs(target.y_pos - current_pos.y_pos)

        if y_diff > 2 or x_diff > 2:
            return False
        
        if y_diff == 0 or x_diff == 0:
            return False
        
        if y_diff == 2:
            return x_diff == 1
        elif y_diff == 1:
            return x_diff == 2


class BishopMovement(MovementBehavior):
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        # test move is on board (8x8)
        if not on_the_board(target):
            raise OffBoardException
        # Diagonal movement requires the x_diff and y_diff to be equal
        x_diff: int = abs(target.x_pos - current_pos.x_pos)
        y_diff: int = abs(target.y_pos - current_pos.y_pos)
        
        # Catch non-movement attempts
        return x_diff == y_diff and not (x_diff == 0 or y_diff == 0)


class QueenMovement(MovementBehavior):
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        # test move is on board (8x8)
        if not on_the_board(target):
            raise OffBoardException

        x_diff: int = abs(target.x_pos - current_pos.x_pos)
        y_diff: int = abs(target.y_pos - current_pos.y_pos)

        if x_diff == 0 and y_diff == 0:
            return False
        
        if (x_diff == 0 and y_diff != 0) or (x_diff != 0 and y_diff == 0):
            return True
        else:
            return x_diff == y_diff


class KingMovement(MovementBehavior):
    def check_under_threat(self, target: Position) -> bool:
        # Not implemented yet
        return False
    
    def check_valid_move(self, current_pos: Position, target: Position, color: str = "white", has_moved: bool = False) -> bool:
        # test move is on board (8x8)
        if not on_the_board(target):
            raise OffBoardException
        
        if self.check_under_threat(target):
            return False
        
        # King can move any direction, one space
        x_diff: int = abs(target.x_pos - current_pos.x_pos)
        y_diff: int = abs(target.y_pos - current_pos.y_pos)

        if x_diff > 1 or y_diff > 1 or (x_diff == 0 and y_diff == 0):
            return False
        
        return True
        
