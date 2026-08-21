from dataclasses import replace
from pathlib import Path

import pytest

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    BoardDefinition,
    DestinationCondition,
    ForwardDirection,
    MovementDirection,
    MovementRule,
    PieceDefinition,
    PlacementType,
    PlayerDefinition,
    PlayableCells,
    SetupRule,
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

@pytest.fixture(scope="module")
def valid_movement_game(valid_game):
    return replace(
        valid_game,
        players=(
            PlayerDefinition(
                name="White",
                forward=ForwardDirection.UP,
            ),
            PlayerDefinition(
                name="Black",
                forward=ForwardDirection.DOWN,
            ),
        ),
        turn_order=("White", "Black"),
        pieces=(
            PieceDefinition(
                name="Man",
                owners=("White", "Black"),
                movement=MovementRule(
                    direction=MovementDirection.DIAGONAL_FORWARD,
                    distance=1,
                    destination_condition=DestinationCondition.EMPTY,
                ),
            ),
        ),
    )

@pytest.fixture(scope="module")
def valid_setup_game(valid_movement_game):
    return replace(
        valid_movement_game,
        board=replace(
            valid_movement_game.board,
            rows=8,
            columns=8,
            playable_cells=PlayableCells.DARK,
        ),
        setup=(
            SetupRule(
                piece_name="Man",
                owner="White",
                first_row=6,
                last_row=8,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=1,
                last_row=3,
                playable_cells_only=True,
            ),
        ),
    )


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

def test_valid_movement_rules_have_no_semantic_issues(
    valid_movement_game,
    validator: SemanticValidator,
) -> None:
    assert validator.validate(valid_movement_game) == ()


def test_rejects_piece_without_placement_or_movement(
    valid_movement_game,
    validator: SemanticValidator,
) -> None:
    piece = valid_movement_game.pieces[0]
    invalid_game = replace(
        valid_movement_game,
        pieces=(
            replace(
                piece,
                placement=None,
                movement=None,
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "missing_piece_action"
        and issue.path == "pieces.Man.action"
        for issue in issues
    )


def test_rejects_piece_with_placement_and_movement(
    valid_movement_game,
    validator: SemanticValidator,
) -> None:
    piece = valid_movement_game.pieces[0]
    invalid_game = replace(
        valid_movement_game,
        pieces=(
            replace(
                piece,
                placement=PlacementType.ANY_EMPTY_CELL,
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "conflicting_piece_actions"
        and issue.path == "pieces.Man.action"
        for issue in issues
    )


def test_rejects_non_positive_movement_distance(
    valid_movement_game,
    validator: SemanticValidator,
) -> None:
    piece = valid_movement_game.pieces[0]
    movement = piece.movement

    assert movement is not None

    invalid_game = replace(
        valid_movement_game,
        pieces=(
            replace(
                piece,
                movement=replace(
                    movement,
                    distance=0,
                ),
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "invalid_movement_distance"
        and issue.path == "pieces.Man.movement.distance"
        for issue in issues
    )


def test_forward_movement_requires_owner_direction(
    valid_movement_game,
    validator: SemanticValidator,
) -> None:
    white, black = valid_movement_game.players
    invalid_game = replace(
        valid_movement_game,
        players=(
            replace(white, forward=None),
            black,
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "missing_forward_direction"
        and issue.path == "players.White.forward"
        for issue in issues
    )

def test_valid_setup_rules_have_no_semantic_issues(
    valid_setup_game,
    validator: SemanticValidator,
) -> None:
    assert validator.validate(valid_setup_game) == ()

def test_rejects_unknown_setup_piece(
    valid_setup_game,
    validator: SemanticValidator,
) -> None:
    setup_rule = valid_setup_game.setup[0]
    invalid_game = replace(
        valid_setup_game,
        setup=(
            replace(
                setup_rule,
                piece_name="Ghost",
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "unknown_setup_piece"
        and issue.path == "setup[0].piece_name"
        for issue in issues
    )

def test_rejects_unknown_setup_owner(
    valid_setup_game,
    validator: SemanticValidator,
) -> None:
    setup_rule = valid_setup_game.setup[0]
    invalid_game = replace(
        valid_setup_game,
        setup=(
            replace(
                setup_rule,
                owner="Ghost",
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "unknown_setup_owner"
        and issue.path == "setup[0].owner"
        for issue in issues
    )

def test_rejects_setup_owner_not_allowed_for_piece(
    valid_setup_game,
    validator: SemanticValidator,
) -> None:
    man = valid_setup_game.pieces[0]
    invalid_game = replace(
        valid_setup_game,
        pieces=(
            replace(
                man,
                owners=("White",),
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "setup_owner_not_allowed"
        and issue.path == "setup[1].owner"
        for issue in issues
    )

@pytest.mark.parametrize(
    ("first_row", "last_row"),
    [
        (0, 3),
        (5, 3),
    ],
)
def test_rejects_invalid_setup_row_range(
    valid_setup_game,
    validator: SemanticValidator,
    first_row: int,
    last_row: int,
) -> None:
    setup_rule = valid_setup_game.setup[0]
    invalid_game = replace(
        valid_setup_game,
        setup=(
            replace(
                setup_rule,
                first_row=first_row,
                last_row=last_row,
            ),
        ),
    )

    issues = validator.validate(invalid_game)

    assert any(
        issue.code == "invalid_setup_row_range"
        and issue.path == "setup[0].rows"
        for issue in issues
    )