# Piecewise Grammar

This directory contains the formal grammar used to parse Piecewise `.game`
files.

The grammar is written for [Lark](https://github.com/lark-parser/lark), a Python
parsing library based on EBNF-style grammar definitions.

## Parsing pipeline

```text
.game file -> Lark grammar -> Parse tree -> AST transformer -> Game engine
```

At the current stage, Lark validates the syntax of a game definition and
produces a parse tree. Transformation into domain objects and semantic
validation will be implemented separately.

## Files

```text
grammar/
├── piecewise.lark  # Formal grammar
└── README.md       # Grammar documentation
```

## Entry point

Parsing starts from the `start` rule:

```lark
start: game_definition
```

`game_definition` describes the required top-level structure of a Piecewise
game:

```lark
game_definition: "game" NAME "{" board_block players_block piece_block+ win_condition_block "}"
```

A game therefore contains, in order:

1. one board block;
2. one players block;
3. one or more piece blocks;
4. one win-condition block.

## Main rules

### Board

`board_block` defines the board and contains one or more board properties:

```lark
board_block: "board" "{" board_property+ "}"
```

The initial grammar supports:

- board dimensions through `size`;
- playable-cell selection through `playable_cells`.

Example:

```text
board {
    size: 3x3
    playable_cells: all
}
```

### Players

`players_block` contains one or more player declarations followed by the turn
order:

```text
players {
    player X
    player O
    turn_order: X, O
}
```

The grammar validates the structure of this block. It does not yet verify that
every player in `turn_order` was previously declared; that is a semantic
validation responsibility.

### Pieces

Each `piece_block` defines a named piece type and one or more properties:

```text
piece Mark {
    owner: X, O
    place: any_empty_cell
}
```

The initial grammar supports:

- one or more owners;
- placement on any empty cell.

Movement, capture, promotion, setup, and gravity are not supported by the first
grammar increment.

### Win conditions

The `win_condition_block` contains one or more end-game conditions:

```text
win_condition {
    align: 3 same_row -> win
    align: 3 same_col -> win
    align: 3 diagonal -> win
    board_full: no_winner -> draw
}
```

The initial grammar supports horizontal, vertical, and diagonal alignments, plus
a draw caused by a full board.

## Lark notation used

| Notation | Meaning |
| --- | --- |
| `"text"` | Literal text required in the input |
| `rule` | Reference to another grammar rule |
| `A \| B` | Either `A` or `B` |
| `rule+` | One or more occurrences |
| `rule*` | Zero or more occurrences |
| `rule?` | Zero or one occurrence |
| `?rule:` | Inline the rule when possible to simplify the parse tree |

## Tokens

The grammar imports common tokens provided by Lark:

```lark
%import common.CNAME -> NAME
%import common.INT
%import common.WS
%ignore WS
```

- `NAME` represents identifiers such as `TicTacToe`, `Mark`, or `X`;
- `INT` represents integer values such as board dimensions or alignment lengths;
- `WS` represents whitespace;
- `%ignore WS` makes spaces, tabs, and line breaks insignificant.

Because whitespace is ignored, indentation improves readability but has no
syntactic meaning.

## Running a manual test

Install Lark:

```bash
python -m pip install lark
```

From the project root, load the grammar and parse a game:

```python
from pathlib import Path

from lark import Lark

grammar_text = Path("grammar/piecewise.lark").read_text(encoding="utf-8")
game_text = Path("games/tictactoe.game").read_text(encoding="utf-8")

parser = Lark(grammar_text, parser="lalr", start="start")
tree = parser.parse(game_text)

print(tree.pretty())
```

A valid file produces a parse tree. Invalid syntax causes Lark to raise an
`UnexpectedCharacters` or `UnexpectedToken` exception.

## Syntax and semantic validation

The grammar is responsible only for syntax. For example, it can verify that an
`owner` property contains a list of names, but it cannot determine whether those
names refer to declared players.

Semantic validation will be performed after parsing. It will check constraints
such as:

- referenced players and pieces exist;
- player and piece names are unique;
- the turn order contains the declared players;
- board dimensions and alignment lengths are valid;
- required properties occur exactly once;
- a game defines at least one reachable end condition.

## Current limitations

The first grammar increment parses Tic-Tac-Toe only. The following documented
DSL features will be added incrementally:

- directional players;
- piece movement and capture;
- piece promotion;
- initial setup;
- board gravity;
- placement by column;
- Checkers and Connect Four definitions.

Keeping these features out of the first increment makes the parser easier to
test and allows each extension to be introduced with its own automated tests.

## Extension workflow

When extending the grammar:

1. add or update a `.game` example;
2. add a parser test for valid syntax;
3. add at least one test for invalid syntax;
4. update `piecewise.lark`;
5. inspect the resulting parse tree;
6. update this document if the grammar structure or supported syntax changes.

