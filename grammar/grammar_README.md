# Piecewise Grammar

This directory contains the formal Lark grammar used to parse Piecewise
`.game` files.

## Current pipeline

```text
.game file -> Lark grammar -> Parse tree -> GameAstTransformer -> GameDefinition
```

The grammar performs syntactic analysis. The transformer is implemented and
converts the resulting tree into typed AST objects. Semantic validation and
execution remain separate future stages.

## Files

```text
grammar/
├── piecewise.lark
└── README.md
```

## Entry point

```lark
start: game_definition
```

The top-level rule requires:

```lark
game_definition: "game" NAME "{" board_block players_block piece_block+ win_condition_block "}"
```

Therefore, the current grammar expects blocks in this order:

1. one board block;
2. one players block;
3. one or more piece blocks;
4. one win-condition block.

## Supported grammar

### Board

```lark
board_block: "board" "{" board_property+ "}"
```

Supported properties:

- `size: ROWSxCOLUMNS`;
- `playable_cells: all|dark|light`.

### Players

```lark
players_block: "players" "{" player_declaration+ turn_order "}"
```

The block contains player declarations followed by `turn_order`.

### Pieces

```lark
piece_block: "piece" NAME "{" piece_property+ "}"
```

The current piece properties are:

- `owner`;
- `place: any_empty_cell`.

### End conditions

The grammar supports:

- `align` with `same_row`, `same_col`, or `diagonal`;
- `board_full: no_winner -> draw`.

## Transformer-oriented aliases

Literal alternatives use Lark aliases:

```lark
playable_cells: "all"   -> all_cells
              | "dark"  -> dark_cells
              | "light" -> light_cells
```

and:

```lark
alignment_direction: "same_row" -> same_row
                   | "same_col" -> same_col
                   | "diagonal" -> diagonal
```

These aliases preserve which literal was selected in the parse tree, allowing
`GameAstTransformer` to map each value to the correct enum.

## Lark notation

| Notation | Meaning |
| --- | --- |
| `"text"` | Literal text required in the input |
| `rule` | Reference to another rule |
| `A \| B` | Either `A` or `B` |
| `rule+` | One or more occurrences |
| `rule*` | Zero or more occurrences |
| `rule?` | Zero or one occurrence |
| `?rule:` | Inline the rule when possible |
| `-> alias` | Rename the produced parse-tree node |

## Tokens and whitespace

```lark
%import common.CNAME -> NAME
%import common.INT
%import common.WS
%ignore WS
```

- `NAME` represents identifiers such as `TicTacToe`, `Mark`, and `X`;
- `INT` represents dimensions and alignment lengths;
- whitespace and indentation have no syntactic meaning.

## Inspect the parse tree

```python
from parser.game_parser import GameParser

tree = GameParser().parse_file("games/tictactoe.game")
print(tree.pretty())
```

A valid source produces a tree. Invalid syntax raises a Lark
`UnexpectedInput` subclass such as `UnexpectedCharacters` or
`UnexpectedToken`.

## Syntax versus semantics

The grammar verifies form, not domain correctness. For example:

```text
owner: UnknownPlayer
```

is syntactically valid because `UnknownPlayer` is a valid `NAME`. Determining
whether that player was declared belongs to semantic validation.

## Current limitations

The current grammar parses the Tic-Tac-Toe subset only. It does not support:

- directional players;
- piece movement or capture;
- promotion;
- initial setup;
- gravity;
- placement by column;
- Checkers or Connect Four definitions.

## Extension workflow

Every grammar extension should:

1. begin with a representative `.game` example;
2. add a valid parser test;
3. add at least one invalid test;
4. update the grammar;
5. update AST nodes and transformation when necessary;
6. inspect the resulting parse tree;
7. update this document.

