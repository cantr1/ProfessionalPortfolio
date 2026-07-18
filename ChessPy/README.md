# ChessPy

ChessPy is a Python chess movement engine prototype built to practice object-oriented design, the Strategy design pattern, and test-driven thinking.

The project models chess pieces by separating each piece's movement rules into interchangeable movement strategy classes. A `Piece` owns color and movement state, while the board coordinates piece placement, path blocking, captures, and move execution.

## Goals

- Practice the Strategy design pattern with concrete chess movement rules
- Keep movement behavior isolated from board state
- Build confidence writing focused unit tests
- Model a small but rule-heavy domain in plain Python
- Create a terminal-playable prototype around the core movement engine

## Current Features

- 8x8 board model using immutable `Position` values
- Piece abstraction with injected movement behavior
- Movement strategies for pawns, rooks, knights, bishops, queens, and kings
- Board setup for a standard starting position
- Path-blocking validation for sliding pieces
- Pawn-specific capture and forward-movement rules
- Capture handling when moving onto occupied target squares
- Simple terminal gameplay loop using chess-style coordinates such as `B1 C3`
- Unit tests for each piece's movement behavior and board operations

## Project Structure

```text
ChessPy/
├── board.py                 # Board, squares, setup, path validation, and piece movement
├── pieces.py                # Piece abstraction that delegates movement rules
├── movement_strategy.py     # Strategy interface and concrete movement behaviors
├── position.py              # Immutable board coordinate value object
├── main.py                  # Terminal gameplay loop
└── tests/                   # Unit tests for movement rules and board behavior
```

## Design

The central design choice is using Strategy to make movement behavior composable:

- `MovementBehavior` defines the movement validation interface.
- `PawnMovement`, `RookMovement`, `KnightMovement`, `BishopMovement`, `QueenMovement`, and `KingMovement` each implement piece-specific movement rules.
- `Piece` delegates move validation to its injected movement strategy.
- `Board` handles stateful concerns such as occupied squares, blocked paths, captures, and piece placement.

This keeps "how a piece moves" separate from "what is currently on the board", which makes the code easier to test and extend.

## Run the Game

From the `ChessPy` directory:

```sh
python3 main.py
```

Move input uses a start and target coordinate:

```text
B1 C3
```

## Run Tests

From the `ChessPy` directory:

```sh
python3 -m unittest discover -s tests
```

## Current Limitations

This project is focused on movement rules and design practice. It does not yet implement every full chess rule, including check, checkmate, castling, en passant, promotion, stalemate, or legal move filtering based on king safety.
