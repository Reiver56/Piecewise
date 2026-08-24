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
- capture rules declared without a movement rule;
- non-positive capture distances;
- owners missing a forward direction required by a `diagonal forward` capture;
- promotion rules declared without a movement rule;
- promotion targets that are undeclared or equal to the source piece;
- promotion targets that do not support every source-piece owner;
- owners missing a forward direction required by a `back_rank` promotion;
- setup rules referencing undeclared pieces or players;
- setup owners not allowed by their referenced piece;
- setup row ranges that are not ordered and one-based;
- setup row ranges extending beyond the board;
- setup rules whose playable row ranges overlap;
- unsupported targets in Checkers player-state end conditions;
- `opponent` targets used by games that do not declare exactly two players;
- non-positive alignment lengths;
- alignments that do not fit the board in their specified direction.

Row alignments are limited by the number of columns, column alignments by the
number of rows, and diagonal alignments by the smaller board dimension.

Piece actions are exclusive: each piece must declare exactly one of `place` or
`move`. A `diagonal any` rule does not depend on player orientation, while every
declared owner of a `diagonal forward` rule must provide `forward: up` or
`forward: down`.

A capture is an optional capability of a movement piece, not a standalone
piece action. Therefore it requires a normal movement rule. Capture distances
must be positive, and `diagonal forward` captures use the same player
orientation requirement as forward movement. When both rules require forward
orientation, the validator avoids reporting the same missing direction twice.

A promotion is an optional capability of a movement piece. Its target must be
a different declared piece, and the target must support every owner of the
source piece. A `back_rank` condition depends on player orientation, so every
declared owner must provide `forward: up` or `forward: down`. The shared
`missing_forward_direction` diagnostic is emitted only once when movement,
capture, and promotion depend on the same missing orientation.

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

Capture validation adds these diagnostics while reusing
`missing_forward_direction` for player orientation:

| Code | Path | Meaning |
| --- | --- | --- |
| `capture_requires_movement` | `pieces.NAME.capture` | Capture is declared without movement |
| `invalid_capture_distance` | `pieces.NAME.capture.distance` | Distance is not positive |

Promotion validation adds these diagnostics while reusing
`missing_forward_direction` for back-rank orientation:

| Code | Path | Meaning |
| --- | --- | --- |
| `promotion_requires_movement` | `pieces.NAME.promotion` | Promotion is declared without movement |
| `unknown_promotion_target` | `pieces.NAME.promotion.target_piece_name` | Target piece is undeclared |
| `self_promotion_target` | `pieces.NAME.promotion.target_piece_name` | Source and target piece are identical |
| `incompatible_promotion_owners` | `pieces.NAME.promotion.target_piece_name` | Target does not support every source owner |

Setup validation uses indexed paths so diagnostics identify the exact rule:

| Code | Path | Meaning |
| --- | --- | --- |
| `unknown_setup_piece` | `setup[N].piece_name` | Referenced piece is undeclared |
| `unknown_setup_owner` | `setup[N].owner` | Referenced player is undeclared |
| `setup_owner_not_allowed` | `setup[N].owner` | Piece cannot belong to that player |
| `invalid_setup_row_range` | `setup[N].rows` | Range is not ordered and one-based |
| `setup_rows_out_of_bounds` | `setup[N].rows` | Range exceeds the board |
| `overlapping_setup_rules` | `setup[N].rows` | Range overlaps an earlier setup rule |

Checkers player-state end-condition validation uses indexed condition paths:

| Code | Path | Meaning |
| --- | --- | --- |
| `unsupported_player_target` | `win_conditions[N].target` | Target is not supported by the current DSL subset |
| `ambiguous_opponent_target` | `win_conditions[N].target` | `opponent` cannot identify one player because the game does not declare exactly two players |

## Architectural boundary

The parser verifies syntax and constructs the AST. This package validates
relationships and domain constraints within that AST. The engine receives
validated definitions and manages runtime state, turns, and supported move
execution. Geometric movement execution remains a separate engine concern.
Removing an enemy piece and moving the capturing piece are likewise runtime
engine responsibilities, not semantic-validation responsibilities.

Validation is currently invoked explicitly; `GameParser` does not run it
automatically.

## Testing

Run the focused tests from the project root:

```bash
python -m pytest tests/test_semantic_validator.py -v
```

The 30 focused tests cover valid Tic-Tac-Toe and Checkers definitions, movement,
capture, promotion, setup, and player-state end-condition rules, cumulative
diagnostics, stable codes and paths, piece-action exclusivity, movement and
capture distances, required player orientation, capture-to-movement and
promotion-to-movement dependencies, promotion targets and ownership
compatibility, setup references, ownership, row ranges and overlaps, supported
player targets, unambiguous `opponent` resolution, and
`SemanticValidationError` behaviour. The complete project suite contains 175
tests.

## Current limitations

The rules cover Tic-Tac-Toe and the current directional movement, capture,
promotion, initial-setup, and Checkers player-state end-condition subsets.
Supported single-jump captures and back-rank promotion are executed by
`MoveExecutor`; multiple captures, mandatory capture, runtime evaluation of
Checkers end conditions, and Connect Four gravity still require future
increments. Valid setup rules are applied to runtime state by
`GameInitializer`.
