# Piecewise Game Engine

The `engine` package turns a validated `GameDefinition` into immutable runtime
snapshots, represents placement and relocation requests, executes supported
placement and non-capturing relocation moves, evaluates terminal conditions,
manages a complete session, and renders the board as plain text.

## Files

```text
engine/
├── __init__.py             # Public engine API
├── board_renderer.py       # Plain-text board rendering
├── condition_evaluator.py  # Win and draw evaluation
├── errors.py               # Engine-specific exceptions
├── game_initializer.py     # GameDefinition to initial GameState
├── game_session.py         # Current-session orchestration
├── game_state.py           # Immutable runtime domain model
├── move.py                 # Immutable placement or relocation request
└── move_executor.py        # Move validation and execution
```

## Runtime model

`game_state.py` defines:

- `Coordinate`: a zero-based row and column;
- `PlacedPiece`: a named piece, its owner, and its coordinate;
- `GameStatus`: `ongoing`, `won`, or `drawn`;
- `GameState`: an immutable snapshot of a running game.

`GameState` enforces positive board dimensions and turn numbers, valid winner
and status combinations, in-bounds pieces, and unique occupied coordinates.

## Move requests

`Move` represents both placement and relocation requests.

A placement specifies only its destination:

```python
placement = Move(
    player="X",
    piece_name="Mark",
    coordinate=Coordinate(row=1, column=1),
)
```

A relocation also specifies the source coordinate:

```python
relocation = Move(
    player="White",
    piece_name="Man",
    source=Coordinate(row=5, column=0),
    coordinate=Coordinate(row=4, column=1),
)
```

`coordinate` remains the destination field for backward compatibility and is
also exposed through the `destination` property. The `is_placement` and
`is_relocation` properties identify the request type.

A move cannot use the same coordinate as both its source and destination.
`Move` instances remain immutable.

## Initialize and play

`GameSession` is the high-level engine API. It validates and initializes the
game, exposes the current snapshot through `state`, and replaces that snapshot
after each successful move:

```python
from engine import Coordinate, GameSession, Move
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
session = GameSession(game)

next_state = session.play(
    Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=1, column=1),
    )
)
```

Previous `GameState` instances remain unchanged. If a move raises
`InvalidMoveError`, the session retains its current snapshot.

`MoveExecutor` rejects moves when the game has ended, when the wrong player is
acting, when a coordinate is outside or unavailable, when a piece is unknown
or unowned, or when a destination is occupied. It dispatches placement and
relocation requests according to the action supported by the piece definition.
A successful move advances the turn and invokes `ConditionEvaluator`.

## Execute a relocation

For a relocation, `MoveExecutor` verifies that:

- the source is inside the board and playable;
- the source contains the requested piece;
- the current player owns that runtime piece;
- the destination is inside the board, playable, and empty;
- source and destination match the declared diagonal distance;
- `diagonal forward` follows the owner's `up` or `down` orientation;
- `diagonal any` may move in either vertical direction.

The source `PlacedPiece` is replaced immutably with a copy at the destination.
All other pieces and the previous `GameState` remain unchanged.

## End conditions

`ConditionEvaluator` supports consecutive same-owner alignments across rows,
columns, and both diagonal directions, plus full-board draws. Only playable
cells count toward a full board. A win takes precedence when the last move also
fills the board.

## Render a board

`BoardRenderer` creates a terminal-friendly view of any rectangular
`GameState`:

```python
from engine import BoardRenderer

print(BoardRenderer(game).render(session.state))
```

```text
    0   1   2
0   . | . | .
1   . | X | .
2   . | . | .
```

The renderer uses:

- `.` for an empty playable cell;
- `#` for a non-playable cell;
- the owner name for a placed piece.

Placed pieces take visual precedence over cell markers. Rendering is read-only
and does not modify the supplied state.

## Architectural boundary

The engine consumes the typed AST and has no dependency on Lark or concrete
DSL syntax. Terminal input and output belong to the separate `cli` package.
The executor supports `ANY_EMPTY_CELL` placement plus validated,
non-capturing `DIAGONAL_FORWARD` and `DIAGONAL_ANY` relocation. Capture,
promotion, gravity, application of parsed initial setup, and interactive
relocation input remain future increments. Movement-rule consistency is
validated before the engine boundary by `SemanticValidator`.

## Testing

Run all engine and renderer tests from the project root:

```bash
python -m pytest \
  tests/test_game_state.py \
  tests/test_game_initializer.py \
  tests/test_game_session.py \
  tests/test_move.py \
  tests/test_condition_evaluator.py \
  tests/test_move_executor.py \
  tests/test_board_renderer.py -v
```

These modules contain 82 engine-focused tests. The complete project suite
contains 113 tests.
