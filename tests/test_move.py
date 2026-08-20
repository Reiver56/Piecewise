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

def test_move_identifies_placement_request() -> None:
    coordinate = Coordinate(row=1, column=2)

    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=coordinate,
    )

    assert move.source is None
    assert move.destination == coordinate
    assert move.is_placement is True
    assert move.is_relocation is False


def test_move_contains_relocation_request() -> None:
    source = Coordinate(row=5, column=0)
    destination = Coordinate(row=4, column=1)

    move = Move(
        player="White",
        piece_name="Man",
        source=source,
        coordinate=destination,
    )

    assert move.player == "White"
    assert move.piece_name == "Man"
    assert move.source == source
    assert move.coordinate == destination
    assert move.destination == destination
    assert move.is_placement is False
    assert move.is_relocation is True


def test_move_rejects_equal_source_and_destination() -> None:
    coordinate = Coordinate(row=4, column=1)

    with pytest.raises(
        ValueError,
        match="Move source and destination must be different",
    ):
        Move(
            player="White",
            piece_name="Man",
            source=coordinate,
            coordinate=coordinate,
        )