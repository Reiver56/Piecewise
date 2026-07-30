# Piecewise Tests

Piecewise uses pytest for automated unit and integration testing. The same suite
runs locally and in GitHub Actions for pull requests targeting `main`.

## Files

```text
tests/
├── __init__.py
├── test_parser.py
├── test_ast_transformer.py
└── README.md
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

The suite currently contains six tests.

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

## Test levels

### Unit tests

Unit tests exercise one component or behaviour in isolation, such as a
transformation rule or semantic constraint.

### Integration tests

Integration tests verify collaboration across boundaries:

```text
.game file -> parser -> parse tree -> AST transformer -> GameDefinition
```

### Negative tests

Negative tests confirm that invalid syntax, definitions, and future game actions
are rejected with the correct error category.

### End-to-end tests

Future scenarios will execute complete deterministic games from setup to a win
or draw.

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

1. parser and AST tests for Tic-Tac-Toe;
2. semantic-validation tests;
3. parser and AST tests for Checkers;
4. parser and AST tests for Connect Four;
5. engine unit tests;
6. complete game-scenario tests.

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