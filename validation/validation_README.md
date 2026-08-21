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
- pieces declaring neither placement nor movement;
- pieces declaring both placement and movement;
- non-positive movement distances;
- owners missing a forward direction required by `diagonal forward`;
- non-positive alignment lengths;
- alignments that do not fit the board in their specified direction.

Row alignments are limited by the number of columns, column alignments by the
number of rows, and diagonal alignments by the smaller board dimension.

Piece actions are exclusive: each piece must declare exactly one of `place` or
`move`. A `diagonal any` rule does not depend on player orientation, while every
declared owner of a `diagonal forward` rule must provide `forward: up` or
`forward: down`.

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

Movement validation uses these stable diagnostics:

| Code | Path | Meaning |
| --- | --- | --- |
| `missing_piece_action` | `pieces.NAME.action` | Neither `place` nor `move` is declared |
| `conflicting_piece_actions` | `pieces.NAME.action` | Both `place` and `move` are declared |
| `invalid_movement_distance` | `pieces.NAME.movement.distance` | Distance is not positive |
| `missing_forward_direction` | `players.NAME.forward` | A forward-moving owner has no orientation |

## Architectural boundary

The parser verifies syntax and constructs the AST. This package validates
relationships and domain constraints within that AST. The engine receives
validated definitions and manages runtime state, turns, and supported move
execution. Geometric movement execution remains a separate engine concern.

Validation is currently invoked explicitly; `GameParser` does not run it
automatically.

## Testing

Run the focused tests from the project root:

```bash
python -m pytest tests/test_semantic_validator.py -v
```

The nine focused tests cover valid Tic-Tac-Toe and movement definitions,
cumulative diagnostics, stable codes and paths, piece-action exclusivity,
movement distances, required player orientation, and
`SemanticValidationError` behaviour. The complete project suite contains 95
tests.

## Current limitations

The rules cover Tic-Tac-Toe and the current directional, non-capturing movement
subset. Capture, promotion, initial setup, Checkers end conditions, and Connect
Four gravity will require additional semantic checks.
