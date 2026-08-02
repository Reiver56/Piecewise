from dataclasses import FrozenInstanceError

import pytest

from engine.game_state import (
    Coordinate,
    GameState,
    GameStatus,
    PlacedPiece,
)


def test_coordinate_uses_zero_based_indices() -> None:
    coordinate = Coordinate(row=0, column=2)

    assert coordinate.row == 0
    assert coordinate.column == 2


@pytest.mark.parametrize(
    ("row", "column"),
    [
        (-1, 0),
        (0, -1),
    ],
)
def test_coordinate_rejects_negative_indices(
    row: int,
    column: int,
) -> None:
    with pytest.raises(ValueError):
        Coordinate(row=row, column=column)


def test_game_state_defaults_to_ongoing() -> None:
    state = GameState(
        rows=3,
        columns=3,
        pieces=(),
        current_player="X",
        turn_number=1,
    )

    assert state.status is GameStatus.ONGOING
    assert state.winner is None
    assert state.pieces == ()


def test_game_state_contains_placed_pieces() -> None:
    piece = PlacedPiece(
        piece_name="Mark",
        owner="X",
        coordinate=Coordinate(row=1, column=2),
    )
    state = GameState(
        rows=3,
        columns=3,
        pieces=(piece,),
        current_player="O",
        turn_number=2,
    )

    assert state.pieces == (piece,)
    assert state.pieces[0].owner == "X"


def test_game_state_is_immutable() -> None:
    state = GameState(
        rows=3,
        columns=3,
        pieces=(),
        current_player="X",
        turn_number=1,
    )

    with pytest.raises(FrozenInstanceError):
        state.turn_number = 2  # type: ignore[misc]