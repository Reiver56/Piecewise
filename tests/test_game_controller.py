from pathlib import Path

from gui import GameController
from engine.game_state import (
    Coordinate,
    GameStatus,
)
from engine.game_state import GameStatus
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )

def load_connectfour():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "connectfour.game"
    )

def test_controller_initializes_game_session() -> None:
    game = load_tictactoe()

    controller = GameController(game)

    assert controller.game is game
    assert controller.state.rows == 3
    assert controller.state.columns == 3
    assert controller.state.pieces == ()
    assert controller.state.current_player == "X"
    assert controller.state.turn_number == 1
    assert controller.state.status is GameStatus.ONGOING
    assert controller.selected_source is None


def test_restart_creates_fresh_state_snapshot() -> None:
    controller = GameController(load_tictactoe())
    initial_state = controller.state

    result = controller.restart()

    assert result is controller.state
    assert result is not initial_state
    assert result.pieces == ()
    assert result.current_player == "X"
    assert result.turn_number == 1
    assert result.status is GameStatus.ONGOING
    assert controller.selected_source is None

def test_handle_cell_places_piece_for_tictactoe() -> None:
    controller = GameController(load_tictactoe())
    initial_state = controller.state

    result = controller.handle_cell(
        row=1,
        column=2,
    )

    assert result is controller.state
    assert result is not initial_state
    assert len(result.pieces) == 1
    assert result.pieces[0].piece_name == "Mark"
    assert result.pieces[0].owner == "X"
    assert result.pieces[0].coordinate == Coordinate(
        row=1,
        column=2,
    )
    assert result.current_player == "O"
    assert result.turn_number == 2
    assert result.status is GameStatus.ONGOING
    assert initial_state.pieces == ()

def test_handle_cell_selects_connect_four_column() -> None:
    controller = GameController(load_connectfour())

    result = controller.handle_cell(
        row=2,
        column=3,
    )

    assert len(result.pieces) == 1
    assert result.pieces[0].piece_name == "Disc"
    assert result.pieces[0].owner == "Red"
    assert result.pieces[0].coordinate == Coordinate(
        row=5,
        column=3,
    )
    assert result.current_player == "Yellow"
    assert result.turn_number == 2
    assert result.status is GameStatus.ONGOING