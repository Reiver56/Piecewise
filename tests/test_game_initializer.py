from dataclasses import replace
from pathlib import Path

import pytest

from engine.errors import GameInitializationError
from engine.game_initializer import GameInitializer
from engine.game_state import (
    Coordinate,
    GameStatus,
    PlacedPiece,
)
from parser.game_parser import GameParser
from parser.ast_nodes import (
    PlayableCells,
    SetupRule,
)


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )


def test_initialize_creates_empty_ongoing_state() -> None:
    game = load_tictactoe()

    state = GameInitializer().initialize(game)

    assert state.rows == 3
    assert state.columns == 3
    assert state.pieces == ()
    assert state.turn_number == 1
    assert state.status is GameStatus.ONGOING
    assert state.winner is None


def test_initialize_uses_first_player_in_turn_order() -> None:
    game = load_tictactoe()

    state = GameInitializer().initialize(game)

    assert state.current_player == game.turn_order[0]
    assert state.current_player == "X"


def test_initialize_rejects_invalid_game_definition() -> None:
    game = load_tictactoe()
    invalid_board = replace(game.board, rows=0)
    invalid_game = replace(game, board=invalid_board)

    with pytest.raises(
        GameInitializationError,
        match="Cannot initialize an invalid game definition",
    ):
        GameInitializer().initialize(invalid_game)


def test_initialization_error_contains_validation_details() -> None:
    game = load_tictactoe()
    invalid_board = replace(game.board, rows=0, columns=0)
    invalid_game = replace(game, board=invalid_board)

    with pytest.raises(GameInitializationError) as error_info:
        GameInitializer().initialize(invalid_game)

    message = str(error_info.value)

    assert "board" in message.lower()
    assert "rows" in message.lower()
    assert "columns" in message.lower()

def test_initialize_places_setup_pieces() -> None:
    game = load_tictactoe()
    game_with_setup = replace(
        game,
        setup=(
            SetupRule(
                piece_name="Mark",
                owner="X",
                first_row=1,
                last_row=1,
                playable_cells_only=True,
            ),
        ),
    )

    state = GameInitializer().initialize(game_with_setup)

    assert state.pieces == (
        PlacedPiece(
            piece_name="Mark",
            owner="X",
            coordinate=Coordinate(row=0, column=0),
        ),
        PlacedPiece(
            piece_name="Mark",
            owner="X",
            coordinate=Coordinate(row=0, column=1),
        ),
        PlacedPiece(
            piece_name="Mark",
            owner="X",
            coordinate=Coordinate(row=0, column=2),
        ),
    )

def test_initialize_uses_only_playable_dark_cells() -> None:
    game = load_tictactoe()
    game_with_setup = replace(
        game,
        board=replace(
            game.board,
            rows=4,
            columns=4,
            playable_cells=PlayableCells.DARK,
        ),
        setup=(
            SetupRule(
                piece_name="Mark",
                owner="X",
                first_row=1,
                last_row=2,
                playable_cells_only=True,
            ),
        ),
    )

    state = GameInitializer().initialize(game_with_setup)

    assert tuple(
        piece.coordinate
        for piece in state.pieces
    ) == (
        Coordinate(row=0, column=1),
        Coordinate(row=0, column=3),
        Coordinate(row=1, column=0),
        Coordinate(row=1, column=2),
    )

def test_initialize_uses_only_playable_light_cells() -> None:
    game = load_tictactoe()
    game_with_setup = replace(
        game,
        board=replace(
            game.board,
            rows=4,
            columns=4,
            playable_cells=PlayableCells.LIGHT,
        ),
        setup=(
            SetupRule(
                piece_name="Mark",
                owner="X",
                first_row=1,
                last_row=2,
                playable_cells_only=True,
            ),
        ),
    )

    state = GameInitializer().initialize(game_with_setup)

    assert tuple(
        piece.coordinate
        for piece in state.pieces
    ) == (
        Coordinate(row=0, column=0),
        Coordinate(row=0, column=2),
        Coordinate(row=1, column=1),
        Coordinate(row=1, column=3),
    )