# Piecewise Tests

Piecewise uses pytest for automated unit and integration testing. The same suite
runs locally and in GitHub Actions for pull requests targeting `main`.

## Files

```text
tests/
├── __init__.py
├── test_parser.py
├── test_ast_transformer.py
├── test_board_renderer.py
├── test_game_cli.py
├── test_semantic_validator.py
├── test_condition_evaluator.py
├── test_game_initializer.py
├── test_game_session.py
├── test_game_state.py
├── test_legal_move_generator.py
├── test_move.py
├── test_move_executor.py
└── tests_README.md
```

## Run the tests

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the complete suite:

```bash
python -m pytest -v
```

Run one module:

```bash
python -m pytest tests/test_parser.py -v
```

Run one test:

```bash
python -m pytest tests/test_ast_transformer.py::test_ast_is_immutable -v
```

Commands should be executed from the project root.

## Current coverage

The suite currently contains 179 tests.

### Parser tests

`test_parse_valid_tictactoe`

- parses `games/tictactoe.game`;
- verifies that the root node is `start`;
- verifies that the parse tree is not empty.

`test_parse_checkers_end_condition_syntax`

- parses the complete `games/checkers.game` source;
- verifies distinct `no_pieces_left_condition` and
  `no_moves_left_condition` nodes;
- verifies two typed `opponent_target` aliases.

`test_reject_invalid_end_condition_target`

- replaces `opponent` with unsupported `self`;
- verifies that the grammar raises `UnexpectedInput`.

`test_reject_incomplete_game`

- supplies an incomplete definition;
- expects a Lark `UnexpectedInput` exception.

`test_reject_wrong_file_extension`

- creates a temporary `.txt` file;
- verifies that `GameParser.parse_file` raises `ValueError`.

`test_parse_movement_rule_syntax`

- parses directional players and two diagonal movement forms;
- verifies the corresponding parse-tree aliases.

The two parameterized `test_reject_invalid_movement_syntax` cases verify that
unsupported player-forward and movement directions raise `UnexpectedInput`.

`test_reject_invalid_capture_condition`

- adds a capture declaration using the unsupported `friend` condition;
- verifies that the grammar raises `UnexpectedInput` because only `enemy` is
  accepted.

`test_reject_invalid_promotion_condition`

- adds `promote: center_rank -> King` to an otherwise valid definition;
- verifies that `UnexpectedInput` is raised because only `back_rank` is
  supported.

### AST tests

`test_transform_tictactoe_definition`

- exercises the complete file-to-AST pipeline;
- verifies the game, board, players, turn order, and piece;
- checks typed enum values.

`test_transform_win_conditions`

- verifies the three alignment conditions;
- verifies the full-board draw condition;
- checks the complete immutable tuple of typed conditions.

`test_transform_checkers_end_conditions`

- transforms the real Checkers file through the complete parser pipeline;
- verifies `NoPiecesLeftCondition` and `NoMovesLeftCondition`;
- verifies `PlayerTarget.OPPONENT` and `Outcome.WIN`.

`test_checkers_end_condition_is_immutable`

- runs once for each new condition type;
- verifies that frozen AST nodes reject target reassignment.

`test_ast_is_immutable`

- attempts to modify a parsed `GameDefinition`;
- verifies that the frozen dataclass raises `FrozenInstanceError`.

`test_transform_player_forward_directions`

- transforms `up` and `down` into typed `ForwardDirection` values;
- preserves the declared turn order.

`test_transform_piece_movement_rules`

- transforms `diagonal forward` and `diagonal any` rules;
- verifies distance and destination-condition values;
- verifies that movement-only pieces have no placement rule.

`test_movement_rule_is_immutable`

- verifies that a transformed `MovementRule` cannot be modified.

`test_transform_piece_capture_rules`

- transforms `diagonal forward` and `diagonal any` capture declarations;
- verifies typed directions, distance, and `CaptureCondition.ENEMY`.

`test_piece_without_capture_has_no_capture`

