from dataclasses import replace
from pathlib import Path

from engine.game_session import GameSession
from engine.game_state import Coordinate, GameStatus
from engine.move import Move

from parser.ast_nodes import SetupRule
from parser.game_parser import GameParser



GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_checkers():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
    )

def create_relocation(
    player: str,
    source_row: int,
    source_column: int,
    destination_row: int,
    destination_column: int,
) -> Move:
    return Move(
        player=player,
        piece_name="Man",
        source=Coordinate(
            row=source_row,
            column=source_column,
        ),
        coordinate=Coordinate(
            row=destination_row,
            column=destination_column,
        ),
    )

def test_checkers_session_initializes_complete_setup() -> None:
    session = GameSession(load_checkers())
    state = session.state

    white_coordinates = {
        piece.coordinate
        for piece in state.pieces
        if piece.owner == "White"
    }
    black_coordinates = {
        piece.coordinate
        for piece in state.pieces
        if piece.owner == "Black"
    }

    expected_white_coordinates = {
        (row, column)
        for row in range(5, 8)
        for column in range(8)
        if (row + column) % 2 == 1
    }
    expected_black_coordinates = {
        (row, column)
        for row in range(0, 3)
        for column in range(8)
        if (row + column) % 2 == 1
    }

    assert state.rows == 8
    assert state.columns == 8
    assert len(state.pieces) == 24
    assert all(
        piece.piece_name == "Man"
        for piece in state.pieces
    )

    assert {
        (coordinate.row, coordinate.column)
        for coordinate in white_coordinates
    } == expected_white_coordinates

    assert {
        (coordinate.row, coordinate.column)
        for coordinate in black_coordinates
    } == expected_black_coordinates

    assert state.current_player == "White"
    assert state.turn_number == 1
    assert state.status is GameStatus.ONGOING
    assert state.winner is None
    assert state.forced_capture_source is None

def test_checkers_session_applies_sequential_ordinary_moves() -> None:
    session = GameSession(load_checkers())
    initial_state = session.state

    after_white_move = session.play(
        create_relocation(
            "White",
            5,
            0,
            4,
            1,
        )
    )
    after_black_move = session.play(
        create_relocation(
            "Black",
            2,
            1,
            3,
            0,
        )
    )

    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(row=5, column=0)
        for piece in initial_state.pieces
    )
    assert not any(
        piece.coordinate == Coordinate(row=4, column=1)
        for piece in initial_state.pieces
    )

    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(row=4, column=1)
        for piece in after_white_move.pieces
    )
    assert after_white_move.current_player == "Black"
    assert after_white_move.turn_number == 2
    assert after_white_move.status is GameStatus.ONGOING

    assert any(
        piece.owner == "Black"
        and piece.coordinate == Coordinate(row=3, column=0)
        for piece in after_black_move.pieces
    )
    assert not any(
        piece.coordinate == Coordinate(row=2, column=1)
        for piece in after_black_move.pieces
    )
    assert len(after_black_move.pieces) == 24
    assert after_black_move.current_player == "White"
    assert after_black_move.turn_number == 3
    assert after_black_move.status is GameStatus.ONGOING

def test_checkers_session_completes_chained_capture() -> None:
    game = replace(
        load_checkers(),
        setup=(
            SetupRule(
                piece_name="Man",
                owner="White",
                first_row=6,
                last_row=6,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=3,
                last_row=3,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=5,
                last_row=5,
                playable_cells_only=True,
            ),
        ),
    )
    session = GameSession(game)
    initial_state = session.state

    continuation_state = session.play(
        create_relocation(
            "White",
            5,
            0,
            3,
            2,
        )
    )

    assert len(initial_state.pieces) == 12
    assert len(continuation_state.pieces) == 11
    assert continuation_state.current_player == "White"
    assert continuation_state.turn_number == 1
    assert continuation_state.status is GameStatus.ONGOING
    assert continuation_state.forced_capture_source == Coordinate(
        row=3,
        column=2,
    )
    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(row=3, column=2)
        for piece in continuation_state.pieces
    )
    assert not any(
        piece.coordinate == Coordinate(row=4, column=1)
        for piece in continuation_state.pieces
    )

    completed_state = session.play(
        create_relocation(
            "White",
            3,
            2,
            1,
            4,
        )
    )

    assert len(completed_state.pieces) == 10
    assert completed_state.current_player == "Black"
    assert completed_state.turn_number == 2
    assert completed_state.status is GameStatus.ONGOING
    assert completed_state.forced_capture_source is None
    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(row=1, column=4)
        for piece in completed_state.pieces
    )
    assert not any(
        piece.owner == "Black"
        and piece.coordinate
        in {
            Coordinate(row=4, column=1),
            Coordinate(row=2, column=3),
        }
        for piece in completed_state.pieces
    )

    # The intermediate snapshot remains unchanged.
    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(row=3, column=2)
        for piece in continuation_state.pieces
    )
    assert continuation_state.forced_capture_source == Coordinate(
        row=3,
        column=2,
    )

