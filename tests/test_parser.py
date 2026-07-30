from pathlib import Path

import pytest
from lark.exceptions import UnexpectedInput

from parser.game_parser import GameParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"


@pytest.fixture(scope="module")
def game_parser() -> GameParser:
    return GameParser()


def test_parse_valid_tictactoe(game_parser: GameParser) -> None:
    tree = game_parser.parse_file(TICTACTOE_PATH)

    assert tree.data == "start"
    assert tree.children


def test_reject_incomplete_game(game_parser: GameParser) -> None:
    invalid_source = """
    game InvalidGame {
        board {
            size: 3x3
            playable_cells: all
        }
    """

    with pytest.raises(UnexpectedInput):
        game_parser.parse(invalid_source)


def test_reject_wrong_file_extension(
    game_parser: GameParser,
    tmp_path: Path,
) -> None:
    invalid_file = tmp_path / "game.txt"
    invalid_file.write_text("game Invalid {}", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Expected a \.game file"):
        game_parser.parse_file(invalid_file)