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
- diagonal-capture syntax and immutable capture rules in the AST;
- back-rank promotion syntax and immutable promotion rules in the AST;
- Checkers player-state end-condition syntax and immutable condition nodes in
  the AST;
- optional initial-setup syntax and immutable setup rules in the AST;
- semantic validation with cumulative, structured diagnostics;
- semantic validation of piece actions and movement rules;
- semantic validation of capture dependencies, distances, and orientation;
- semantic validation of promotion targets, movement dependency, ownership,
  and back-rank orientation;
- semantic validation of setup references, ownership, row ranges, and overlaps;
- semantic validation of Checkers player-state end-condition targets, including
  the requirement that `opponent` refers to exactly one of two players;
- an immutable runtime game-state model with enforced invariants;
- initialization of runtime state and setup pieces from a valid definition;
- immutable placement and relocation requests;
- validated placement, ordinary relocation, capture, chained capture, and
  back-rank promotion execution with controlled turn rotation;
- deterministic generation of legal ordinary and capture moves for the current
  player, with mandatory captures and forced chain sources taking precedence;
- automatic evaluation of row, column, and diagonal win conditions;
- automatic Checkers victory when the opponent has no pieces or no legal moves
  left;
- full-board draw detection with victory taking precedence;
- complete game-session management with sequential state updates;
- text rendering for rectangular boards and non-playable cells;
- an interactive Tic-Tac-Toe CLI with recoverable input errors;
- parser, AST, semantic-validation, engine, renderer, and CLI tests with pytest;
- automatic test execution on pull requests through GitHub Actions.

The following features are designed but not implemented yet:

- interactive Checkers play and piece-specific rendering;
- Connect Four gravity and column placement;
- graphical interaction.

The Checkers and Connect Four files are design examples for future DSL
increments. The grammar and AST now support the directional-player, basic
movement, capture, promotion, initial-setup, and player-state end-condition
declarations used by Checkers. Movement, capture, promotion, and setup are also
validated or executed by their current subsets. Checkers end-condition targets
are also validated semantically. After each move, the engine evaluates both
`no_pieces_left` and `no_moves_left` against the next player.

## Architecture

```text
.game source
    -> Lark parser
    -> Parse tree
    -> AST transformer
    -> GameDefinition
    -> Semantic validator
    -> Initial GameState
    -> Legal move generation
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
│   ├── legal_move_generator.py  # Current-player legal move discovery
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
│   ├── test_legal_move_generator.py
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

## Generate legal moves

`LegalMoveGenerator` derives the current player's available movement and
capture requests from an immutable `GameState`:

```python
from engine import LegalMoveGenerator

