from dataclasses import replace
from pathlib import Path

import pytest

from engine.errors import InvalidMoveError
from engine.game_initializer import GameInitializer
from engine.game_state import Coordinate, GameState, GameStatus, PlacedPiece
from engine.move import Move
from engine.move_executor import MoveExecutor
from parser.ast_nodes import PlayableCells
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )


def test_apply_places_piece_and_advances_turn() -> None:
    game = load_tictactoe()
    initial_state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=1, column=1),
    )

    new_state = MoveExecutor(game).apply(initial_state, move)

    assert new_state.pieces == (
        PlacedPiece(
            piece_name="Mark",
            owner="X",
            coordinate=Coordinate(row=1, column=1),
        ),
    )
    assert new_state.current_player == "O"
    assert new_state.turn_number == 2
    assert new_state.status is GameStatus.ONGOING


def test_apply_does_not_modify_previous_state() -> None:
    game = load_tictactoe()
    initial_state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    new_state = MoveExecutor(game).apply(initial_state, move)

    assert new_state is not initial_state
    assert initial_state.pieces == ()
    assert initial_state.current_player == "X"
    assert initial_state.turn_number == 1


def test_apply_rotates_back_to_first_player() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
        ),
        current_player="O",
        turn_number=2,
    )
    move = Move(
        player="O",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=1),
    )

    new_state = MoveExecutor(game).apply(state, move)

    assert new_state.current_player == "X"
    assert new_state.turn_number == 3


def test_apply_rejects_move_after_game_has_ended() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(),
        current_player="X",
        turn_number=6,
        status=GameStatus.WON,
        winner="X",
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="game has ended"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_wrong_player_turn() -> None:
    game = load_tictactoe()
    state = GameInitializer().initialize(game)
    move = Move(
        player="O",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="It is X's turn"):
        MoveExecutor(game).apply(state, move)


@pytest.mark.parametrize(
    "coordinate",
    [
        Coordinate(row=3, column=0),
        Coordinate(row=0, column=3),
    ],
)
def test_apply_rejects_coordinate_outside_board(
    coordinate: Coordinate,
) -> None:
    game = load_tictactoe()
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=coordinate,
    )

    with pytest.raises(InvalidMoveError, match="outside"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_unknown_piece_type() -> None:
    game = load_tictactoe()
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Unknown",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="Unknown piece type"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_piece_not_owned_by_player() -> None:
    game = load_tictactoe()
    mark = next(piece for piece in game.pieces if piece.name == "Mark")
    restricted_mark = replace(mark, owners=("O",))
    restricted_game = replace(
        game,
        pieces=(restricted_mark,),
    )
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="does not own"):
        MoveExecutor(restricted_game).apply(state, move)


def test_apply_rejects_occupied_cell() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=1),
            ),
        ),
        current_player="X",
        turn_number=2,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=1, column=1),
    )

    with pytest.raises(InvalidMoveError, match="already occupied"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_non_playable_cell() -> None:
    game = load_tictactoe()
    dark_board = replace(
        game.board,
        playable_cells=PlayableCells.DARK,
    )
    dark_cells_game = replace(game, board=dark_board)
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="not a playable dark cell"):
        MoveExecutor(dark_cells_game).apply(state, move)

def test_apply_marks_state_as_won_after_winning_move() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=1),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=1),
            ),
        ),
        current_player="X",
        turn_number=5,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.status is GameStatus.WON
    assert result.winner == "X"
    assert result.turn_number == 6
    assert result.current_player == "O"


def test_apply_marks_state_as_drawn_after_board_filling_move() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=0, column=1),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=2),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=1, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=1),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=2),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=2, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=2, column=1),
            ),
        ),
        current_player="X",
        turn_number=9,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=2, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.status is GameStatus.DRAWN
    assert result.winner is None
    assert result.turn_number == 10
    assert result.current_player == "O"