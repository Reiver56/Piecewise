from pathlib import Path

import pytest
from lark.exceptions import UnexpectedInput

from parser.game_parser import GameParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"

MOVEMENT_GAME_SOURCE = """
game MovementGame {
    board {
        size: 8x8
        playable_cells: dark
    }

    players {
        player White {
            forward: up
        }

        player Black {
            forward: down
        }

        turn_order: White, Black
    }

    piece Man {
        owner: White, Black
        move: diagonal forward 1 if empty
    }

    piece King {
        owner: White, Black
        move: diagonal any 1 if empty
    }

    win_condition {
        board_full: no_winner -> draw
    }
}
"""

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

def test_parse_movement_rule_syntax(
    game_parser: GameParser,
) -> None:
    tree = game_parser.parse(MOVEMENT_GAME_SOURCE)
    rendered_tree = tree.pretty()

    assert tree.data == "start"
    assert rendered_tree.count("forward_property") == 2
    assert rendered_tree.count("move_property") == 2
    assert "diagonal_forward" in rendered_tree
    assert "diagonal_any" in rendered_tree
    assert "empty_destination" in rendered_tree

@pytest.mark.parametrize(
    "invalid_source",
    [
        MOVEMENT_GAME_SOURCE.replace(
            "forward: up",
            "forward: sideways",
            1,
        ),
        MOVEMENT_GAME_SOURCE.replace(
            "diagonal forward",
            "orthogonal forward",
            1,
        ),
    ],
)
def test_reject_invalid_movement_syntax(
    game_parser: GameParser,
    invalid_source: str,
) -> None:
    with pytest.raises(UnexpectedInput):
        game_parser.parse(invalid_source)

def test_reject_invalid_capture_condition(
    game_parser: GameParser,
) -> None:
    invalid_source = MOVEMENT_GAME_SOURCE.replace(
        "move: diagonal forward 1 if empty",
        (
            "move: diagonal forward 1 if empty\n"
            "        capture: diagonal forward 2 if friend"
        ),
        1,
    )

    with pytest.raises(UnexpectedInput):
        game_parser.parse(invalid_source)