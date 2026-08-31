# Piecewise Interactive CLI

The `cli` package turns terminal input into engine `Move` objects and presents
the resulting immutable game states. It contains no game-rule implementation:
all validation, capture, promotion, gravity, and end-condition behaviour remains
inside the shared engine.

## Files

```text
cli/
├── __init__.py           # Public GameCLI import
├── __main__.py           # python -m cli launcher
├── game_cli.py           # Testable interactive game loop
└── terminal_renderer.py  # Optional ANSI presentation layer
```

## Start a game

From the project root, launch the default Tic-Tac-Toe definition:

```bash
python -m cli
```

Or select one of the bundled games:

```bash
python -m cli games/tictactoe.game
python -m cli games/connectfour.game
python -m cli games/checkers.game
```

Display launcher options:

```bash
python -m cli --help
```

## Input formats

The CLI derives the expected format from the current player's declared piece
actions and prints the relevant help text before each prompt.

| Action | Input example | Meaning |
| --- | --- | --- |
| Direct placement | `1 2` | destination row and column |
| Gravity placement | `3` | destination column |
| Relocation or capture | `5 0 4 1` | source row/column, then destination row/column |
| Abandon game | `quit` | return the current ongoing state |

All coordinates are zero-based. A gravity placement chooses a column; the
engine resolves the lowest empty row. A relocation finds the runtime piece at
the source and uses its actual piece type, which is important after a Checkers
`Man` becomes a `King`.

Malformed input and moves rejected by the engine are reported without ending or
mutating the session. During a mandatory Checkers capture chain, the engine
keeps the same player and forced source active, and the CLI requests the next
relocation normally.

## Terminal presentation

`TerminalRenderer` wraps the engine's plain `BoardRenderer`. This preserves a
colour-independent board representation while allowing the terminal layer to
add presentation details.

The CLI displays:

- game title;
- turn number and current player;
- aligned row and column coordinates;
- contextual input help;
- compact owner symbols;
- `WK` and `BK` for promoted Checkers kings;
- highlighted errors and final results when colours are enabled.

Owner colours are:

| Owner | Colour |
| --- | --- |
| X | bright magenta |
| O | bright cyan |
| Red | bright red |
| Yellow | bright yellow |
| White | bright white |
| Black | bright black/grey |

Colours are enabled only when standard output is an interactive, compatible
terminal. They are disabled when:

- `--no-color` is supplied;
- output is redirected;
- the `NO_COLOR` environment variable is set;
- `TERM=dumb`.

Explicitly disable colours:

```bash
python -m cli games/checkers.game --no-color
```

Removing ANSI sequences from a coloured board produces exactly the same text as
`BoardRenderer`; colours do not change cell widths or game data.

## Programmatic use

`GameCLI` can be imported directly:

```python
from cli import GameCLI
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
final_state = GameCLI(game).run()
```

Input and output callables can be injected, making a complete interaction
deterministic without a real terminal:

```python
outputs: list[str] = []
inputs = iter(["0 0", "quit"])

cli = GameCLI(
    game,
    input_function=lambda _: next(inputs),
    output_function=outputs.append,
    use_color=False,
)

state = cli.run()
```

The launcher decides whether colours are appropriate and passes `use_color` to
`GameCLI`. Tests and embedding code can select the behaviour explicitly.

## Architecture

```text
raw terminal input
    -> GameCLI format selection
    -> Move
    -> GameSession
    -> MoveExecutor
    -> immutable GameState
    -> BoardRenderer
    -> TerminalRenderer
    -> terminal output
```

`GameCLI` coordinates input and output. `TerminalRenderer` styles text.
`GameSession` owns the current snapshot, and the engine remains the authority
for legal moves and results.

## Testing

Run the CLI-related tests:

```bash
python -m pytest tests/test_game_cli.py tests/test_cli_main.py tests/test_terminal_renderer.py -v
```

The final suite contains:

- 24 `GameCLI` cases covering placement, gravity, relocation, errors, turn
  information, contextual help, victories, draws, and capture chains;
- 6 launcher cases collected from the parameterized colour-detection test and
  the `--no-color` parser test;
- 6 terminal-renderer cases covering plain output, coloured pieces, kings,
  alignment, titles, errors, and results.

Together these contribute 36 collected CLI-related cases to the complete
261-case project suite.
