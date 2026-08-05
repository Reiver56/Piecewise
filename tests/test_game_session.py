from pathlib import Path

import pytest

from engine.errors import InvalidMoveError
from engine.game_session import GameSession
from engine.game_state import Coordinate, GameStatus
from engine.move import Move
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )


def create_move(
    player: str,
    row: int,
    column: int,
) -> Move:
    return Move(
        player=player,
        piece_name="Mark",
        coordinate=Coordinate(row=row, column=column),
    )


def test_session_initializes_game_state() -> None:
    session = GameSession(load_tictactoe())

    assert session.state.rows == 3
    assert session.state.columns == 3
    assert session.state.pieces == ()
    assert session.state.current_player == "X"
    assert session.state.turn_number == 1
    assert session.state.status is GameStatus.ONGOING


def test_play_updates_and_returns_current_state() -> None:
    session = GameSession(load_tictactoe())

    result = session.play(create_move("X", 0, 0))

    assert result is session.state
    assert len(result.pieces) == 1
    assert result.pieces[0].owner == "X"
    assert result.pieces[0].coordinate == Coordinate(
        row=0,
        column=0,
    )
    assert result.current_player == "O"
    assert result.turn_number == 2


def test_play_preserves_previous_state_snapshot() -> None:
    session = GameSession(load_tictactoe())
    initial_state = session.state

    session.play(create_move("X", 0, 0))

    assert initial_state.pieces == ()
    assert initial_state.current_player == "X"
    assert initial_state.turn_number == 1
    assert session.state is not initial_state


def test_session_applies_moves_sequentially() -> None:
    session = GameSession(load_tictactoe())

    session.play(create_move("X", 0, 0))
    session.play(create_move("O", 1, 0))
    result = session.play(create_move("X", 0, 1))

    assert len(result.pieces) == 3
    assert result.current_player == "O"
    assert result.turn_number == 4
    assert result.status is GameStatus.ONGOING


def test_session_reaches_winning_state() -> None:
    session = GameSession(load_tictactoe())

    session.play(create_move("X", 0, 0))
    session.play(create_move("O", 1, 0))
    session.play(create_move("X", 0, 1))
    session.play(create_move("O", 1, 1))
    result = session.play(create_move("X", 0, 2))

    assert result is session.state
    assert result.status is GameStatus.WON
    assert result.winner == "X"
    assert result.turn_number == 6


def test_invalid_move_does_not_change_session_state() -> None:
    session = GameSession(load_tictactoe())
    state_before_move = session.state

    with pytest.raises(
        InvalidMoveError,
        match="It is X's turn, not O",
    ):
        session.play(create_move("O", 0, 0))

    assert session.state is state_before_move


def test_session_rejects_moves_after_game_ends() -> None:
    session = GameSession(load_tictactoe())

    session.play(create_move("X", 0, 0))
    session.play(create_move("O", 1, 0))
    session.play(create_move("X", 0, 1))
    session.play(create_move("O", 1, 1))
    winning_state = session.play(create_move("X", 0, 2))

    with pytest.raises(
        InvalidMoveError,
        match="Cannot apply a move after the game has ended",
    ):
        session.play(create_move("O", 2, 0))

    assert session.state is winning_state
    assert session.state.status is GameStatus.WON