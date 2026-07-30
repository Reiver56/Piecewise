# Piecewise Tests

This directory contains the automated test suite for Piecewise.

The project uses [pytest](https://docs.pytest.org/) to verify each component in
isolation and to check that the parsing pipeline works correctly from `.game`
source files to parse trees.

## Files

```text
tests/
├── __init__.py
├── test_parser.py
└── README.md
```

Additional test modules will be added as the project grows:

```text
tests/
├── test_parser.py
├── test_ast_transformer.py
├── test_semantic_validator.py
└── test_engine.py
```

## Running the tests

Install the test dependencies from the project root:

```bash
python -m pip install lark pytest
```

Run the complete suite:

```bash
python -m pytest -v
```

Run a single test module:

```bash
python -m pytest tests/test_parser.py -v
```

Run a single test:

```bash
python -m pytest tests/test_parser.py::test_parse_valid_tictactoe -v
```

The commands must be executed from the project root so imports and project paths
are resolved consistently.

## Current parser tests

The initial parser suite contains three tests.

### Valid Tic-Tac-Toe definition

`test_parse_valid_tictactoe` parses `games/tictactoe.game` and verifies that:

- parsing completes without an exception;
- the returned root node is `start`;
- the parse tree contains child nodes.

This is a positive integration test between the example game, Lark grammar, and
`GameParser`.

### Incomplete game definition

`test_reject_incomplete_game` passes an incomplete game definition directly to
the parser and expects a Lark `UnexpectedInput` exception.

This is a negative syntax test: invalid input must be rejected instead of
producing a partial parse tree.

### Invalid file extension

`test_reject_wrong_file_extension` creates a temporary `.txt` file and verifies
that `GameParser.parse_file` raises `ValueError`.

The test uses pytest's `tmp_path` fixture, so it does not create permanent files
inside the repository.

## Test structure

Tests follow the Arrange-Act-Assert pattern:

1. **Arrange:** prepare the parser and input;
2. **Act:** execute the operation being tested;
3. **Assert:** verify the returned result or expected exception.

Example:

```python
def test_parse_valid_tictactoe(game_parser: GameParser) -> None:
    tree = game_parser.parse_file(TICTACTOE_PATH)

    assert tree.data == "start"
    assert tree.children
```

## Fixtures

The parser tests use a module-scoped fixture:

```python
@pytest.fixture(scope="module")
def game_parser() -> GameParser:
    return GameParser()
```

The `GameParser` instance is created once and shared by all tests in the module.
This avoids repeatedly loading and compiling the same Lark grammar.

Fixtures should contain reusable setup, not test assertions or domain logic.

## Test categories

The Piecewise suite will contain the following categories.

### Unit tests

Unit tests exercise one component in isolation, such as:

- parsing a source string;
- transforming one parse-tree node;
- validating one semantic constraint;
- checking one movement rule.

### Integration tests

Integration tests verify collaboration between components, such as:

```text
.game file -> parser -> parse tree -> AST
```

The valid Tic-Tac-Toe parser test is the first integration test.

### Negative tests

Negative tests verify that invalid definitions and illegal game actions are
rejected with the correct error type.

Examples include:

- malformed syntax;
- references to undeclared players;
- invalid board dimensions;
- illegal moves;
- actions performed by the wrong player.

### End-to-end tests

Later increments will run complete deterministic game scenarios from initial
setup to a win or draw.

## Naming conventions

- Test modules use the `test_*.py` naming pattern.
- Test functions use descriptive `test_*` names.
- Each test verifies one clearly identifiable behavior.
- Positive and negative cases are tested separately.
- Shared setup is implemented with pytest fixtures.
- Temporary filesystem content uses `tmp_path`.

Avoid coupling tests to irrelevant parse-tree details. A test should fail when
observable behavior changes incorrectly, not when an internal implementation is
refactored without changing its contract.

## Test independence

Tests must:

- run successfully in any order;
- avoid depending on state left by another test;
- avoid modifying files inside `games/`;
- avoid network access;
- produce the same result on repeated executions.

This keeps the suite deterministic and suitable for future continuous
integration.

## Coverage roadmap

Testing will be expanded incrementally:

1. parser tests for Tic-Tac-Toe;
2. AST transformation tests;
3. semantic-validation tests;
4. parser tests for Checkers;
5. parser tests for Connect Four;
6. engine unit tests;
7. complete game-scenario tests.

Every newly supported DSL construct should add:

- at least one valid example;
- at least one invalid example;
- an assertion about the produced model or error.

## Reporting failures

Run pytest without hiding the traceback:

```bash
python -m pytest -v
```

When reporting a failure, include:

- the failing test name;
- the complete exception and traceback;
- the relevant `.game` input;
- the Python and dependency versions when environment differences may matter.