# Piecewise Semantic Validation

This package validates the semantic consistency of a parsed Piecewise
`GameDefinition`.

Semantic validation runs after syntax parsing and AST transformation. It checks
domain constraints that do not belong in the Lark grammar.

## Pipeline

```text
.game source
    -> Lark parser
    -> Parse tree
    -> AST transformer
    -> GameDefinition
    -> SemanticValidator
    -> Validated GameDefinition
```

The package does not parse source text and does not execute games.

## Files

```text
validation/
├── __init__.py
├── errors.py
├── semantic_validator.py
└── README.md
```

## Public API

```python
from parser.game_parser import GameParser
from validation import SemanticValidator

game = GameParser().parse_game_file("games/tictactoe.game")
validator = SemanticValidator()
issues = validator.validate(game)
```

`validate()` returns an immutable tuple containing every detected issue. Use
`validate_or_raise()` when invalid input must stop processing:

```python
validator.validate_or_raise(game)
```

This raises `SemanticValidationError`, whose `issues` attribute contains all
the detected problems.

## Current rules

The validator detects:

- non-positive board rows or columns;
- duplicate player and piece declarations;
- duplicate players in the turn order;
- undeclared players in the turn order;
- declared players missing from the turn order;
- undeclared piece owners;
- non-positive alignment lengths;
- alignments that do not fit the board in their specified direction.

Row alignments are limited by the number of columns, column alignments by the
number of rows, and diagonal alignments by the smaller board dimension.

## Diagnostics

Each problem is an immutable `ValidationIssue` with:

- a stable machine-readable `code`;
- a human-readable `message`;
- an optional AST `path`.

For example:

```text
[unknown_piece_owner] pieces.Mark.owners: Player 'Ghost' owning piece 'Mark' is not declared.
```

Validation is cumulative: independent problems are collected in one pass.
Constructing `SemanticValidationError` without issues raises `ValueError`.

## Architectural boundary

The parser verifies syntax and constructs the AST. This package validates
relationships and domain constraints within that AST. The future engine will
receive validated definitions and manage runtime state, legal moves, turns, and
end-condition evaluation.

Validation is currently invoked explicitly; `GameParser` does not run it
automatically.

## Testing

Run the focused tests from the project root:

```bash
python -m pytest tests/test_semantic_validator.py -v
```

They cover valid Tic-Tac-Toe, cumulative diagnostics, stable codes, and
`SemanticValidationError` behaviour.

## Current limitations

The rules cover the currently implemented Tic-Tac-Toe AST. Future Checkers and
Connect Four constructs will require additional semantic checks.