moves = LegalMoveGenerator(game).generate(state)
```

It supports `diagonal forward` and `diagonal any`, respects player orientation,
board limits, playable cells, occupied destinations, and enemy-only capture
targets. Results are returned as an immutable tuple in deterministic piece,
direction, and destination order. When at least one current-player piece can
capture, the generator returns only captures and suppresses every ordinary
move, including moves belonging to other pieces. During a chained capture,
`GameState.forced_capture_source` further restricts generation to the piece
that started the sequence. An empty tuple means the current player has no
generated move and is used directly by `ConditionEvaluator` for
`no_moves_left`.

## Define capture rules

Movement pieces may optionally declare a capture rule:

```text
piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
    capture: diagonal forward 2 if enemy
}
```

The grammar supports both `diagonal forward` and `diagonal any` capture
directions. Each declaration becomes an immutable `CaptureRule` containing its
typed direction, distance, and `CaptureCondition.ENEMY`. Pieces without a
capture declaration keep `PieceDefinition.capture` set to `None`.

Capture rules are also validated semantically. A capture requires a normal
movement rule, its distance must be positive, and every owner of a `diagonal
forward` capture must declare `forward: up` or `forward: down`.

At runtime, `MoveExecutor` distinguishes ordinary relocation distance from
capture distance. It validates `diagonal forward` or `diagonal any`, identifies
the intermediate coordinate, requires an enemy piece there, and returns a new
snapshot with the moving piece at its destination and the enemy removed. The
previous `GameState` remains unchanged. Capturing the opponent's last remaining
piece now produces a won state. When any capture is available, `MoveExecutor`
rejects otherwise valid ordinary relocations and accepts the required capture.
If the moved piece can capture again, the immutable continuation state keeps
the same player and turn number and records the piece's destination as the
forced source. Turn rotation and terminal evaluation occur only when the chain
ends.

## Define promotion rules

A movement piece may declare a target type for promotion on the back rank:

```text
piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
    promote: back_rank -> King
}
```

The grammar maps `back_rank` to `PromotionCondition.BACK_RANK` and stores the
target identifier in an immutable `PromotionRule`. The optional
`PieceDefinition.promotion` field remains `None` for pieces such as `King` that
do not promote.

Promotion rules are validated before reaching the engine. The source must be a
movement piece, the target must be declared and different from the source, and
every source owner must also be supported by the target piece. A `back_rank`
promotion additionally requires every owner to declare `forward: up` or
`forward: down`.

After an ordinary relocation or capture, `MoveExecutor` compares the
destination row with the active owner's back rank: row `0` for `up` and
`rows - 1` for `down`. On a match, it immutably replaces the moved
`PlacedPiece` name with the declared target type. Moves ending before the back
rank preserve the source type, and the previous `GameState` remains unchanged.

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

Setup rules are validated semantically before reaching the engine. The
validator checks that referenced pieces and players exist, that ownership is
allowed, that one-based row ranges are ordered and fit the board, and that two
rules do not overlap. `GameInitializer` converts valid ranges to zero-based
coordinates and creates a `PlacedPiece` on each selected playable cell.

## Define Checkers end conditions

Checkers may declare victory when the opponent has no pieces or no legal
moves:

```text
win_condition {
    no_pieces_left: opponent -> win
    no_moves_left: opponent -> win
}
```

The grammar accepts only the typed target `opponent`. The transformer maps it
to `PlayerTarget.OPPONENT` and creates immutable `NoPiecesLeftCondition` and
`NoMovesLeftCondition` objects with `Outcome.WIN`. The semantic validator
requires exactly two declared players so `opponent` identifies one unambiguous
player. It also rejects unsupported targets in AST objects constructed directly
in Python. At runtime, `ConditionEvaluator` awards the active player a victory
when a move leaves the declared opponent without pieces or without any legal
ordinary or capture move.

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

The initial state starts at turn one and uses the first player declared in
`turn_order`. Games without setup rules begin with no pieces. For configured
setups, `GameInitializer` preserves rule order, expands each inclusive row
range, and filters cells according to `ALL`, `DARK`, or `LIGHT` board
playability.

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

For a capture relocation, the executor matches `capture.distance`, validates
the declared direction, and inspects the intermediate diagonal cell. An empty
cell or a piece owned by the active player makes the move invalid. A successful
capture removes exactly one enemy, advances the turn, and preserves the
previous snapshot. When the destination is the active player's back rank, the
surviving piece is promoted after the enemy is removed. Capturing the final
opponent piece immediately produces a won state. If the next player still owns
pieces but has no generated legal move, `no_moves_left` also produces a victory.
Mandatory capture is enforced across all pieces owned by the active player. A
chained capture must continue from `forced_capture_source`; completing the
sequence clears that field, advances the turn once, and then evaluates terminal
conditions. Promotion remains immediate, so a newly promoted `King` may continue
the same chain using `diagonal any`.

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

The current suite contains 192 parser, AST-transformation, semantic-validation,
engine, renderer, and CLI tests. Pull requests targeting `main` run the same command
automatically.

## Documentation

- [`games/README.md`](games/games_README.md): user-facing DSL guide and examples;
- [`grammar/README.md`](grammar/grammar_README.md): grammar structure and Lark notation;
- [`parser/README.md`](parser/parser_README.md): parsing API, AST, and transformation;
- [`engine/README.md`](engine/engine_README.md): runtime model, initialization, and move execution;
- [`cli/README.md`](cli/cli_README.md): interactive play and command-line entry point;
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