- verifies backward compatibility through the optional
  `PieceDefinition.capture` field.

`test_capture_rule_is_immutable`

- verifies that a transformed `CaptureRule` cannot be modified.

`test_transform_piece_promotion_rule`

- transforms `promote: back_rank -> King` into a typed `PromotionRule`;
- verifies `PromotionCondition.BACK_RANK`, the target name, and optional absence
  on a piece without promotion.

`test_promotion_rule_is_immutable`

- verifies that the promotion target cannot be modified after transformation.

`test_transform_setup_rules`

- transforms multiple initial-placement declarations into ordered `SetupRule`
  objects;
- verifies piece names, owners, inclusive one-based row ranges, and the
  playable-cells-only marker.

`test_game_without_setup_has_empty_setup`

- verifies backward compatibility through the empty `GameDefinition.setup`
  tuple.

`test_setup_rule_is_immutable`

- verifies that a transformed `SetupRule` cannot be modified.

The Tic-Tac-Toe transformation test also verifies that its players have no
forward direction and its placement piece has no movement rule.

### Semantic-validation tests

The 30 cases in `test_semantic_validator.py` verify:

- valid Tic-Tac-Toe and movement-rule definitions;
- acceptance of valid definitions through `validate_or_raise()`;
- cumulative diagnostics with stable codes and paths;
- complete issue exposure through `SemanticValidationError`;
- rejection of pieces with neither placement nor movement;
- rejection of pieces declaring both placement and movement;
- rejection of non-positive movement distances;
- the requirement that every owner of a `diagonal forward` piece declares a
  forward direction;
- acceptance of valid capture rules;
- rejection of non-positive capture distances;
- rejection of capture rules without a normal movement rule;
- the forward-direction requirement introduced by `diagonal forward` capture;
- cumulative reporting of independent capture issues;
- acceptance of a valid `back_rank` promotion;
- rejection of undeclared and self-referencing promotion targets;
- rejection of promotion rules without movement;
- compatibility between source-piece and target-piece owners;
- the forward-direction requirement introduced by `back_rank` promotion;
- acceptance of valid initial setup rules;
- rejection of unknown setup pieces and owners;
- rejection of setup owners not allowed for their piece;
- rejection of non-one-based, reversed, and out-of-bounds row ranges;
- rejection of overlapping setup ranges;
- acceptance of the two player-state end conditions in the real Checkers
  definition;
- indexed `ambiguous_opponent_target` diagnostics for both conditions when
  `opponent` cannot identify one of exactly two players;
- rejection of unsupported targets in AST objects constructed directly in
  Python.

`test_valid_tictactoe_has_no_semantic_issues`

- validates the parsed Tic-Tac-Toe definition;
- verifies that no issues are returned.

`test_validate_or_raise_accepts_valid_game`

- verifies that a valid definition is accepted without an exception.

`test_collects_multiple_semantic_issues`

- builds an invalid AST from the valid fixture;
- verifies cumulative diagnostics and stable issue codes.

`test_validate_or_raise_contains_all_issues`

- verifies that `SemanticValidationError` exposes every collected issue;
- checks the formatted error message.

The movement-rule cases exercise the diagnostic codes
`missing_piece_action`, `conflicting_piece_actions`,
`invalid_movement_distance`, and `missing_forward_direction`.

The capture-rule cases exercise `capture_requires_movement`,
`invalid_capture_distance`, and the shared `missing_forward_direction`
diagnostic. They also isolate forward capture from ordinary movement and verify
that multiple capture problems are collected in one validation pass.

The promotion-rule cases exercise `promotion_requires_movement`,
`unknown_promotion_target`, `self_promotion_target`,
`incompatible_promotion_owners`, and the shared
`missing_forward_direction` diagnostic. They isolate back-rank orientation from
movement and capture so the promotion-specific dependency is tested directly.

### Game-initializer tests

The nine tests in `test_game_initializer.py` verify that:

