# Piecewise

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/DSL-Piecewise-6f42c1" alt="Piecewise DSL"/>
  <a href="https://github.com/lark-parser/lark">
    <img src="https://img.shields.io/badge/Parser-Lark-orange" alt="Lark parser"/>
  </a>
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow" alt="Development status"/>
  <a href="https://github.com/Reiver56/Piecewise/actions/workflows/tests.yml">
    <img src="https://github.com/Reiver56/Piecewise/actions/workflows/tests.yml/badge.svg" alt="Tests"/>
  </a>
</p>

<p align="center">
  <img src="giphy.gif" alt="Piecewise demonstration" width="600"/>
</p>

Piecewise is a Domain-Specific Language (DSL) for defining deterministic,
turn-based board games on rectangular grids.

The project is being developed for the Advanced Software Engineering course
(2025/2026). Its main goal is to explore language design, parsing, domain
modelling, semantic validation, modular architecture, and automated testing.

## Project status

Piecewise is under active development.

The current increment supports:

- a declarative Tic-Tac-Toe definition;
- syntax parsing with Lark;
- generation of a Lark parse tree;
- transformation into an immutable, typed AST;
- directional-player and diagonal-movement syntax in the grammar and AST;
- optional initial-setup syntax and immutable setup rules in the AST;
- semantic validation with cumulative, structured diagnostics;
- semantic validation of piece actions and movement rules;
- an immutable runtime game-state model with enforced invariants;
- initialization of runtime state from a semantically valid definition;
- immutable placement and relocation requests;
- validated placement and non-capturing relocation execution with turn rotation;
- automatic evaluation of row, column, and diagonal win conditions;
- full-board draw detection with victory taking precedence;
- complete game-session management with sequential state updates;
- text rendering for rectangular boards and non-playable cells;
- an interactive Tic-Tac-Toe CLI with recoverable input errors;
- parser, AST, semantic-validation, engine, renderer, and CLI tests with pytest;
- automatic test execution on pull requests through GitHub Actions.

The following features are designed but not implemented yet:

- Checkers capture, promotion, setup validation and execution, end conditions,
  and interactive play;
- Connect Four gravity and column placement;
- graphical interaction.

The Checkers and Connect Four files are design examples for future DSL
increments. The grammar and AST now support the directional-player, basic
movement, and initial-setup declarations used by Checkers, but the complete
files still contain unsupported constructs.

## Architecture

```text
.game source
    -> Lark parser
    -> Parse tree
    -> AST transformer
    -> GameDefinition
    -> Semantic validator
    -> Initial GameState
    -> Move validation
    -> Next GameState
    -> Win/draw evaluation
    -> Ongoing or terminal GameState
    -> GameSession current state
    -> BoardRenderer
    -> Interactive GameCLI
```

Parsing, transformation, validation, and execution are intentionally separated.
This keeps the domain model independent from Lark and prevents the game engine
from depending on concrete syntax details.

## Project structure

```text
Piecewise/
├── .github/
│   └── workflows/
│       └── tests.yml            # Pull-request test workflow
├── engine/
│   ├── README.md                # Runtime-model and initialization guide
│   ├── board_renderer.py        # Plain-text board rendering
│   ├── condition_evaluator.py   # Win and draw condition evaluation
│   ├── errors.py                # Engine-specific exceptions
│   ├── game_initializer.py      # Validated AST to initial runtime state
│   ├── game_session.py          # Complete game-session orchestration
│   ├── game_state.py            # Immutable runtime domain model
│   ├── move.py                  # Immutable placement or relocation request
│   └── move_executor.py         # Placement validation and execution
├── cli/
│   ├── README.md                # Interactive CLI guide
│   ├── __init__.py              # Public CLI API
│   ├── __main__.py              # `python -m cli` entry point
│   └── game_cli.py              # Testable interactive game loop
├── games/
│   ├── README.md                # Guide to Piecewise game definitions
│   ├── tictactoe.game           # Currently supported example
│   ├── checkers.game            # Planned DSL extension
│   └── connectfour.game         # Planned DSL extension
├── grammar/
│   ├── README.md                # Lark grammar documentation
│   └── piecewise.lark           # Current formal grammar
├── parser/
│   ├── README.md                # Parser and AST documentation
│   ├── ast_nodes.py             # Immutable AST domain objects
│   ├── ast_transformer.py       # Parse-tree to AST transformation
│   └── game_parser.py           # Public parsing API
├── tests/
│   ├── tests_README.md          # Testing strategy
│   ├── test_parser.py
│   ├── test_ast_transformer.py
│   ├── test_board_renderer.py
│   ├── test_game_cli.py
│   ├── test_semantic_validator.py
│   ├── test_condition_evaluator.py
│   ├── test_game_initializer.py
│   ├── test_game_session.py
│   ├── test_game_state.py
│   ├── test_move.py
│   └── test_move_executor.py
├── validation/
│   ├── README.md                # Semantic-validation guide
│   ├── errors.py                # Structured validation diagnostics
│   └── semantic_validator.py    # Domain-consistency checks
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or newer;
- Lark;
- pytest.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Parse a game

`GameParser` offers a high-level API that returns a typed `GameDefinition`:

```python
from parser.game_parser import GameParser

