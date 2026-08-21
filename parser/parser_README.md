# Piecewise Parser and AST

This directory implements the parsing boundary of Piecewise. It converts
`.game` source text into an immutable, typed `GameDefinition`.

## Pipeline

```text
Source text
    -> GameParser
    -> Lark parse tree
    -> GameAstTransformer
    -> GameDefinition
```

The parser layer does not perform semantic validation and does not execute the
game.

## Files

```text
parser/
├── __init__.py
├── ast_nodes.py
├── ast_transformer.py
├── game_parser.py
└── README.md
```

## Responsibilities

This package is responsible for:

- loading `grammar/piecewise.lark`;
- parsing source strings and `.game` files;
- preserving source positions in Lark trees;
- converting supported syntax into typed AST nodes;
- exposing low-level and high-level parsing APIs.

It is not responsible for:

- checking cross-references or domain constraints;
- evaluating win conditions;
- creating runtime board state;
- managing moves or turns.

## Public API

```python
from parser.game_parser import GameParser

parser = GameParser()
```

By default, `GameParser` resolves the grammar relative to the project root. A
different grammar path may be supplied to the constructor.

### Low-level parsing

```python
tree = parser.parse(source_text)
tree = parser.parse_file("games/tictactoe.game")
```

These methods return a Lark `Tree` and are useful for diagnostics, grammar
development, and tests.

### High-level AST parsing

```python
game = parser.parse_game(source_text)
game = parser.parse_game_file("games/tictactoe.game")
```

These methods apply `GameAstTransformer` and return `GameDefinition`. Downstream
components should normally use this high-level API.

Files passed to `parse_file` or `parse_game_file` must use the `.game`
extension.

## AST domain model

`ast_nodes.py` defines immutable dataclasses and enums for the currently
supported domain:

- `GameDefinition`;
- `BoardDefinition`;
- `PlayerDefinition`;
- `PieceDefinition`;
- `AlignCondition`;
- `BoardFullCondition`;
- `PlayableCells`;
- `PlacementType`;
- `ForwardDirection`;
- `MovementDirection`;
- `DestinationCondition`;
- `MovementRule`;
- `AlignmentDirection`;
- `Outcome`.

The dataclasses use `frozen=True` and `slots=True`. Collections are represented
with tuples, making the parsed game definition effectively immutable.

The AST deliberately contains no Lark types. This keeps the domain model
independent from the parsing technology.

## AST transformation

`GameAstTransformer` maps grammar nodes to domain objects:

```text
size_property          -> BoardDefinition data
player_declaration     -> PlayerDefinition
forward_property       -> ForwardDirection data
piece_block            -> PieceDefinition
move_property          -> MovementRule
align_condition        -> AlignCondition
board_full_condition   -> BoardFullCondition
game_definition        -> GameDefinition
```

The private `_PlayersBlock` object groups players and turn order while the
transformer assembles the final game.

## Error handling

Syntax errors are intentionally preserved as Lark exceptions, including:

- `UnexpectedCharacters`;
- `UnexpectedToken`;
- other `UnexpectedInput` subclasses.

Because `propagate_positions=True` is enabled, parse-tree nodes retain line and
column information for future user-facing diagnostics.

Invalid file extensions raise `ValueError`. Missing files continue to raise
standard filesystem exceptions.

Semantic errors are represented separately by `ValidationIssue` and
`SemanticValidationError` in the `validation` package.

## Design decisions

### LALR parsing

The deterministic Piecewise grammar uses Lark's LALR parser for efficient
analysis and useful syntax errors.

### Reusable parser

The grammar is loaded and compiled when `GameParser` is created. The internal
Lark parser is reused for subsequent calls.

### Separate transformation

`GameParser` coordinates the pipeline, while `GameAstTransformer` owns the
mapping logic. This separates source analysis from domain-object construction
and allows the low-level parse tree to remain accessible.

### Separate semantic validation

The AST transformer converts syntax into domain data but does not check whether
references and values are meaningful. These checks belong to the separate
`SemanticValidator`, which consumes the resulting `GameDefinition`.

## Example

```python
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")

print(game.name)                   # TicTacToe
print(game.board.rows)             # 3
print(game.turn_order)             # ("X", "O")
print(game.win_conditions)         # Typed condition objects
```

Movement syntax is transformed into typed domain data as well:

```text
player White {
    forward: up
}

piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
}
```

The player receives `ForwardDirection.UP`. The piece has no placement rule and
contains an immutable `MovementRule` with direction
`MovementDirection.DIAGONAL_FORWARD`, distance `1`, and destination condition
`DestinationCondition.EMPTY`.

## Testing

```bash
python -m pytest -v
```

The current suite verifies:

- valid Tic-Tac-Toe parsing;
- invalid and incomplete syntax;
- invalid file extensions;
- valid directional-player and movement-rule syntax;
- rejection of unsupported forward and movement directions;
- complete AST transformation;
- typed win conditions;
- typed movement rules and AST immutability;
- backward compatibility with the Tic-Tac-Toe AST.

Semantic-validation behaviour is covered independently in
`tests/test_semantic_validator.py`.

## Current limitations

Tic-Tac-Toe is fully transformed. The parser and AST also support the
directional-player and non-capturing diagonal-movement subset required for
Checkers. Capture, promotion, setup, Checkers end conditions, and Connect Four
gravity still require additional grammar and AST increments.

## Next steps

1. improve user-facing diagnostics;
2. add capture and promotion syntax;
3. extend the language for Connect Four;
4. add the remaining Checkers constructs.

