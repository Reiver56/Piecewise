# Piecewise Tests

Piecewise uses pytest for automated unit and integration testing. The same suite
runs locally and in GitHub Actions for pull requests targeting `main`.

## Files

```text
tests/
├── __init__.py
├── test_parser.py
├── test_ast_transformer.py
├── test_semantic_validator.py
├── test_condition_evaluator.py
├── test_game_initializer.py
├── test_game_session.py
├── test_game_state.py
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

The suite currently contains 66 tests.

### Parser tests

`test_parse_valid_tictactoe`

- parses `games/tictactoe.game`;
- verifies that the root node is `start`;
- verifies that the parse tree is not empty.

`test_reject_incomplete_game`

- supplies an incomplete definition;
- expects a Lark `UnexpectedInput` exception.

`test_reject_wrong_file_extension`

- creates a temporary `.txt` file;
- verifies that `GameParser.parse_file` raises `ValueError`.

### AST tests

`test_transform_tictactoe_definition`

- exercises the complete file-to-AST pipeline;
- verifies the game, board, players, turn order, and piece;
- checks typed enum values.

`test_transform_win_conditions`

- verifies the three alignment conditions;
- verifies the full-board draw condition;
- checks the complete immutable tuple of typed conditions.

`test_ast_is_immutable`

- attempts to modify a parsed `GameDefinition`;
- verifies that the frozen dataclass raises `FrozenInstanceError`.

### Semantic-validation tests

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

### Game-initializer tests

The four tests in `test_game_initializer.py` verify that:

- initialization creates an empty, ongoing state;
- the first player in `turn_order` becomes the current player;
- semantically invalid definitions are rejected;
- `GameInitializationError` includes validation details.

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

The four cases in `test_move.py` verify:

- storage of the player, piece name, and destination coordinate;
- rejection of an empty player or piece name;
- immutability of placement requests.

### Move-executor tests

The 13 cases in `test_move_executor.py` verify:

- piece placement, turn-number advancement, and player rotation;
- creation of a new state without modifying the previous snapshot;
- rejection of moves after a game has ended;
- enforcement of the current player's turn;
- board-boundary and playable-cell checks;
- rejection of unknown or unowned piece types;
- rejection of occupied destination cells;
- automatic transition to a won state after a winning placement;
- automatic transition to a drawn state after a board-filling placement.

### Condition-evaluator tests

The 10 cases in `test_condition_evaluator.py` verify:

- row and column victories;
- victories across both diagonal directions;
- rejection of mixed-owner and non-consecutive alignments;
- full-board draw detection;
- victory precedence when the last move also fills the board;
- board-full evaluation using only playable cells;
- continued play when no board-full draw condition is declared.

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
```

### Negative tests

Negative tests confirm that invalid syntax, definitions, coordinates, and
runtime states are rejected with the correct error category.

### End-to-end tests

The move-executor suite verifies the integrated transition from a valid
placement to a won or drawn runtime state. The game-session suite exercises a
complete deterministic game from initialization through sequential moves to a
terminal result.

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
game-initialization, placement-move, turn-rotation, and end-condition tests for
Tic-Tac-Toe, including complete game-session orchestration.

Future coverage will add:

1. parser, AST, and semantic-validation tests for Checkers;
2. parser, AST, and semantic-validation tests for Connect Four;
3. complete game-scenario tests for additional supported games.

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
