# Piecewise Game Engine

The `engine` package turns a validated `GameDefinition` into immutable runtime
snapshots, represents placement and relocation requests, executes supported
placement, ordinary relocation, capture, and back-rank promotion moves,
evaluates terminal conditions, manages a complete session, and renders the
board as plain text.

## Files

```text
engine/
├── __init__.py             # Public engine API
├── board_renderer.py       # Plain-text board rendering
├── condition_evaluator.py  # Win and draw evaluation
├── errors.py               # Engine-specific exceptions
├── game_initializer.py     # GameDefinition to initial GameState
├── game_session.py         # Current-session orchestration
├── game_state.py           # Immutable runtime domain model
├── legal_move_generator.py # Current-player legal move discovery
├── move.py                 # Immutable placement or relocation request
└── move_executor.py        # Move validation and execution
```

## Runtime model

`game_state.py` defines:

- `Coordinate`: a zero-based row and column;
- `PlacedPiece`: a named piece, its owner, and its coordinate;
- `GameStatus`: `ongoing`, `won`, or `drawn`;
- `GameState`: an immutable snapshot of a running game.

`GameState` enforces positive board dimensions and turn numbers, valid winner
and status combinations, in-bounds pieces, and unique occupied coordinates. Its
optional `forced_capture_source` records an unfinished capture chain. When set,
the coordinate must contain a piece owned by `current_player`.

## Move requests

`Move` represents both placement and relocation requests.

A placement specifies only its destination:

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
also exposed through the `destination` property. The `is_placement` and
`is_relocation` properties identify the request type.

A move cannot use the same coordinate as both its source and destination.
`Move` instances remain immutable.

## Generate legal moves

`LegalMoveGenerator` inspects an immutable state and returns an ordered tuple of
legal `Move` requests for `state.current_player`:

```python
from engine import LegalMoveGenerator

moves = LegalMoveGenerator(game).generate(state)
```

For ordinary movement it supports `DIAGONAL_FORWARD` using the owner's
orientation and `DIAGONAL_ANY` in both vertical directions. It rejects
out-of-bounds, non-playable, and occupied destinations. For captures it uses
the declared capture distance, requires an empty landing cell, and includes the
move only when the intermediate coordinate contains an enemy piece.

Generation is deterministic and does not mutate the supplied state. Captures
have global precedence: when any current-player piece can capture, the result
contains only captures and suppresses ordinary moves from every owned piece.
When `state.forced_capture_source` is set, only moves originating from that
piece are generated. Returning an empty tuple is the engine primitive used by
`ConditionEvaluator` for `no_moves_left`.

## Initialize setup pieces

`GameInitializer` validates the complete `GameDefinition` before creating the
first `GameState`. Invalid setup rules therefore raise
`GameInitializationError` with the semantic diagnostics.

For a valid setup, each inclusive one-based DSL row range is converted to
zero-based runtime rows. The initializer creates `PlacedPiece` instances in
rule, row, and column order and keeps only the requested playable cells:

- `ALL` accepts every cell;
- `DARK` accepts coordinates whose row-column sum is odd;
- `LIGHT` accepts coordinates whose row-column sum is even.

An absent setup produces the empty piece tuple used by Tic-Tac-Toe. The two
standard three-row Checkers ranges on an 8x8 dark-cell board produce 12 pieces
per player and 24 pieces in total.

## Initialize and play

`GameSession` is the high-level engine API. It validates and initializes the
game, exposes the current snapshot through `state`, and replaces that snapshot
after each successful move:

```python
from engine import Coordinate, GameSession, Move
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
session = GameSession(game)

next_state = session.play(
    Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=1, column=1),
    )
)
```

Previous `GameState` instances remain unchanged. If a move raises
`InvalidMoveError`, the session retains its current snapshot.

`MoveExecutor` rejects moves when the game has ended, when the wrong player is
acting, when a coordinate is outside or unavailable, when a piece is unknown
or unowned, or when a destination is occupied. It dispatches placement and
relocation requests according to the action supported by the piece definition.
A successful move advances the turn and invokes `ConditionEvaluator`.

## Execute a relocation

For a relocation, `MoveExecutor` verifies that:

- the source is inside the board and playable;
- the source contains the requested piece;
- the current player owns that runtime piece;
- the destination is inside the board, playable, and empty;
- source and destination match the declared diagonal distance;
- `diagonal forward` follows the owner's `up` or `down` orientation;
- `diagonal any` may move in either vertical direction.

