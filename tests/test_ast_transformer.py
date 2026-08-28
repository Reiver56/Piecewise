from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    BoardFullCondition,
    DestinationCondition,
    ForwardDirection,
    GameDefinition,
    MovementDirection,
    MovementRule,
    Outcome,
    PieceDefinition,
    PlacementType,
    PlayableCells,
    PlayerDefinition,
    SetupRule,
    CaptureCondition,
    CaptureRule,
    PromotionCondition,
    PromotionRule,
    NoMovesLeftCondition,
    NoPiecesLeftCondition,
    PlayerTarget,
    NoMovesLeftCondition,
    NoPiecesLeftCondition,
    PlayerTarget,
    GravityDirection,
)

from parser.game_parser import GameParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"
CHECKERS_PATH = PROJECT_ROOT / "games" / "checkers.game"

MOVEMENT_GAME_SOURCE = """
game MovementGame {
    board {
        size: 8x8
        playable_cells: dark
    }

    players {
        player White {
            forward: up
        }

        player Black {
            forward: down
        }

        turn_order: White, Black
    }

    piece Man {
        owner: White, Black
        move: diagonal forward 1 if empty
    }

    piece King {
        owner: White, Black
        move: diagonal any 1 if empty
    }

    win_condition {
        board_full: no_winner -> draw
    }
}
"""

SETUP_GAME_SOURCE = """
game SetupGame {
    board {
        size: 8x8
        playable_cells: dark
    }

    players {
        player White
        player Black
        turn_order: White, Black
    }

    piece Man {
        owner: White, Black
        move: diagonal forward 1 if empty
    }

    setup {
        place: Man owned_by White on rows 6..8 playable_cells
        place: Man owned_by Black on rows 1..3 playable_cells
    }

    win_condition {
        board_full: no_winner -> draw
    }
}
"""

CAPTURE_GAME_SOURCE = """
game CaptureGame {
    board {
        size: 8x8
        playable_cells: dark
    }

    players {
        player White {
            forward: up
        }

        player Black {
            forward: down
        }

        turn_order: White, Black
    }

    piece Man {
        owner: White, Black
        move: diagonal forward 1 if empty
        capture: diagonal forward 2 if enemy
    }

    piece King {
        owner: White, Black
        move: diagonal any 1 if empty
        capture: diagonal any 2 if enemy
    }

    win_condition {
        board_full: no_winner -> draw
    }
}
"""

PROMOTION_GAME_SOURCE = CAPTURE_GAME_SOURCE.replace(
    "capture: diagonal forward 2 if enemy",
    (
        "capture: diagonal forward 2 if enemy\n"
        "        promote: back_rank -> King"
    ),
    1,
)

@pytest.fixture(scope="module")
def tictactoe_game() -> GameDefinition:
    return GameParser().parse_game_file(TICTACTOE_PATH)

@pytest.fixture(scope="module")
def gravity_game() -> GameDefinition:
    source = TICTACTOE_PATH.read_text(
        encoding="utf-8",
    ).replace(
        "playable_cells: all",
        (
            "playable_cells: all\n"
            "        gravity: down"
        ),
        1,
    )

    return GameParser().parse_game(source)

@pytest.fixture(scope="module")
def checkers_game() -> GameDefinition:
    return GameParser().parse_game_file(CHECKERS_PATH)

@pytest.fixture(scope="module")
def movement_game() -> GameDefinition:
    return GameParser().parse_game(MOVEMENT_GAME_SOURCE)

@pytest.fixture(scope="module")
def capture_game() -> GameDefinition:
    return GameParser().parse_game(CAPTURE_GAME_SOURCE)

@pytest.fixture(scope="module")
def promotion_game() -> GameDefinition:
    return GameParser().parse_game(PROMOTION_GAME_SOURCE)

@pytest.fixture(scope="module")
def setup_game() -> GameDefinition:
    return GameParser().parse_game(SETUP_GAME_SOURCE)

def test_transform_tictactoe_definition(
    tictactoe_game: GameDefinition,
) -> None:
    assert tictactoe_game.name == "TicTacToe"

    assert tictactoe_game.board.rows == 3
    assert tictactoe_game.board.columns == 3
    assert tictactoe_game.board.playable_cells is PlayableCells.ALL
    assert tictactoe_game.board.gravity is None

    assert tuple(
        player.name for player in tictactoe_game.players
    ) == ("X", "O")

    assert tictactoe_game.turn_order == ("X", "O")

    assert len(tictactoe_game.pieces) == 1

    mark = tictactoe_game.pieces[0]

    assert mark.name == "Mark"
    assert mark.owners == ("X", "O")
    assert mark.placement is PlacementType.ANY_EMPTY_CELL
    assert mark.movement is None
    assert all(
        player.forward is None
        for player in tictactoe_game.players
    )


def test_transform_board_gravity(
    gravity_game: GameDefinition,
) -> None:
    assert gravity_game.board.gravity is GravityDirection.DOWN

