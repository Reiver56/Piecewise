# Piecewise Grammar

This directory contains the formal Lark grammar used to parse Piecewise
`.game` files.

## Current pipeline

```text
.game file -> Lark grammar -> Parse tree -> GameAstTransformer -> GameDefinition
```

The grammar performs syntactic analysis. The transformer converts the resulting
tree into typed AST objects. Semantic validation and execution remain separate
stages.

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
game_definition: "game" NAME "{" board_block players_block piece_block+ setup_block? win_condition_block "}"
```

Therefore, the current grammar expects blocks in this order:

1. one board block;
2. one players block;
3. one or more piece blocks;
4. zero or one setup block;
5. one win-condition block.

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

A player may optionally declare its forward direction:

```text
player White {
    forward: up
}
```

Supported values are `up` and `down`. Players without a block remain valid, so
the Tic-Tac-Toe declarations `player X` and `player O` are unchanged.

### Pieces

```lark
piece_block: "piece" NAME "{" piece_property+ "}"
```

The current piece properties are:

- `owner`;
- `place: any_empty_cell`;
- `move: diagonal forward DISTANCE if empty`;
- `move: diagonal any DISTANCE if empty`.

For example:

```text
piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
}
```

Movement distances use `INT`. Whether a distance or rule is meaningful belongs
to semantic validation rather than grammar parsing.

### Initial setup

An optional setup block may contain one or more initial-placement rules:

```lark
setup_block: "setup" "{" setup_rule+ "}"
setup_rule: "place" ":" NAME "owned_by" NAME "on" "rows" INT ".." INT "playable_cells"
```

For example:

```text
setup {
    place: Man owned_by White on rows 6..8 playable_cells
    place: Man owned_by Black on rows 1..3 playable_cells
}
```

The first `NAME` identifies the piece, the second identifies its owner, and the
two `INT` values form an inclusive row range. The grammar checks only this
shape; reference validity, row ordering, board bounds, and overlapping setup
rules belong to semantic validation.

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

Directional players and movement rules use the same pattern:

```lark
forward_direction: "up"   -> forward_up
                 | "down" -> forward_down

movement_direction: "diagonal" "forward" -> diagonal_forward
                  | "diagonal" "any"     -> diagonal_any

destination_condition: "empty" -> empty_destination
```

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
- `INT` represents dimensions, alignment lengths, movement distances, and
  setup row bounds;
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

The grammar supports Tic-Tac-Toe plus the directional-player, basic
non-capturing movement, and initial-setup declarations required by Checkers.
It does not yet support:

- capture rules;
- promotion;
- gravity;
- placement by column;
- complete Checkers or Connect Four definitions.

## Extension workflow

Every grammar extension should:

1. begin with a representative `.game` example;
2. add a valid parser test;
3. add at least one invalid test;
4. update the grammar;
5. update AST nodes and transformation when necessary;
6. inspect the resulting parse tree;
7. update this document.
