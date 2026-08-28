# Piecewise Graphical Interface

The `gui` package provides a Tkinter interface for choosing and playing the
game definitions bundled with Piecewise. It is a presentation layer over the
existing parser and engine: game rules, move validation, gravity, captures,
promotion, turn rotation, and terminal evaluation remain outside the GUI.

## Files

```text
gui/
├── __init__.py          # Public GUI API
├── __main__.py          # `python -m gui` entry point
├── app.py               # Application shell and game selector
├── game_controller.py   # Click-to-move session adapter
├── game_view.py         # Interactive board and status view
├── theme.py             # Shared colours and fonts
└── README.md
```

## Run the application

From the project root:

```bash
python -m gui
```

The selector offers:

- Tic-Tac-Toe;
- Connect Four;
- Checkers.

Each option is loaded from its corresponding file in `games/` through
`GameParser`. A parse, validation, or initialization failure is displayed in
an error dialog instead of terminating the application.

Tkinter is part of standard Windows Python installations. Some Linux
distributions provide it through a separate system package such as
`python3-tk`.

## Architecture

```text
PiecewiseApp
    -> GameParser
    -> GameController
        -> GameSession
        -> LegalMoveGenerator
    -> GameView
        -> Tkinter widgets
```

The separation is intentional:

- `PiecewiseApp` owns navigation and game loading;
- `GameController` translates cell clicks into engine-level `Move` objects;
- `GameView` renders state and forwards user interaction;
- `GameSession` remains the source of truth for the current immutable state;
- `MoveExecutor` and `ConditionEvaluator` retain all game-rule decisions.

The GUI therefore does not duplicate DSL semantics or engine validation.

## Application shell

`PiecewiseApp` is the main `tk.Tk` window. It creates a shared content frame
and switches between two screens:

- the responsive game selector;
- one active `GameView`.

The selector uses weighted Tkinter grid rows so its three cards divide the
available vertical space evenly. Card text and `Play` controls also use
weighted columns, allowing the interface to grow and shrink with the window
without clipping the final option.

`_open_game()` resolves a bundled filename, parses the definition, creates a
`GameController`, and opens the game view. Returning to the selector destroys
the previous screen before rebuilding the available options.

## Game controller

`GameController` adapts mouse clicks to the two interaction models supported
by the engine.

### Placement games

For Tic-Tac-Toe, the clicked coordinate becomes the move destination directly.

For Connect Four, only the selected column matters. The controller sends a
column-placement request and the engine applies downward gravity to resolve the
lowest empty row.

### Relocation games

Checkers uses two clicks:

1. the first click selects a piece owned by the current player;
2. the second click selects its destination.

Clicking the selected source again cancels the selection. Clicking another
current-player piece changes the source. Empty and opponent-owned sources are
rejected without changing the session state.

After a capture, `forced_capture_source` becomes the new selected source when
the same piece must continue capturing. The selection is cleared only when the
chain ends or the session is restarted.

The `legal_destinations` property filters `LegalMoveGenerator` output by the
selected source. The view uses those coordinates for guidance; the engine still
performs the authoritative validation when the move is applied.

## Game view

`GameView` builds:

- a header with game navigation and restart controls;
- current-player or terminal status text;
- a board with zero-based row and column labels;
- contextual help for placement, column-placement, and relocation games.

Every runtime `Coordinate` maps to one Tkinter button. Non-playable cells are
disabled, selected sources use the selection colour, and legal destinations
use the success colour. When a game reaches `WON` or `DRAWN`, playable cells
are disabled and the final result remains visible.

Invalid moves are reported inline and leave the controller state unchanged.
Restart creates a fresh session snapshot, while the back control returns to the
game selector.

## Piece symbols

The graphical board uses compact owner-based symbols:

| Runtime piece | Symbol |
| --- | --- |
| Tic-Tac-Toe X mark | `X` |
| Tic-Tac-Toe O mark | `O` |
| Red Connect Four disc | `R` |
| Yellow Connect Four disc | `Y` |
| White Checkers man | `W` |
| Black Checkers man | `B` |
| White Checkers king | `WK` |
| Black Checkers king | `BK` |

Owner-specific foreground colours come from `OWNER_COLORS` in `theme.py`.
King symbols retain the owner initial and append `K`, making promotion visible
without changing the runtime model.

## Theme

`theme.py` centralizes:

- background, surface, border, and interaction colours;
- selected-source and legal-destination colours;
- owner-specific piece colours;
- title, status, body, button, card, and board fonts.

Keeping visual constants outside the widgets avoids repeating presentation
choices throughout `app.py` and `game_view.py`.

## Testing

Controller behaviour is tested without opening a real window:

```bash
python -m pytest tests/test_game_controller.py -v
```

Compact graphical piece symbols are tested separately:

```bash
python -m pytest tests/test_game_view.py -v
```

Run the complete suite with:

```bash
python -m pytest -v
```

The complete project currently contains 246 tests.

## Design boundaries

The GUI may:

- load a game definition;
- translate clicks into placement or relocation requests;
- display current state and recoverable errors;
- expose legal destinations as visual guidance.

The GUI must not:

- parse DSL syntax itself;
- reproduce semantic-validation rules;
- decide whether an engine move is legal;
- mutate a `GameState` snapshot;
- evaluate wins, draws, captures, gravity, or promotion independently.

These boundaries keep the Tkinter interface replaceable by another frontend
without changing the Piecewise language or engine.
