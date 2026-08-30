from pathlib import Path
import re

from cli.terminal_renderer import TerminalRenderer
from engine.board_renderer import BoardRenderer
from engine.game_state import Coordinate, GameState, PlacedPiece
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )


def create_state() -> GameState:
    return GameState(
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
                coordinate=Coordinate(row=1, column=1),
            ),
        ),
        current_player="X",
        turn_number=3,
    )


def test_render_without_colors_matches_plain_board() -> None:
    game = load_tictactoe()
    state = create_state()
    renderer = TerminalRenderer(game, use_color=False)

    result = renderer.render(state)

    assert result == BoardRenderer(game).render(state)
    assert "\x1b[" not in result


def test_render_colors_pieces_without_changing_layout() -> None:
    game = load_tictactoe()
    state = create_state()
    renderer = TerminalRenderer(game, use_color=True)

    result = renderer.render(state)

    assert "\x1b[95mX\x1b[0m" in result
    assert "\x1b[96mO\x1b[0m" in result

    plain_result = re.sub(
        r"\x1b\[[0-9;]*m",
        "",
        result,
    )

    assert plain_result == BoardRenderer(game).render(state)

def test_render_colors_kings_without_changing_layout() -> None:
    game = GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
    )
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="King",
                owner="White",
                coordinate=Coordinate(row=5, column=2),
            ),
            PlacedPiece(
                piece_name="King",
                owner="Black",
                coordinate=Coordinate(row=2, column=3),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    renderer = TerminalRenderer(game, use_color=True)

    result = renderer.render(state)

    assert "\x1b[97mWK\x1b[0m" in result
    assert "\x1b[90mBK\x1b[0m" in result

    plain_result = re.sub(
        r"\x1b\[[0-9;]*m",
        "",
        result,
    )

    assert plain_result == BoardRenderer(game).render(state)
    assert result.count("\x1b[0m") == 2