from dataclasses import FrozenInstanceError

import pytest

from engine.game_state import Coordinate
from engine.move import Move


def test_move_contains_placement_request() -> None:
    coordinate = Coordinate(row=1, column=2)

    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=coordinate,
    )

    assert move.player == "X"
    assert move.piece_name == "Mark"
    assert move.coordinate == coordinate


@pytest.mark.parametrize(
    ("player", "piece_name", "error_message"),
    [
        ("", "Mark", "Move player cannot be empty."),
        ("X", "", "Move piece name cannot be empty."),
    ],
)
def test_move_rejects_empty_required_fields(
    player: str,
    piece_name: str,
    error_message: str,
) -> None:
    with pytest.raises(ValueError, match=error_message):
        Move(
            player=player,
            piece_name=piece_name,
            coordinate=Coordinate(row=0, column=0),
        )


def test_move_is_immutable() -> None:
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(FrozenInstanceError):
        move.player = "O"  # type: ignore[misc]