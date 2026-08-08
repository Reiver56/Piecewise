from dataclasses import replace
from pathlib import Path

from engine.board_renderer import BoardRenderer
from engine.game_state import Coordinate, GameState, PlacedPiece
from parser.ast_nodes import PlayableCells
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )


def create_state(
    *pieces: PlacedPiece,
    rows: int = 3,
    columns: int = 3,
) -> GameState:
    return GameState(
        rows=rows,
        columns=columns,
        pieces=pieces,
        current_player="X",
        turn_number=len(pieces) + 1,
    )


def placed_piece(
    owner: str,
    row: int,
    column: int,
) -> PlacedPiece:
    return PlacedPiece(
        piece_name="Mark",
        owner=owner,
        coordinate=Coordinate(row=row, column=column),
    )


def test_render_empty_board() -> None:
    renderer = BoardRenderer(load_tictactoe())

    result = renderer.render(create_state())

    assert result == (
        "    0   1   2\n"
        "0   . | . | .\n"
        "1   . | . | .\n"
        "2   . | . | ."
    )


def test_render_board_with_placed_pieces() -> None:
    renderer = BoardRenderer(load_tictactoe())
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("O", 1, 1),
        placed_piece("X", 2, 2),
    )

    result = renderer.render(state)

    assert result == (
        "    0   1   2\n"
        "0   X | . | .\n"
        "1   . | O | .\n"
        "2   . | . | X"
    )


def test_render_supports_different_board_dimensions() -> None:
    game = load_tictactoe()
    resized_game = replace(
        game,
        board=replace(
            game.board,
            rows=2,
            columns=4,
        ),
    )
    renderer = BoardRenderer(resized_game)
    state = create_state(
        placed_piece("X", 0, 3),
        rows=2,
        columns=4,
    )

    result = renderer.render(state)

    assert result == (
        "    0   1   2   3\n"
        "0   . | . | . | X\n"
        "1   . | . | . | ."
    )


def test_render_marks_non_playable_dark_board_cells() -> None:
    game = load_tictactoe()
    dark_cells_game = replace(
        game,
        board=replace(
            game.board,
            playable_cells=PlayableCells.DARK,
        ),
    )
    renderer = BoardRenderer(dark_cells_game)

    result = renderer.render(create_state())

    assert result == (
        "    0   1   2\n"
        "0   # | . | #\n"
        "1   . | # | .\n"
        "2   # | . | #"
    )


def test_render_marks_non_playable_light_board_cells() -> None:
    game = load_tictactoe()
    light_cells_game = replace(
        game,
        board=replace(
            game.board,
            playable_cells=PlayableCells.LIGHT,
        ),
    )
    renderer = BoardRenderer(light_cells_game)

    result = renderer.render(create_state())

    assert result == (
        "    0   1   2\n"
        "0   . | # | .\n"
        "1   # | . | #\n"
        "2   . | # | ."
    )