def test_checkers_session_promotes_man_on_back_rank() -> None:
    game = replace(
        load_checkers(),
        setup=(
            SetupRule(
                piece_name="Man",
                owner="White",
                first_row=2,
                last_row=2,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=3,
                last_row=3,
                playable_cells_only=True,
            ),
        ),
    )
    session = GameSession(game)
    initial_state = session.state

    promoted_state = session.play(
        create_relocation(
            "White",
            1,
            0,
            0,
            1,
        )
    )

    assert any(
        piece.piece_name == "Man"
        and piece.owner == "White"
        and piece.coordinate == Coordinate(row=1, column=0)
        for piece in initial_state.pieces
    )
    assert not any(
        piece.coordinate == Coordinate(row=0, column=1)
        for piece in initial_state.pieces
    )

    assert any(
        piece.piece_name == "King"
        and piece.owner == "White"
        and piece.coordinate == Coordinate(row=0, column=1)
        for piece in promoted_state.pieces
    )
    assert not any(
        piece.piece_name == "Man"
        and piece.owner == "White"
        and piece.coordinate == Coordinate(row=0, column=1)
        for piece in promoted_state.pieces
    )
    assert not any(
        piece.coordinate == Coordinate(row=1, column=0)
        for piece in promoted_state.pieces
    )

    assert len(initial_state.pieces) == 8
    assert len(promoted_state.pieces) == 8
    assert promoted_state.current_player == "Black"
    assert promoted_state.turn_number == 2
    assert promoted_state.status is GameStatus.ONGOING
    assert promoted_state.winner is None
    assert promoted_state.forced_capture_source is None

def test_checkers_session_wins_after_capturing_last_enemy() -> None:
    base_game = load_checkers()
    game = replace(
        base_game,
        board=replace(
            base_game.board,
            rows=4,
            columns=3,
        ),
        setup=(
            SetupRule(
                piece_name="Man",
                owner="White",
                first_row=4,
                last_row=4,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=3,
                last_row=3,
                playable_cells_only=True,
            ),
        ),
    )
    session = GameSession(game)
    initial_state = session.state

    assert len(initial_state.pieces) == 3
    assert sum(
        piece.owner == "Black"
        for piece in initial_state.pieces
    ) == 1

    winning_state = session.play(
        create_relocation(
            "White",
            3,
            0,
            1,
            2,
        )
    )

    assert not any(
        piece.owner == "Black"
        for piece in winning_state.pieces
    )
    assert any(
        piece.owner == "White"
        and piece.coordinate == Coordinate(row=1, column=2)
        for piece in winning_state.pieces
    )

    assert winning_state.status is GameStatus.WON
    assert winning_state.winner == "White"
    assert winning_state.current_player == "Black"
    assert winning_state.turn_number == 2
    assert winning_state.forced_capture_source is None

    # The state before the capture remains unchanged.
    assert any(
        piece.owner == "Black"
        and piece.coordinate == Coordinate(row=2, column=1)
        for piece in initial_state.pieces
    )
    assert initial_state.status is GameStatus.ONGOING

def test_checkers_session_wins_when_opponent_has_no_moves() -> None:
    base_game = load_checkers()
    game = replace(
        base_game,
        board=replace(
            base_game.board,
            rows=4,
            columns=4,
        ),
        setup=(
            SetupRule(
                piece_name="Man",
                owner="White",
                first_row=3,
                last_row=3,
                playable_cells_only=True,
            ),
            SetupRule(
                piece_name="Man",
                owner="Black",
                first_row=4,
                last_row=4,
                playable_cells_only=True,
            ),
        ),
    )
    session = GameSession(game)
    initial_state = session.state

    assert sum(
        piece.owner == "Black"
        for piece in initial_state.pieces
    ) == 2

    winning_state = session.play(
        create_relocation(
            "White",
            2,
            1,
            1,
            0,
        )
    )

    # Black still owns pieces, so no_pieces_left cannot be the cause.
    assert sum(
        piece.owner == "Black"
        for piece in winning_state.pieces
    ) == 2
    assert any(
        piece.owner == "Black"
        and piece.coordinate == Coordinate(row=3, column=0)
        for piece in winning_state.pieces
    )
    assert any(
        piece.owner == "Black"
        and piece.coordinate == Coordinate(row=3, column=2)
        for piece in winning_state.pieces
    )

    assert winning_state.status is GameStatus.WON
    assert winning_state.winner == "White"
    assert winning_state.current_player == "Black"
    assert winning_state.turn_number == 2
    assert winning_state.forced_capture_source is None