- initialization creates an empty, ongoing state;
- the first player in `turn_order` becomes the current player;
- semantically invalid definitions are rejected;
- `GameInitializationError` includes validation details;
- one-based setup rows become zero-based runtime coordinates;
- `ALL`, `DARK`, and `LIGHT` cell selection is respected;
- multiple setup rules create the expected 24-piece initial position;
- invalid setup diagnostics cross the engine boundary as
  `GameInitializationError`.

### Game-state tests

The 18 cases in `test_game_state.py` verify:

- zero-based coordinates and rejection of negative indices;
- immutable runtime state and placed-piece representation;
- positive board dimensions and turn numbers starting at one;
- the winner and game status relationship;
- board-boundary checks for placed pieces;
- rejection of overlapping pieces.

### Game-session tests

The seven cases in `test_game_session.py` verify:

- automatic initialization of the current game state;
- state updates and return values after successful moves;
- preservation of previous immutable snapshots;
- sequential application of multiple moves;
- transition to a winning state during a complete session;
- preservation of the current state after an invalid move;
- rejection of further moves after the game has ended.

### Move tests

The seven cases in `test_move.py` verify:

- storage of the player, piece name, and destination coordinate;
- rejection of an empty player or piece name;
- immutability of move requests;
- identification of placement requests without a source;
- representation of relocation requests with source and destination;
- rejection of equal source and destination coordinates.

### Move-executor tests

The 43 cases in `test_move_executor.py` verify:

- piece placement, turn-number advancement, and player rotation;
- creation of a new state without modifying the previous snapshot;
- rejection of moves after a game has ended;
- enforcement of the current player's turn;
- board-boundary and playable-cell checks;
- rejection of unknown or unowned piece types;
- rejection of occupied destination cells;
- automatic transition to a won state after a winning placement;
- automatic transition to a drawn state after a board-filling placement;
- forward relocation for players oriented `up` and `down`;
- unrestricted vertical direction for `diagonal any`;
- immutable replacement of the source piece at the destination;
- rejection of missing, out-of-bounds, opponent-owned, or wrongly typed source
  pieces;
- enforcement of diagonal geometry and declared distance;
- rejection of backward `diagonal forward` movement;
- rejection of occupied relocation destinations;
- rejection of placement requests for movement-only pieces and relocation
  requests for placement-only pieces;
- runtime protection when a forward direction is unavailable;
- forward captures for players oriented both `up` and `down`;
- backward captures for `diagonal any` and their rejection for
  `diagonal forward`;
- rejection of an empty intermediate cell or a piece owned by the active
  player;
- immutable enemy removal and preservation of the previous snapshot;
- normal turn rotation after a successful capture;
- back-rank promotion for owners oriented both `up` and `down`;
- preservation of the source type before reaching the back rank;
- promotion after a capture and removal of the intermediate enemy;
- immutable preservation of the pre-promotion snapshot;
- integration between a final capture and the `no_pieces_left` victory;
- integration between turn rotation, legal-move generation, and a
  `no_moves_left` victory.

### Legal-move-generator tests

The eight cases in `test_legal_move_generator.py` verify:

- one or both forward diagonal moves for a `Man`;
- deterministic left-before-right destination ordering;
- exclusion of opponent pieces as move sources;
- rejection of occupied, non-playable, and out-of-bounds destinations through
  the covered edge and blocking scenarios;
- movement in both vertical directions for `diagonal any`;
- forward single captures over an enemy piece;
- backward single captures for a `King` using `diagonal any`;
- rejection of captures over a piece with the same owner;
- an empty immutable tuple when the current player has no legal moves.

### Condition-evaluator tests

The 15 cases in `test_condition_evaluator.py` verify:

- row and column victories;
- victories across both diagonal directions;
- rejection of mixed-owner and non-consecutive alignments;
- full-board draw detection;
- victory precedence when the last move also fills the board;
- board-full evaluation using only playable cells;
- continued play when no board-full draw condition is declared;
- a Checkers victory when the opponent has no pieces left;
- continued play while the opponent still owns at least one piece;
- a Checkers victory when the next player has no generated legal moves;
- continued play when that player has an ordinary move or a capture.

