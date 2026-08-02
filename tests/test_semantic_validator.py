from dataclasses import replace
from pathlib import Path

import pytest

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    BoardDefinition,
    PieceDefinition,
    PlayerDefinition,
)
from parser.game_parser import GameParser
from validation import (
    SemanticValidationError,
    SemanticValidator,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"


@pytest.fixture(scope="module")
def valid_game():
    return GameParser().parse_game_file(TICTACTOE_PATH)


@pytest.fixture
def validator() -> SemanticValidator:
    return SemanticValidator()


def test_valid_tictactoe_has_no_semantic_issues(
    valid_game,
    validator: SemanticValidator,
) -> None:
    assert validator.validate(valid_game) == ()


def test_validate_or_raise_accepts_valid_game(
    valid_game,
    validator: SemanticValidator,
) -> None:
    validator.validate_or_raise(valid_game)


def test_collects_multiple_semantic_issues(
    valid_game,
    validator: SemanticValidator,
) -> None:
    invalid_game = replace(
        valid_game,
        board=BoardDefinition(
            rows=0,
            columns=2,
            playable_cells=valid_game.board.playable_cells,
        ),
        players=(
            PlayerDefinition(name="X"),
            PlayerDefinition(name="X"),
        ),
        turn_order=("X", "X", "Unknown"),
        pieces=(
            PieceDefinition(
                name="Mark",
                owners=("X", "Ghost"),
                placement=valid_game.pieces[0].placement,
            ),
            PieceDefinition(
                name="Mark",
                owners=("X",),
                placement=valid_game.pieces[0].placement,
            ),
        ),
        win_conditions=(
            AlignCondition(
                length=3,
                direction=AlignmentDirection.SAME_ROW,
            ),
            AlignCondition(
                length=0,
                direction=AlignmentDirection.SAME_COL,
            ),
        ),
    )

    issues = validator.validate(invalid_game)
    codes = {issue.code for issue in issues}

    assert codes == {
        "invalid_board_rows",
        "duplicate_player",
        "duplicate_turn_player",
        "unknown_turn_player",
        "duplicate_piece",
        "unknown_piece_owner",
        "alignment_does_not_fit",
        "invalid_alignment_length",
    }


def test_validate_or_raise_contains_all_issues(
    valid_game,
    validator: SemanticValidator,
) -> None:
    invalid_game = replace(
        valid_game,
        board=replace(valid_game.board, rows=-1, columns=0),
    )

    with pytest.raises(SemanticValidationError) as error:
        validator.validate_or_raise(invalid_game)

    assert tuple(
        issue.code for issue in error.value.issues
    ) == (
        "invalid_board_rows",
        "invalid_board_columns",
        "alignment_does_not_fit",
        "alignment_does_not_fit",
        "alignment_does_not_fit",
    )

    message = str(error.value)

    assert "Invalid game definition:" in message
    assert "[invalid_board_rows] board.rows:" in message
    assert "[invalid_board_columns] board.columns:" in message