The source `PlacedPiece` is replaced immutably with a copy at the destination.
All other pieces and the previous `GameState` remain unchanged.

## Execute a capture

A capture uses the same `Move` request as any relocation. `MoveExecutor`
recognizes it when the source-to-destination displacement matches the piece's
`capture.distance` rather than its ordinary `movement.distance`.

For a valid capture, the executor:

- validates a diagonal displacement of the declared distance;
- applies the owner's orientation to `diagonal forward`;
- permits either vertical direction for `diagonal any`;
- calculates the intermediate coordinate between source and destination;
- requires that coordinate to contain an enemy piece;
- rejects an empty intermediate cell or a piece owned by the active player;
- moves the active piece and removes the enemy in a new immutable tuple;
- advances the turn without modifying the previous `GameState`.

The same logic supports players oriented both `up` and `down`. Each atomic move
captures exactly one enemy. If the generator detects an available capture,
`MoveExecutor` rejects an otherwise valid ordinary relocation with
`InvalidMoveError`; the required capture remains executable.

If the moved piece can capture again, `MoveExecutor` returns a continuation
state that retains the current player and turn number and stores the landing
coordinate in `forced_capture_source`. Subsequent requests must use that same
piece. When no follow-up capture exists, the field returns to `None`, the turn
advances once, and terminal conditions are evaluated.

## Execute a promotion

After every successful relocation, `MoveExecutor` checks the optional
`PromotionRule` of the moved piece. For `BACK_RANK`, the destination must be:

- row `0` when the owner declares `forward: up`;
- row `state.rows - 1` when the owner declares `forward: down`.

If the destination matches, the moved `PlacedPiece` is immutably replaced with
a copy whose `piece_name` is the declared promotion target. Its owner and
destination remain unchanged. The same post-relocation step runs after a
capture, so the intermediate enemy is removed before the surviving piece is
promoted. A move ending before the back rank preserves the original piece
type, and the previous `GameState` remains unchanged. Promotion is immediate:
if the promoted `King` has another capture, it continues the current chain with
its `DIAGONAL_ANY` capture rule.

## End conditions

`ConditionEvaluator` supports consecutive same-owner alignments across rows,
columns, and both diagonal directions, full-board draws, and Checkers
`no_pieces_left` victories. For the latter, it resolves the single declared
opponent of the player who made the last move and checks whether that owner has
any remaining pieces. For `no_moves_left`, it generates the next player's legal
ordinary and capture moves and detects an empty result. Capture continuation
states remain ongoing; terminal evaluation runs after the chain finishes. In
both cases the winner is the player who made the last move. Only playable cells
count toward a full board, and a win takes precedence when the last move also
fills the board.

## Render a board

`BoardRenderer` creates a terminal-friendly view of any rectangular
`GameState`:

```python
from engine import BoardRenderer

print(BoardRenderer(game).render(session.state))
```

```text
    0   1   2
0   . | . | .
1   . | X | .
2   . | . | .
```

The renderer uses:

- `.` for an empty playable cell;
- `#` for a non-playable cell;
- the owner name for a placed piece.

Placed pieces take visual precedence over cell markers. Rendering is read-only
and does not modify the supplied state.

## Architectural boundary

The engine consumes the typed AST and has no dependency on Lark or concrete
DSL syntax. Terminal input and output belong to the separate `cli` package.
The executor supports `ANY_EMPTY_CELL` placement plus validated ordinary and
capturing `DIAGONAL_FORWARD` and `DIAGONAL_ANY` relocation, followed by
validated `BACK_RANK` promotion. `LegalMoveGenerator` discovers the supported
ordinary and capture moves without applying them and gives captures
global precedence over ordinary moves. `GameState` and `MoveExecutor` coordinate
forced chained captures without making the executor stateful. The separate CLI
now converts four-coordinate user input into relocation requests without adding
terminal concerns to the engine. Gravity remains a future increment. Movement,
capture, promotion, setup-rule consistency, and Checkers
player-state targets are validated before the engine boundary by
`SemanticValidator`.

## Testing

Run all engine and renderer tests from the project root:

```bash
python -m pytest \
  tests/test_game_state.py \
  tests/test_game_initializer.py \
  tests/test_game_session.py \
  tests/test_move.py \
  tests/test_legal_move_generator.py \
  tests/test_condition_evaluator.py \
  tests/test_move_executor.py \
  tests/test_checkers_scenarios.py \
  tests/test_board_renderer.py -v
```

These modules contain 133 engine-focused and end-to-end scenario tests. The
complete project suite contains 204 tests.
