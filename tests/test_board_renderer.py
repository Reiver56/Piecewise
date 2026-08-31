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

def load_checkers():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
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

def test_render_supports_single_cell_board() -> None:
    game = load_tictactoe()
    single_cell_game = replace(
        game,
        board=replace(
            game.board,
            rows=1,
            columns=1,
        ),
    )
    renderer = BoardRenderer(single_cell_game)
    state = create_state(
        placed_piece("X", 0, 0),
        rows=1,
        columns=1,
    )

    result = renderer.render(state)

    assert result == (
        "    0\n"
        "0   X"
    )


def test_piece_is_rendered_before_cell_playability_marker() -> None:
    game = load_tictactoe()
    dark_cells_game = replace(
        game,
        board=replace(
            game.board,
            playable_cells=PlayableCells.DARK,
        ),
    )
    renderer = BoardRenderer(dark_cells_game)
    state = create_state(
        placed_piece("X", 0, 0),
    )

    result = renderer.render(state)

    assert result == (
        "    0   1   2\n"
        "0   X | . | #\n"
        "1   . | # | .\n"
        "2   # | . | #"
    )


def test_render_does_not_modify_game_state() -> None:
    renderer = BoardRenderer(load_tictactoe())
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("O", 1, 1),
    )
    pieces_before_render = state.pieces

    renderer.render(state)

    assert state.pieces is pieces_before_render
    assert state.turn_number == 3
    assert state.current_player == "X"

def test_render_uses_compact_owner_symbols() -> None:
    renderer = BoardRenderer(load_tictactoe())
    state = create_state(
        placed_piece("White", 0, 0),
        placed_piece("Black", 0, 1),
    )

    result = renderer.render(state)

    assert result == (
        "    0   1   2\n"
        "0   W | B | .\n"
        "1   . | . | .\n"
        "2   . | . | ."
    )

def test_render_distinguishes_kings_from_men() -> None:
    renderer = BoardRenderer(load_tictactoe())

    state = create_state(
        placed_piece("White", 0, 0),
        replace(
            placed_piece("White", 0, 1),
            piece_name="King",
        ),
        placed_piece("Black", 1, 0),
        replace(
            placed_piece("Black", 1, 1),
            piece_name="King",
        ),
    )

    result = renderer.render(state)

    symbols = result.replace("|", " ").split()

    assert symbols.count("W") == 1
    assert symbols.count("WK") == 1
    assert symbols.count("B") == 1
    assert symbols.count("BK") == 1

def test_render_aligns_columns_with_king_symbols() -> None:
    renderer = BoardRenderer(load_tictactoe())
    state = create_state(
        replace(
            placed_piece("White", 0, 0),
            piece_name="King",
        ),
        replace(
            placed_piece("White", 0, 0),
            piece_name="King",
        )
    )
    rows = renderer.render(state).splitlines()[1:]

    separator_positions = [
        tuple(
            index
            for index, character in enumerate(row)
            if character == "|"
        )
        for row in rows
    ]

    assert all(len(positions) == 2 for positions in separator_positions)
    assert len(set(separator_positions)) == 1

def test_render_distinguishes_kings_from_men() -> None:
    renderer = BoardRenderer(load_checkers())

    state = create_state(
        replace(
            placed_piece("White", 5, 0),
            piece_name="Man",
        ),
        replace(
            placed_piece("White", 5, 2),
            piece_name="King",
        ),
        replace(
            placed_piece("Black", 2, 1),
            piece_name="Man",
        ),
        replace(
            placed_piece("Black", 2, 3),
            piece_name="King",
        ),
        rows=8,
        columns=8,
    )

    result = renderer.render(state)
    symbols = result.replace("|", " ").split()

    assert symbols.count("W") == 1
    assert symbols.count("WK") == 1
    assert symbols.count("B") == 1
    assert symbols.count("BK") == 1


def test_render_aligns_columns_with_king_symbols() -> None:
    renderer = BoardRenderer(load_checkers())

    state = create_state(
        replace(
            placed_piece("White", 5, 2),
            piece_name="King",
        ),
        replace(
            placed_piece("Black", 2, 1),
            piece_name="Man",
        ),
        rows=8,
        columns=8,
    )

    rows = renderer.render(state).splitlines()[1:]

    separator_positions = [
        tuple(
            index
            for index, character in enumerate(row)
            if character == "|"
        )
        for row in rows
    ]

    assert len(rows) == 8
    assert all(
        len(positions) == 7
        for positions in separator_positions
    )
    assert len(set(separator_positions)) == 1    
