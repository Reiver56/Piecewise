# Piecewise Game Engine

The `engine` package contains the runtime model used to create and represent a
running Piecewise game after parsing and semantic validation.

The current increment provides game-state modelling and initialization. Move
execution and end-condition evaluation will be introduced in later increments.

## Files

```text
engine/
├── __init__.py             # Public engine API
├── errors.py               # Engine-specific exceptions
├── game_initializer.py     # Validated AST to initial runtime state
├── game_state.py           # Immutable runtime domain model
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

## Architectural boundary

The parser constructs the immutable AST. The semantic validator checks domain
relationships and constraints. The engine accepts the resulting definition and
creates runtime state.

The engine does not currently apply moves, rotate turns, place pieces, or
evaluate win and draw conditions.

## Testing

Run the engine tests from the project root:

```bash
python -m pytest tests/test_game_state.py tests/test_game_initializer.py -v
```