parser = GameParser()
game = parser.parse_game_file("games/tictactoe.game")

print(game.name)
print(game.board)
print(game.players)
```

Low-level methods are also available when the Lark parse tree is needed:

```python
tree = parser.parse_file("games/tictactoe.game")
print(tree.pretty())
```

## Validate a game

Semantic validation is an explicit stage after AST construction:

```python
from parser.game_parser import GameParser
from validation import SemanticValidator

game = GameParser().parse_game_file("games/tictactoe.game")
SemanticValidator().validate_or_raise(game)
```

Use `validate()` instead to receive every issue as an immutable tuple without
raising an exception.

## Define movement rules

Players may declare the direction considered forward:

```text
player White {
    forward: up
}
```

Pieces may declare a non-capturing diagonal movement rule:

```text
piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
}
```

The grammar also supports `diagonal any`, which is represented by a typed,
immutable `MovementRule`. These declarations are parsed, transformed, and
validated semantically. `MoveExecutor` executes the supported non-capturing
movement rules.

Each piece must declare exactly one action: `place` or `move`. Movement
distances must be positive, and every owner of a `diagonal forward` piece must
declare a forward direction. Violations are returned as cumulative,
machine-readable diagnostics.

## Define an initial setup

Games may optionally declare one or more initial-placement rules after their
piece blocks and before `win_condition`:

```text
setup {
    place: Man owned_by White on rows 6..8 playable_cells
    place: Man owned_by Black on rows 1..3 playable_cells
}
```

Each declaration becomes an immutable `SetupRule` containing the piece name,
owner, inclusive row range, and the requirement to use playable cells only.
The row numbers remain one-based in the AST so it faithfully represents the
DSL source. Games without a setup block receive an empty setup tuple.

This increment covers syntax and AST transformation only. Checking setup
references and row ranges, converting them to zero-based coordinates, and
placing runtime pieces remain separate validation and engine increments.

## Initialize a game

`GameInitializer` validates the definition at the engine boundary and creates
the initial immutable `GameState`:

```python
from engine import GameInitializer
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
state = GameInitializer().initialize(game)

print(state.current_player)
print(state.turn_number)
```

The initial state currently contains no placed pieces, starts at turn one, and
uses the first player declared in `turn_order`. Parsed setup rules are not yet
applied by `GameInitializer`.

## Represent a move

`Move` represents both placement and relocation requests. A placement specifies
only its destination:

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
also available through `destination`. The `is_placement` and `is_relocation`
properties identify the request type. Source and destination must differ.

The runtime model can express relocation requests, while the DSL, AST, and
semantic validator describe and validate basic movement rules. `MoveExecutor`
applies validated `diagonal forward` and `diagonal any` relocations to immutable
runtime snapshots.

## Execute a placement move

`MoveExecutor` validates a placement request and returns a new immutable
`GameState` without modifying the previous snapshot:

```python
from engine import Coordinate, GameInitializer, Move, MoveExecutor
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
state = GameInitializer().initialize(game)

move = Move(
    player="X",
    piece_name="Mark",
    coordinate=Coordinate(row=1, column=1),
)
next_state = MoveExecutor(game).apply(state, move)

