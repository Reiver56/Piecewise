# Piecewise Game Engine

The `engine` package turns a validated `GameDefinition` into immutable runtime
snapshots, represents placement and relocation requests, executes supported
placement moves, evaluates terminal conditions, manages a complete session,
and renders the board as plain text.

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
or unowned, or when a destination is occupied. A successful placement advances
the turn and invokes `ConditionEvaluator`.

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
The runtime model can represent both placement and relocation requests. The
current executor supports only `ANY_EMPTY_CELL` placement. Relocation-rule
validation, capture, promotion, gravity, and initial piece setup remain future
increments.

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

These modules contain 67 engine-focused tests. The complete project suite
contains 84 tests.
