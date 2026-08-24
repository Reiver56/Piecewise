from dataclasses import replace
from pathlib import Path

from engine.condition_evaluator import ConditionEvaluator
from engine.game_state import Coordinate, GameState, GameStatus, PlacedPiece
from engine.move import Move
from parser.ast_nodes import BoardFullCondition, PlayableCells
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


def create_state(
    *pieces: PlacedPiece,
    rows: int = 3,
    columns: int = 3,
) -> GameState:
    return GameState(
        rows=rows,
        columns=columns,
        pieces=pieces,
        current_player="O",
        turn_number=len(pieces) + 1,
    )


def create_move(
    player: str,
    row: int,
    column: int,
) -> Move:
    return Move(
        player=player,
        piece_name="Mark",
        coordinate=Coordinate(row=row, column=column),
    )


def test_evaluate_detects_same_row_win() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("X", 1, 0),
        placed_piece("X", 1, 1),
        placed_piece("X", 1, 2),
    )
    last_move = create_move("X", 1, 1)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result.status is GameStatus.WON
    assert result.winner == "X"


def test_evaluate_detects_same_column_win() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("O", 0, 2),
        placed_piece("O", 1, 2),
        placed_piece("O", 2, 2),
    )
    last_move = create_move("O", 2, 2)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result.status is GameStatus.WON
    assert result.winner == "O"


def test_evaluate_detects_descending_diagonal_win() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("X", 1, 1),
        placed_piece("X", 2, 2),
    )
    last_move = create_move("X", 2, 2)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result.status is GameStatus.WON
    assert result.winner == "X"


def test_evaluate_detects_ascending_diagonal_win() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("O", 0, 2),
        placed_piece("O", 1, 1),
        placed_piece("O", 2, 0),
    )
    last_move = create_move("O", 1, 1)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result.status is GameStatus.WON
    assert result.winner == "O"


def test_evaluate_rejects_alignment_with_different_owners() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("O", 0, 1),
        placed_piece("X", 0, 2),
    )
    last_move = create_move("X", 0, 2)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result is state
    assert result.status is GameStatus.ONGOING
    assert result.winner is None


def test_evaluate_rejects_non_consecutive_alignment() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("X", 0, 2),
    )
    last_move = create_move("X", 0, 2)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result is state
    assert result.status is GameStatus.ONGOING


def test_evaluate_detects_board_full_draw() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("O", 0, 1),
        placed_piece("X", 0, 2),
        placed_piece("X", 1, 0),
        placed_piece("O", 1, 1),
        placed_piece("O", 1, 2),
        placed_piece("O", 2, 0),
        placed_piece("X", 2, 1),
        placed_piece("X", 2, 2),
    )
    last_move = create_move("X", 2, 2)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result.status is GameStatus.DRAWN
    assert result.winner is None


def test_evaluate_prioritizes_win_over_board_full_draw() -> None:
    game = load_tictactoe()
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("O", 0, 1),
        placed_piece("O", 0, 2),
        placed_piece("O", 1, 0),
        placed_piece("X", 1, 1),
        placed_piece("X", 1, 2),
        placed_piece("O", 2, 0),
        placed_piece("O", 2, 1),
        placed_piece("X", 2, 2),
    )
    last_move = create_move("X", 2, 2)

    result = ConditionEvaluator(game).evaluate(state, last_move)

    assert result.status is GameStatus.WON
    assert result.winner == "X"


def test_board_full_considers_only_playable_cells() -> None:
    game = load_tictactoe()
    dark_board = replace(
        game.board,
        playable_cells=PlayableCells.DARK,
    )
    dark_cells_game = replace(game, board=dark_board)
    state = create_state(
        placed_piece("X", 0, 1),
        placed_piece("O", 1, 0),
        placed_piece("X", 1, 2),
        placed_piece("O", 2, 1),
    )
    last_move = create_move("O", 2, 1)

    result = ConditionEvaluator(dark_cells_game).evaluate(
        state,
        last_move,
    )

    assert result.status is GameStatus.DRAWN
    assert result.winner is None


def test_full_board_remains_ongoing_without_draw_condition() -> None:
    game = load_tictactoe()
    game_without_draw = replace(
        game,
        win_conditions=tuple(
            condition
            for condition in game.win_conditions
            if not isinstance(condition, BoardFullCondition)
        ),
    )
    state = create_state(
        placed_piece("X", 0, 0),
        placed_piece("O", 0, 1),
        placed_piece("X", 0, 2),
        placed_piece("X", 1, 0),
        placed_piece("O", 1, 1),
        placed_piece("O", 1, 2),
        placed_piece("O", 2, 0),
        placed_piece("X", 2, 1),
        placed_piece("X", 2, 2),
    )
    last_move = create_move("X", 2, 2)

    result = ConditionEvaluator(game_without_draw).evaluate(
        state,
        last_move,
    )

    assert result is state
    assert result.status is GameStatus.ONGOING

def test_evaluate_detects_no_pieces_left_win() -> None:
    game = load_checkers()

    state_after_capture = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=2, column=3),
            ),
        ),
        current_player="Black",
        turn_number=2,
    )
    last_move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=4, column=1),
        coordinate=Coordinate(row=2, column=3),
    )

    result = ConditionEvaluator(game).evaluate(
        state_after_capture,
        last_move,
    )

    assert result.status is GameStatus.WON
    assert result.winner == "White"

def test_no_pieces_left_remains_ongoing_while_opponent_has_piece() -> None:
    game = load_checkers()

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=2, column=3),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=5, column=0),
            ),
        ),
        current_player="Black",
        turn_number=2,
    )
    last_move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=4, column=1),
        coordinate=Coordinate(row=2, column=3),
    )

    result = ConditionEvaluator(game).evaluate(
        state,
        last_move,
    )

    assert result is state
    assert result.status is GameStatus.ONGOING
    assert result.winner is None