print(next_state.current_player)  # O
print(next_state.turn_number)     # 2
print(next_state.status)          # GameStatus.ONGOING
```

The executor rejects moves after the game has ended, moves by the wrong player,
coordinates outside the board, non-playable or occupied cells, unknown piece
types, and pieces not owned by the requesting player. Invalid requests raise
`InvalidMoveError`.

After placing a piece, the executor evaluates the declared end conditions. It
detects consecutive same-owner alignments across rows, columns, and both
diagonals, and detects a draw when every playable cell is occupied. A winning
alignment takes precedence when the final move also fills the board. The
returned state is marked `GameStatus.WON` with its winner or
`GameStatus.DRAWN`; further moves are then rejected.

## Execute a relocation move

A relocation identifies both its source and destination. `MoveExecutor`
verifies the source piece, its owner and type, the destination, the declared
distance, and the allowed diagonal direction:

```python
move = Move(
    player="White",
    piece_name="Man",
    source=Coordinate(row=5, column=0),
    coordinate=Coordinate(row=4, column=1),
)

next_state = MoveExecutor(game).apply(state, move)
```

`diagonal forward` uses the owner's `forward: up|down` declaration, while
`diagonal any` accepts either vertical direction. Successful relocation
replaces the source piece with an equivalent piece at the destination, advances
the turn, and leaves the previous `GameState` unchanged.

The current relocation executor is deliberately non-capturing. Applying the
parsed initial setup, captures, promotion, and Checkers-specific end conditions
remain future increments.

## Manage a complete game session

`GameSession` is the high-level engine API for running a game from its initial
state through a sequence of moves:

```python
from engine import Coordinate, GameSession, Move
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
session = GameSession(game)

session.play(
    Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )
)

print(session.state.current_player)  # O
print(session.state.turn_number)     # 2
```

The session initializes the game automatically, exposes its current immutable
state through `state`, and replaces that snapshot after every successful
`play()` call. If a move is invalid, the exception is propagated and the
session keeps its previous state. Terminal-state protection remains delegated
to `MoveExecutor`, so moves after a win or draw are rejected consistently.

## Render a board

`BoardRenderer` converts a runtime snapshot into plain text without modifying
the state:

```python
from engine import BoardRenderer, GameSession
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
session = GameSession(game)

print(BoardRenderer(game).render(session.state))
```

```text
    0   1   2
0   . | . | .
1   . | . | .
2   . | . | .
```

The renderer uses `.` for an empty playable cell, `#` for a non-playable cell,
and the piece owner as the placement symbol.

## Play from the terminal

Start the bundled Tic-Tac-Toe definition from the project root:

```bash
python -m cli
```

An explicit `.game` path can also be supplied:

```bash
python -m cli games/tictactoe.game
```

Enter moves as zero-based `row column` coordinates, such as `1 2`. Invalid
input is reported without ending the session. Enter `quit` to abandon the
current game.

## Run the tests

```bash
python -m pytest -v
```

The current suite contains 113 parser, AST-transformation, semantic-validation,
engine, renderer, and CLI tests. Pull requests targeting `main` run the same command
automatically.

## Documentation

- [`games/README.md`](games/games_README.md): user-facing DSL guide and examples;
- [`grammar/README.md`](grammar/grammar_README.md): grammar structure and Lark notation;
- [`parser/README.md`](parser/parser_README.md): parsing API, AST, and transformation;
- [`engine/README.md`](engine/README.md): runtime model, initialization, and move execution;
- [`cli/README.md`](cli/README.md): interactive play and command-line entry point;
- [`tests/README.md`](tests/tests_README.md): test strategy and conventions;
- [`validation/README.md`](validation/validation_README.md): semantic rules and diagnostics.

## Development workflow

Development is organised into small feature branches and pull requests. Each
increment should:

1. define a focused change;
2. include positive and negative tests where applicable;
3. update the relevant documentation;
4. pass the required `pytest` status check before merge.

## Scope

The initial scope covers deterministic, turn-based games on rectangular grids.
Card games, hidden information, random events, and real-time mechanics are
outside the current project scope.
