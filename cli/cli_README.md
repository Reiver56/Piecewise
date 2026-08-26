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

The supported Checkers definition can be started with:

```bash
python -m cli games/checkers.game
```

Use `--help` to display the launcher options:

```bash
python -m cli --help
```

## Controls

Placement games accept two zero-based integers:

```text
Player X > 1 2
```

The first value is the destination row and the second is the destination
column.

Relocation games accept source and destination coordinates:

```text
Player White > 5 0 4 1
```

The four values follow the order
`source_row source_column destination_row destination_column`. The CLI locates
the runtime piece at the source coordinate and uses its declared piece name in
the generated `Move`. Enter `quit` in any letter case to abandon the game.

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

The CLI selects the input format from the actions available to the current
player. Placement games use `row column`; relocation games use source and
destination coordinates. Invalid formats, non-integer coordinates, empty
sources, opponent-owned sources, and moves rejected by the engine are reported
without terminating the session.

For Checkers, consecutive CLI inputs can complete a mandatory capture chain.
The engine keeps the same player active while another capture is required and
the CLI naturally requests the next relocation. Gravity and piece-specific
rendering remain future increments.

## Testing

Run the 13 CLI tests from the project root:

```bash
python -m pytest tests/test_game_cli.py -v
```

They cover case-insensitive `quit`, placement and relocation formats, malformed
and non-integer input, empty and opponent-owned sources, invalid game moves,
complete victories and draws, chained Checkers captures, final rendering, and
result messages.
