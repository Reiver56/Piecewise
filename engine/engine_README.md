# Piecewise Game Engine

The `engine` package contains the runtime model used to create and represent a
running Piecewise game after parsing and semantic validation.

The current increment provides game-state modelling, initialization, validated
placement-move execution, and automatic evaluation of win and draw conditions.

## Files

```text
engine/
├── __init__.py             # Public engine API
├── condition_evaluator.py  # Win and draw condition evaluation
├── errors.py               # Engine-specific exceptions
├── game_initializer.py     # Validated AST to initial runtime state
├── game_state.py           # Immutable runtime domain model
├── move.py                 # Immutable placement-move request
├── move_executor.py        # Placement validation and execution
└── README.md
```

## Runtime model

`game_state.py` defines:

- `Coordinate`: a zero-based row and column on the runtime board;
- `PlacedPiece`: a named piece, its owner, and its coordinate;
- `GameStatus`: `ongoing`, `won`, or `drawn`;
- `GameState`: an immutable snapshot of a running game.

`GameState` enforces the following invariants:

- board dimensions are greater than zero;
- turn numbers start at one;
- the current player is not empty;
- only a won game has a winner, and every won game has one;
- placed pieces remain inside the board;
- no two pieces occupy the same coordinate.

## Initialize a game

`GameInitializer` validates a `GameDefinition` before creating its initial
runtime state:

```python
from engine import GameInitializer
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
state = GameInitializer().initialize(game)

print(state.current_player)  # X
print(state.turn_number)     # 1
print(state.pieces)          # ()
```

The initial state uses the board dimensions from the definition, selects the
first player in `turn_order`, starts at turn one, contains no placed pieces, and
has status `GameStatus.ONGOING`.

Validation is repeated at the engine boundary because `GameDefinition` does not
record whether it has already been validated. Invalid definitions raise
`GameInitializationError` with the collected semantic diagnostics.

## Represent a move

`Move` is an immutable placement request containing the requesting player, the
piece type, and its destination coordinate:

```python
from engine import Coordinate, Move

move = Move(
    player="X",
    piece_name="Mark",
    coordinate=Coordinate(row=1, column=1),
)
```

The player and piece name cannot be empty. State-dependent rules are enforced
by `MoveExecutor`, not by the request object.

## Execute a placement move

`MoveExecutor` applies a valid move and returns a new `GameState`:

```python
from engine import GameInitializer, MoveExecutor
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
state = GameInitializer().initialize(game)
next_state = MoveExecutor(game).apply(state, move)

print(next_state.current_player)  # O
print(next_state.turn_number)     # 2
print(state.pieces)               # ()
```

The executor validates that:

- the game is still ongoing;
- the move belongs to the current player;
- the coordinate is inside the runtime board;
- the destination is allowed by the board's `playable_cells` setting;
- the piece type exists and belongs to the requesting player;
- the destination cell is empty.

A successful move appends a `PlacedPiece`, advances the turn number, rotates to
the next player declared in `turn_order`, and evaluates the declared end
conditions. The previous state is unchanged. Rejected requests raise
`InvalidMoveError`.

This increment supports the DSL's current `ANY_EMPTY_CELL` placement model. It
does not yet implement movement, capture, promotion, gravity, or initial piece
setup.

## Evaluate end conditions

`ConditionEvaluator` evaluates the state produced by a placement move using the
conditions declared in the game's immutable AST:

```python
from engine import ConditionEvaluator

evaluated_state = ConditionEvaluator(game).evaluate(
    next_state,
    move,
)
```

For normal gameplay, callers do not need to invoke the evaluator directly:
`MoveExecutor.apply()` performs this step automatically after placement.

The evaluator supports:

- consecutive same-owner alignments in a row;
- consecutive same-owner alignments in a column;
- consecutive same-owner alignments across both diagonal directions;
- full-board draws based only on the board's playable cells.

Alignment checks start from the last placed piece, because a new win can only
be created by the latest move. When a move both creates a winning alignment and
fills the board, victory takes precedence over the draw condition. A win sets
`GameStatus.WON` and the winner; a draw sets `GameStatus.DRAWN`. If no terminal
condition matches, the existing ongoing state is returned unchanged.

## Architectural boundary

The parser constructs the immutable AST. The semantic validator checks domain
relationships and constraints. The engine accepts the resulting definition and
creates runtime state.

The engine does not depend on Lark or concrete syntax. It consumes the typed
`GameDefinition`, creates immutable runtime snapshots, applies placement moves,
and evaluates the AST's typed end conditions.

## Testing

Run the engine tests from the project root:

```bash
python -m pytest tests/test_game_state.py tests/test_game_initializer.py tests/test_move.py tests/test_condition_evaluator.py tests/test_move_executor.py -v
```

These modules contain 49 engine-focused test cases. Run `python -m pytest -v`
from the project root for the complete 59-test suite.

