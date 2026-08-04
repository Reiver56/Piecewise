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
- semantic validation with cumulative, structured diagnostics;
- an immutable runtime game-state model with enforced invariants;
- initialization of runtime state from a semantically valid definition;
- immutable placement-move requests;
- validated placement execution with turn rotation;
- parser, AST, semantic-validation, and engine tests with pytest;
- automatic test execution on pull requests through GitHub Actions.

The following features are designed but not implemented yet:

- end-condition evaluation;
- Checkers movement, capture, promotion, and setup;
- Connect Four gravity and column placement;
- command-line or graphical interaction.

The Checkers and Connect Four files are design examples for future DSL
increments. The current grammar parses Tic-Tac-Toe only.

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
│   ├── errors.py                # Engine-specific exceptions
│   ├── game_initializer.py      # Validated AST to initial runtime state
│   ├── game_state.py            # Immutable runtime domain model
│   ├── move.py                  # Immutable placement-move request
│   └── move_executor.py         # Placement validation and execution
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
│   ├── test_semantic_validator.py
│   ├── test_game_initializer.py
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

The initial state contains no placed pieces, starts at turn one, and uses the
first player declared in `turn_order`.

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
```

The executor rejects moves after the game has ended, moves by the wrong player,
coordinates outside the board, non-playable or occupied cells, unknown piece
types, and pieces not owned by the requesting player. Invalid requests raise
`InvalidMoveError`.

## Run the tests

```bash
python -m pytest -v
```

The current suite contains 47 parser, AST-transformation, semantic-validation,
and engine tests. Pull requests targeting `main` run the same command
automatically.

## Documentation

- [`games/README.md`](games/games_README.md): user-facing DSL guide and examples;
- [`grammar/README.md`](grammar/grammar_README.md): grammar structure and Lark notation;
- [`parser/README.md`](parser/parser_README.md): parsing API, AST, and transformation;
- [`engine/README.md`](engine/README.md): runtime model, initialization, and move execution;
- [`tests/README.md`](tests/tests_README.md): test strategy and conventions;
- [`validation/README.md`](validation/README.md): semantic rules and diagnostics.

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

