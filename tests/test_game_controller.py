from dataclasses import replace
from pathlib import Path
import pytest

from gui import GameController
from engine.errors import InvalidMoveError
from engine.game_state import (
    Coordinate,
    GameStatus,
)
from engine.game_state import GameStatus
from parser.game_parser import GameParser
from parser.ast_nodes import SetupRule


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )

def load_connectfour():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "connectfour.game"
    )

def load_checkers():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
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

def test_rejected_cell_does_not_change_controller_state() -> None:
    controller = GameController(load_tictactoe())

    controller.handle_cell(
        row=0,
        column=0,
    )
    state_before_invalid_click = controller.state

    with pytest.raises(
        InvalidMoveError,
        match="already occupied",
    ):
        controller.handle_cell(
            row=0,
            column=0,
        )

    assert controller.state is state_before_invalid_click
    assert len(controller.state.pieces) == 1
    assert controller.state.current_player == "O"
    assert controller.state.turn_number == 2


def test_handle_cell_completes_connect_four_vertical_win() -> None:
    controller = GameController(load_connectfour())

    for column in (
        0,  # Red
        1,  # Yellow
        0,  # Red
        1,  # Yellow
        0,  # Red
        1,  # Yellow
        0,  # Red wins
    ):
        result = controller.handle_cell(
            row=3,
            column=column,
        )

    assert result is controller.state
    assert result.status is GameStatus.WON
    assert result.winner == "Red"
    assert result.turn_number == 8
    assert len(result.pieces) == 7

    assert {
        piece.coordinate
        for piece in result.pieces
        if piece.owner == "Red"
    } == {
        Coordinate(row=5, column=0),
        Coordinate(row=4, column=0),
        Coordinate(row=3, column=0),
        Coordinate(row=2, column=0),
    }

def test_handle_cell_selects_owned_checkers_piece() -> None:
    controller = GameController(load_checkers())
    initial_state = controller.state

    result = controller.handle_cell(
        row=5,
        column=0,
    )

    assert result is initial_state
    assert controller.state is initial_state
    assert controller.selected_source == Coordinate(
        row=5,
        column=0,
    )
    assert controller.state.current_player == "White"
    assert controller.state.turn_number == 1
    assert len(controller.state.pieces) == 24

def test_handle_cell_executes_checkers_relocation() -> None:
    controller = GameController(load_checkers())
    initial_state = controller.state

    selection_result = controller.handle_cell(
        row=5,
        column=0,
    )
    result = controller.handle_cell(
        row=4,
        column=1,
    )

    assert selection_result is initial_state
    assert controller.selected_source is None

    assert not any(
        piece.coordinate == Coordinate(
            row=5,
            column=0,
        )
        for piece in result.pieces
    )

    assert any(
        piece.piece_name == "Man"
        and piece.owner == "White"
        and piece.coordinate == Coordinate(
            row=4,
            column=1,
        )
        for piece in result.pieces
    )

    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.status is GameStatus.ONGOING

    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(
            row=5,
            column=0,
        )
        for piece in initial_state.pieces
    )

def test_controller_preserves_chained_capture_selection() -> None:
    game = load_checkers()

    chain_game = replace(
        game,
        setup=(
            SetupRule(
                piece_name="Man",
                owner="White",
                first_row=6,
                last_row=6,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=3,
                last_row=3,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=5,
                last_row=5,
                playable_cells_only=True,
            ),
        ),
    )

    controller = GameController(chain_game)

    controller.handle_cell(
        row=5,
        column=0,
    )
    continuation_state = controller.handle_cell(
        row=3,
        column=2,
    )

    assert continuation_state.current_player == "White"
    assert continuation_state.turn_number == 1
    assert continuation_state.forced_capture_source == Coordinate(
        row=3,
        column=2,
    )
    assert controller.selected_source == Coordinate(
        row=3,
        column=2,
    )

    result = controller.handle_cell(
        row=1,
        column=4,
    )

    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.forced_capture_source is None
    assert controller.selected_source is None

    assert any(
        piece.piece_name == "Man"
        and piece.owner == "White"
        and piece.coordinate == Coordinate(
            row=1,
            column=4,
        )
        for piece in result.pieces
    )

    assert not any(
        piece.owner == "Black"
        and piece.coordinate in {
            Coordinate(row=4, column=1),
            Coordinate(row=2, column=3),
        }
        for piece in result.pieces
    )

def test_controller_exposes_selected_piece_destinations() -> None:
    controller = GameController(load_checkers())

    assert controller.legal_destinations == ()

    controller.handle_cell(
        row=5,
        column=0,
    )

    assert controller.selected_source == Coordinate(
        row=5,
        column=0,
    )
    assert controller.legal_destinations == (
        Coordinate(
            row=4,
            column=1,
        ),
    )

def test_clicking_selected_source_cancels_selection() -> None:
    controller = GameController(load_checkers())
    initial_state = controller.state

    controller.handle_cell(
        row=5,
        column=0,
    )

    assert controller.selected_source == Coordinate(
        row=5,
        column=0,
    )
    assert controller.legal_destinations == (
        Coordinate(row=4, column=1),
    )

    result = controller.handle_cell(
        row=5,
        column=0,
    )

    assert result is initial_state
    assert controller.state is initial_state
    assert controller.selected_source is None
    assert controller.legal_destinations == ()
    assert controller.state.turn_number == 1


def test_controller_rejects_opponent_piece_selection() -> None:
    controller = GameController(load_checkers())
    initial_state = controller.state

    with pytest.raises(
        ValueError,
        match=(
            "Player 'White' cannot select "
            "a piece owned by 'Black'"
        ),
    ):
        controller.handle_cell(
            row=2,
            column=1,
        )

    assert controller.state is initial_state
    assert controller.selected_source is None
    assert controller.legal_destinations == ()
    assert controller.state.current_player == "White"
    assert controller.state.turn_number == 1