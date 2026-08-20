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
)

from parser.game_parser import GameParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"

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
@pytest.fixture(scope="module")
def tictactoe_game() -> GameDefinition:
    return GameParser().parse_game_file(TICTACTOE_PATH)

@pytest.fixture(scope="module")
def movement_game() -> GameDefinition:
    return GameParser().parse_game(MOVEMENT_GAME_SOURCE)


def test_transform_tictactoe_definition(
    tictactoe_game: GameDefinition,
) -> None:
    assert tictactoe_game.name == "TicTacToe"

    assert tictactoe_game.board.rows == 3
    assert tictactoe_game.board.columns == 3
    assert tictactoe_game.board.playable_cells is PlayableCells.ALL

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


def test_movement_rule_is_immutable(
    movement_game: GameDefinition,
) -> None:
    movement_rule = movement_game.pieces[0].movement

    assert movement_rule is not None

    with pytest.raises(FrozenInstanceError):
        setattr(movement_rule, "distance", 2)