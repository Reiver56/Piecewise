# Piecewise Parser

This directory contains the syntactic parser for Piecewise `.game` files.

The parser loads the formal grammar from `grammar/piecewise.lark`, delegates
syntax analysis to Lark, and returns a parse tree. It does not create game
objects or validate domain constraints.

## Responsibilities

The parser is responsible for:

- loading the Piecewise grammar;
- parsing game definitions from strings;
- parsing `.game` files;
- rejecting syntactically invalid input;
- preserving source positions for later error reporting.

The parser is not responsible for:

- checking whether referenced players or pieces exist;
- validating board dimensions or game rules;
- transforming the parse tree into the Piecewise AST;
- executing a game;
- managing turns or board state.

These responsibilities belong to later semantic-validation, transformation, and
engine components.

## Files

```text
parser/
├── __init__.py
├── game_parser.py
└── README.md
```

## Public API

The parser is exposed through the `GameParser` class:

```python
from parser.game_parser import GameParser

parser = GameParser()
```

By default, the class loads:

```text
grammar/piecewise.lark
```

A different grammar can be supplied for testing or experimentation:

```python
parser = GameParser("path/to/alternative.lark")
```

### Parsing a string

Use `parse` when the game definition is already available as text:

```python
source = """
game Example {
    ...
}
"""

tree = parser.parse(source)
```

### Parsing a file

Use `parse_file` to read and parse a `.game` file:

```python
tree = parser.parse_file("games/tictactoe.game")
```

The method accepts either a string path or a `pathlib.Path`.

Files without the `.game` extension are rejected with `ValueError`.

## Returned value

Both parsing methods return a Lark `Tree`:

```python
tree = parser.parse_file("games/tictactoe.game")
print(tree.pretty())
```

Example output:

```text
start
  game_definition
    TicTacToe
    board_block
    players_block
    piece_block
    win_condition_block
```

This tree still represents the concrete syntax of the source file. A separate
transformer will later convert it into Piecewise domain objects.

## Error handling

The parser deliberately preserves Lark syntax exceptions instead of replacing
them with generic errors.

Typical exceptions include:

- `UnexpectedCharacters`: the source contains a character that is not valid at
  the current position;
- `UnexpectedToken`: a valid token occurs where the grammar does not allow it;
- `UnexpectedEOF`: the file ends before a grammar rule is complete.

Because the Lark parser is created with `propagate_positions=True`, parse-tree
nodes retain line and column information. This metadata can later be used to
produce user-friendly Piecewise diagnostics.

Filesystem errors such as a missing grammar or game file are also allowed to
propagate to the caller.

## Design decisions

### LALR parser

The implementation uses:

```python
Lark(grammar_text, parser="lalr", start="start")
```

LALR is suitable for the deterministic structure of the Piecewise DSL and
provides efficient parsing with useful syntax errors.

### Parser instance reuse

The grammar is loaded when `GameParser` is created. The resulting Lark parser is
then reused by every call to `parse` or `parse_file`, avoiding repeated grammar
construction.

### Path resolution

The default grammar path is calculated relative to `game_parser.py`, rather than
relative to the current terminal directory. This allows the parser to locate the
grammar consistently when Piecewise is launched from different locations.

### Separation of concerns

Syntactic parsing and semantic validation are intentionally separate.

For example, this property can be syntactically valid:

```text
owner: UnknownPlayer
```

The grammar can confirm that `UnknownPlayer` is a valid identifier, but only the
semantic validator can determine whether that player was declared.

## Running the tests

Install the development dependencies:

```bash
python -m pip install lark pytest
```

From the project root, run:

```bash
python -m pytest -v
```

The initial parser tests verify that:

- a valid Tic-Tac-Toe definition is parsed;
- an incomplete definition is rejected;
- a file with the wrong extension is rejected.

## Current limitations

The parser currently depends on the first grammar increment, which supports
Tic-Tac-Toe syntax only.

The following features are not parsed yet:

- player movement directions;
- piece movement and capture;
- promotion;
- initial setup;
- gravity;
- placement by column;
- Checkers and Connect Four definitions.

## Next steps

The next parser-related increments are:

1. transform the parse tree into an AST;
2. add semantic validation;
3. improve user-facing error messages;
4. extend the grammar and parser tests for Checkers;
5. extend the grammar and parser tests for Connect Four.

