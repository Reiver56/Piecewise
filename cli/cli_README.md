# Piecewise Interactive CLI

The `cli` package connects `GameParser`, `GameSession`, and `BoardRenderer` so a
supported Piecewise game can be played from a terminal.

## Files

```text
cli/
├── __init__.py   # Public `GameCLI` import
├── __main__.py   # `python -m cli` entry point
├── game_cli.py   # Testable interactive loop
└── README.md
```

## Start a game

From the project root, start the default Tic-Tac-Toe game:

```bash
python -m cli
```

Or select a `.game` definition explicitly:

```bash
python -m cli games/tictactoe.game
```

Use `--help` to display the launcher options:

```bash
python -m cli --help
```

## Controls

Enter a move as two zero-based integers:

```text
Player X > 1 2
```

The first value is the row and the second is the column. Enter `quit` in any
letter case to abandon the game.

The CLI redraws the board before every turn and after the terminal move. It
reports malformed coordinates and invalid game moves without terminating the
session. A completed game prints either the winning player or a draw message.

## Programmatic use

`GameCLI` can also be imported directly:

```python
from cli import GameCLI
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
final_state = GameCLI(game).run()
```

The constructor accepts injected input and output callables. This keeps the
game loop independent from a real terminal and makes complete sessions
deterministic in tests:

```python
outputs: list[str] = []
inputs = iter(["0 0", "quit"])

cli = GameCLI(
    game,
    input_function=lambda _: next(inputs),
    output_function=outputs.append,
)
state = cli.run()
```

## Current scope

The CLI automatically selects the first piece owned by the current player and
accepts `row column` placement moves. This matches the currently executable
Tic-Tac-Toe DSL. Movement, capture, promotion, gravity, and piece-selection
syntax will require later CLI increments.

## Testing

Run the seven CLI tests from the project root:

```bash
python -m pytest tests/test_game_cli.py -v
```

They cover case-insensitive `quit`, malformed and non-integer input, invalid
game moves, complete victories, complete draws, final rendering, and result
messages.
