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

@pytest.mark.parametrize(
    ("rows", "columns"),
    [
        (0, 3),
        (-1, 3),
        (3, 0),
        (3, -1),
    ],
)
def test_game_state_rejects_invalid_board_dimensions(
    rows: int,
    columns: int,
) -> None:
    with pytest.raises(ValueError):
        GameState(
            rows=rows,
            columns=columns,
            pieces=(),
            current_player="X",
            turn_number=1,
        )


def test_game_state_rejects_invalid_turn_number() -> None:
    with pytest.raises(ValueError, match="Turn number"):
        GameState(
            rows=3,
            columns=3,
            pieces=(),
            current_player="X",
            turn_number=0,
        )


def test_game_state_rejects_empty_current_player() -> None:
    with pytest.raises(ValueError, match="Current player"):
        GameState(
            rows=3,
            columns=3,
            pieces=(),
            current_player="",
            turn_number=1,
        )


def test_won_game_requires_winner() -> None:
    with pytest.raises(ValueError, match="must have a winner"):
        GameState(
            rows=3,
            columns=3,
            pieces=(),
            current_player="X",
            turn_number=5,
            status=GameStatus.WON,
        )


@pytest.mark.parametrize(
    "status",
    [
        GameStatus.ONGOING,
        GameStatus.DRAWN,
    ],
)
def test_non_won_game_rejects_winner(
    status: GameStatus,
) -> None:
    with pytest.raises(ValueError, match="Only a won game"):
        GameState(
            rows=3,
            columns=3,
            pieces=(),
            current_player="X",
            turn_number=5,
            status=status,
            winner="X",
        )


@pytest.mark.parametrize(
    "coordinate",
    [
        Coordinate(row=3, column=0),
        Coordinate(row=0, column=3),
    ],
)
def test_game_state_rejects_piece_outside_board(
    coordinate: Coordinate,
) -> None:
    piece = PlacedPiece(
        piece_name="Mark",
        owner="X",
        coordinate=coordinate,
    )

    with pytest.raises(ValueError, match="outside"):
        GameState(
            rows=3,
            columns=3,
            pieces=(piece,),
            current_player="O",
            turn_number=2,
        )


def test_game_state_rejects_overlapping_pieces() -> None:
    coordinate = Coordinate(row=1, column=1)
    pieces = (
        PlacedPiece(
            piece_name="Mark",
            owner="X",
            coordinate=coordinate,
        ),
        PlacedPiece(
            piece_name="Mark",
            owner="O",
            coordinate=coordinate,
        ),
    )

    with pytest.raises(ValueError, match="Multiple pieces occupy"):
        GameState(
            rows=3,
            columns=3,
            pieces=pieces,
            current_player="X",
            turn_number=3,
        )

def test_game_state_stores_forced_capture_source() -> None:
    source = Coordinate(row=1, column=1)
    piece = PlacedPiece(
        piece_name="Man",
        owner="White",
        coordinate=source,
    )

    state = GameState(
        rows=3,
        columns=3,
        pieces=(piece,),
        current_player="White",
        turn_number=2,
        forced_capture_source=source,
    )

    assert state.forced_capture_source == source

def test_game_state_rejects_empty_forced_capture_source() -> None:
    with pytest.raises(
        ValueError,
        match="Forced capture source must contain a piece",
    ):
        GameState(
            rows=3,
            columns=3,
            pieces=(),
            current_player="X",
            turn_number=1,
            forced_capture_source=Coordinate(
                row=1,
                column=1,
            ),
        )

def test_game_state_rejects_opponent_forced_capture_source() -> None:
    source = Coordinate(row=1, column=1)
    opponent_piece = PlacedPiece(
        piece_name="Man",
        owner="O",
        coordinate=source,
    )

    with pytest.raises(
        ValueError,
        match="Forced capture source must belong to the current player",
    ):
        GameState(
            rows=3,
            columns=3,
            pieces=(opponent_piece,),
            current_player="X",
            turn_number=1,
            forced_capture_source=source,
        )