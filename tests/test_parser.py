from pathlib import Path

import pytest
from lark.exceptions import UnexpectedInput

from parser.game_parser import GameParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"
CHECKERS_PATH = PROJECT_ROOT / "games" / "checkers.game"
CONNECTFOUR_PATH = PROJECT_ROOT / "games" / "connectfour.game"

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

def test_parse_connect_four_syntax(
    game_parser: GameParser,
) -> None:
    tree = game_parser.parse_file(CONNECTFOUR_PATH)
    rendered_tree = tree.pretty()

    assert tree.data == "start"
    assert "gravity_property" in rendered_tree
    assert "gravity_down" in rendered_tree
    assert "any_non_full_column_placement" in rendered_tree

def test_parse_gravity_rule_syntax(
    game_parser: GameParser,
) -> None:
    gravity_game_source = TICTACTOE_PATH.read_text(
        encoding="utf-8",
    ).replace(
        "playable_cells: all",
        (
            "playable_cells: all\n"
            "        gravity: down"
        ),
        1,
    )

    tree = game_parser.parse(gravity_game_source)
    rendered_tree = tree.pretty()

    assert tree.data == "start"
    assert "gravity_property" in rendered_tree
    assert "gravity_down" in rendered_tree

def test_reject_unsupported_gravity_direction(
    game_parser: GameParser,
) -> None:
    invalid_source = TICTACTOE_PATH.read_text(
        encoding="utf-8",
    ).replace(
        "playable_cells: all",
        (
            "playable_cells: all\n"
            "        gravity: up"
        ),
        1,
    )

    with pytest.raises(UnexpectedInput):
        game_parser.parse(invalid_source)

def test_parse_checkers_end_condition_syntax(
    game_parser: GameParser,
) -> None:
    tree = game_parser.parse_file(CHECKERS_PATH)
    rendered_tree = tree.pretty()

    assert tree.data == "start"
    assert "no_pieces_left_condition" in rendered_tree
    assert "no_moves_left_condition" in rendered_tree
    assert rendered_tree.count("opponent_target") == 2

def test_reject_invalid_end_condition_target(
    game_parser: GameParser,
) -> None:
    invalid_source = CHECKERS_PATH.read_text(
        encoding="utf-8",
    ).replace(
        "no_pieces_left: opponent -> win",
        "no_pieces_left: self -> win",
        1,
    )

    with pytest.raises(UnexpectedInput):
        game_parser.parse(invalid_source)

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

def test_reject_invalid_promotion_condition(
    game_parser: GameParser,
) -> None:
    invalid_source = MOVEMENT_GAME_SOURCE.replace(
        "move: diagonal forward 1 if empty",
        (
            "move: diagonal forward 1 if empty\n"
            "        promote: center_rank -> King"
        ),
        1,
    )

    with pytest.raises(UnexpectedInput):
        game_parser.parse(invalid_source)