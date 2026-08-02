from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    BoardFullCondition,
    GameDefinition,
    Outcome,
    PlacementType,
    PlayableCells,
)
#from parser.ast_transformer import GameAstTransformer
from parser.game_parser import GameParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TICTACTOE_PATH = PROJECT_ROOT / "games" / "tictactoe.game"


@pytest.fixture(scope="module")
def tictactoe_game() -> GameDefinition:
    parser = GameParser()
    return parser.parse_game_file(TICTACTOE_PATH)


def test_transform_tictactoe_definition(
    tictactoe_game: GameDefinition,
) -> None:
    assert tictactoe_game.name == "TicTacToe"

    assert tictactoe_game.board.rows == 3
    assert tictactoe_game.board.columns == 3
    assert tictactoe_game.board.playable_cells is PlayableCells.ALL

    assert tuple(
        player.name for player in tictactoe_game.players
    ) == ("X", "O")

    assert tictactoe_game.turn_order == ("X", "O")

    assert len(tictactoe_game.pieces) == 1

    mark = tictactoe_game.pieces[0]

    assert mark.name == "Mark"
    assert mark.owners == ("X", "O")
    assert mark.placement is PlacementType.ANY_EMPTY_CELL


def test_transform_win_conditions(
    tictactoe_game: GameDefinition,
) -> None:
    assert tictactoe_game.win_conditions == (
        AlignCondition(
            length=3,
            direction=AlignmentDirection.SAME_ROW,
            outcome=Outcome.WIN,
        ),
        AlignCondition(
            length=3,
            direction=AlignmentDirection.SAME_COL,
            outcome=Outcome.WIN,
        ),
        AlignCondition(
            length=3,
            direction=AlignmentDirection.DIAGONAL,
            outcome=Outcome.WIN,
        ),
        BoardFullCondition(outcome=Outcome.DRAW),
    )


def test_ast_is_immutable(
    tictactoe_game: GameDefinition,
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(tictactoe_game, "name", "ModifiedGame")