def test_board_gravity_is_immutable(
    gravity_game: GameDefinition,
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(
            gravity_game.board,
            "gravity",
            None,
        )

def test_transform_win_conditions(
    tictactoe_game: GameDefinition,
) -> None:
    assert tictactoe_game.win_conditions == (
        AlignCondition(
            length=3,
            direction=AlignmentDirection.SAME_ROW,
            outcome=Outcome.WIN,
        ),
        AlignCondition(
            length=3,
            direction=AlignmentDirection.SAME_COL,
            outcome=Outcome.WIN,
        ),
        AlignCondition(
            length=3,
            direction=AlignmentDirection.DIAGONAL,
            outcome=Outcome.WIN,
        ),
        BoardFullCondition(outcome=Outcome.DRAW),
    )

def test_transform_checkers_end_conditions(
    checkers_game: GameDefinition,
) -> None:
    assert checkers_game.win_conditions == (
        NoPiecesLeftCondition(
            target=PlayerTarget.OPPONENT,
            outcome=Outcome.WIN,
        ),
        NoMovesLeftCondition(
            target=PlayerTarget.OPPONENT,
            outcome=Outcome.WIN,
        ),
    )

@pytest.mark.parametrize(
    "condition",
    (
        NoPiecesLeftCondition(
            target=PlayerTarget.OPPONENT,
        ),
        NoMovesLeftCondition(
            target=PlayerTarget.OPPONENT,
        ),
    ),
    ids=(
        "no_pieces_left",
        "no_moves_left",
    ),
)
def test_checkers_end_condition_is_immutable(
    condition: (
        NoPiecesLeftCondition
        | NoMovesLeftCondition
    ),
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(
            condition,
            "target",
            PlayerTarget.OPPONENT,
        )

def test_ast_is_immutable(
    tictactoe_game: GameDefinition,
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(tictactoe_game, "name", "ModifiedGame")

def test_transform_player_forward_directions(
    movement_game: GameDefinition,
) -> None:
    assert movement_game.players == (
        PlayerDefinition(
            name="White",
            forward=ForwardDirection.UP,
        ),
        PlayerDefinition(
            name="Black",
            forward=ForwardDirection.DOWN,
        ),
    )

    assert movement_game.turn_order == ("White", "Black")


def test_transform_piece_movement_rules(
    movement_game: GameDefinition,
) -> None:
    assert movement_game.pieces == (
        PieceDefinition(
            name="Man",
            owners=("White", "Black"),
            placement=None,
            movement=MovementRule(
                direction=MovementDirection.DIAGONAL_FORWARD,
                distance=1,
                destination_condition=DestinationCondition.EMPTY,
            ),
        ),
        PieceDefinition(
            name="King",
            owners=("White", "Black"),
            placement=None,
            movement=MovementRule(
                direction=MovementDirection.DIAGONAL_ANY,
                distance=1,
                destination_condition=DestinationCondition.EMPTY,
            ),
        ),
    )

def test_transform_piece_capture_rules(
    capture_game: GameDefinition,
) -> None:
    man_capture = capture_game.pieces[0].capture
    king_capture = capture_game.pieces[1].capture

    assert man_capture == CaptureRule(
        direction=MovementDirection.DIAGONAL_FORWARD,
        distance=2,
        condition=CaptureCondition.ENEMY,
    )

    assert king_capture == CaptureRule(
        direction=MovementDirection.DIAGONAL_ANY,
        distance=2,
        condition=CaptureCondition.ENEMY,
    )

def test_transform_piece_promotion_rule(
    promotion_game: GameDefinition,
) -> None:
    man, king = promotion_game.pieces

    assert man.promotion == PromotionRule(
        condition=PromotionCondition.BACK_RANK,
        target_piece_name="King",
    )

    assert king.promotion is None

def test_promotion_rule_is_immutable(
    promotion_game: GameDefinition,
) -> None:
    promotion_rule = promotion_game.pieces[0].promotion

    assert promotion_rule is not None

    with pytest.raises(FrozenInstanceError):
        setattr(
            promotion_rule,
            "target_piece_name",
            "SuperKing",
        )

def test_piece_without_capture_has_no_capture(
    movement_game: GameDefinition,
) -> None:
    assert all(
        piece.capture is None
        for piece in movement_game.pieces
    )


def test_capture_rule_is_immutable(
    capture_game: GameDefinition,
) -> None:
    capture_rule = capture_game.pieces[0].capture

    assert capture_rule is not None

    with pytest.raises(FrozenInstanceError):
        setattr(capture_rule, "distance", 3)

def test_movement_rule_is_immutable(
    movement_game: GameDefinition,
) -> None:
    movement_rule = movement_game.pieces[0].movement

    assert movement_rule is not None

    with pytest.raises(FrozenInstanceError):
        setattr(movement_rule, "distance", 2)

def test_transform_setup_rules(
    setup_game: GameDefinition,
) -> None:
    assert setup_game.setup == (
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
    )

def test_game_without_setup_has_empty_setup(
    tictactoe_game: GameDefinition,
) -> None:
    assert tictactoe_game.setup == ()

def test_setup_rule_is_immutable(
    setup_game: GameDefinition,
) -> None:
    setup_rule = setup_game.setup[0]

    with pytest.raises(FrozenInstanceError):
        setattr(setup_rule, "first_row", 5)