### Board-renderer tests

The eight cases in `test_board_renderer.py` verify:

- rendering of an empty board and placed pieces;
- support for different dimensions and a single-cell board;
- `#` markers for non-playable light or dark cells;
- piece precedence over a non-playable-cell marker;
- preservation of the immutable state during rendering.

### Interactive-CLI tests

The seven cases in `test_game_cli.py` verify:

- normal and case-insensitive `quit` handling;
- recovery from malformed and non-integer coordinates;
- recovery from a move rejected by the engine;
- a complete winning game with its final board and message;
- a complete drawn game with its final board and message.

## Test levels

### Unit tests

Unit tests exercise one component or behaviour in isolation, such as a
transformation rule or semantic constraint.

### Integration tests

Integration tests verify collaboration across boundaries:

```text
.game file
    -> parser
    -> parse tree
    -> AST transformer
    -> GameDefinition
    -> SemanticValidator
    -> GameInitializer
    -> GameState
    -> MoveExecutor
    -> Next GameState
    -> ConditionEvaluator
    -> Ongoing or terminal GameState
    -> GameSession current state
    -> BoardRenderer output
    -> GameCLI interaction
```

### Negative tests

Negative tests confirm that invalid syntax, definitions, coordinates, and
runtime states are rejected with the correct error category.

### End-to-end tests

The move-executor suite verifies placement transitions to won or drawn states,
ordinary relocation, and immutable single-enemy capture transitions. The game-session
suite exercises a complete deterministic game from initialization through
sequential moves to a terminal result. The CLI suite covers the full path from
simulated user input to moves, state transitions, final board rendering, and
the result message.

## Fixtures

Module-scoped fixtures reuse expensive setup such as grammar loading:

```python
@pytest.fixture(scope="module")
def game_parser() -> GameParser:
    return GameParser()
```

`tmp_path` is used for temporary filesystem inputs, preventing tests from
modifying repository fixtures.

## Conventions

- Test modules follow `test_*.py`.
- Test functions have descriptive `test_*` names.
- Each test verifies one coherent behaviour.
- Positive and negative cases remain separate.
- Tests do not depend on execution order.
- Tests do not modify files inside `games/`.
- Tests avoid network access and external state.
- Shared setup belongs in fixtures.

Tests should assert public behaviour and stable domain contracts rather than
irrelevant internal implementation details.

## Continuous integration

`.github/workflows/tests.yml` runs:

```bash
python -m pytest -v
```

on pushes to `main` and pull requests targeting `main`. The repository ruleset
can require the `pytest` status check before merge.

## Coverage roadmap

Completed coverage includes parser, AST, semantic-validation, runtime-state,
game-initialization, placement and relocation request modelling, directional
players, typed and semantically validated movement rules, immutable and
semantically validated initial setup rules, capture syntax, immutable capture
AST rules, semantic capture constraints, ordinary relocation and capture
execution, promotion syntax and immutable AST rules, runtime setup expansion,
semantic promotion constraints, back-rank promotion execution after ordinary
movement or capture, Checkers player-state end-condition syntax, immutable AST
nodes, semantic target validation, runtime `no_pieces_left` and `no_moves_left`
evaluation, and deterministic legal movement and capture generation,
turn-rotation, end-condition, rendering, and interactive-session tests for
Tic-Tac-Toe.

Future coverage will add:

1. multiple and mandatory capture tests for Checkers;
2. complete Checkers scenario tests;
3. parser, AST, and semantic-validation tests for Connect Four;
4. complete game-scenario tests for additional supported games.

Every new DSL construct should include:

- at least one valid case;
- at least one invalid case;
- assertions about the produced model or diagnostic.

## Reporting failures

When reporting a failure, include:

- the failing test name;
- the complete traceback;
- the relevant `.game` input;
- Python and dependency versions when environment differences may matter.
