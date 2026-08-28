from pathlib import Path

from engine.game_initializer import GameInitializer
from engine.game_state import Coordinate, GameState, PlacedPiece
from engine.legal_move_generator import LegalMoveGenerator
from engine.move import Move
from parser.game_parser import GameParser
from engine.move_executor import MoveExecutor



GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_checkers():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
    )

def load_connectfour():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "connectfour.game"
    )


def test_generate_single_forward_move_from_board_edge() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=Coordinate(row=5, column=0),
            coordinate=Coordinate(row=4, column=1),
        ),
    )

def test_generate_both_forward_diagonal_moves() -> None:
    game = load_checkers()
    source = Coordinate(row=5, column=2)
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=source,
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=source,
            coordinate=Coordinate(row=4, column=1),
        ),
        Move(
            player="White",
            piece_name="Man",
            source=source,
            coordinate=Coordinate(row=4, column=3),
        ),
    )

def test_generate_ignores_opponent_and_occupied_destination() -> None:
    game = load_checkers()
    white_source = Coordinate(row=5, column=2)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=white_source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=3, column=0)
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=white_source,
            coordinate=Coordinate(row=4, column=3),
        ),
    )

def test_generate_diagonal_any_moves_in_both_directions() -> None:
    game = load_checkers()
    source = Coordinate(row=3, column=2)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="King",
                owner="White",
                coordinate=source,
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="King",
            source=source,
            coordinate=Coordinate(row=2, column=1),
        ),
        Move(
            player="White",
            piece_name="King",
            source=source,
            coordinate=Coordinate(row=2, column=3),
        ),
        Move(
            player="White",
            piece_name="King",
            source=source,
            coordinate=Coordinate(row=4, column=1),
        ),
        Move(
            player="White",
            piece_name="King",
            source=source,
            coordinate=Coordinate(row=4, column=3),
        ),
    )

def test_generate_forward_capture_over_enemy_piece() -> None:
    game = load_checkers()
    source = Coordinate(row=5, column=0)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=source,
            coordinate=Coordinate(row=3, column=2),
        ),
    )

def test_generate_diagonal_any_backward_capture() -> None:
    game = load_checkers()
    source = Coordinate(row=3, column=2)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="King",
                owner="White",
                coordinate=source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=3),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert Move(
        player="White",
        piece_name="King",
        source=source,
        coordinate=Coordinate(row=5, column=4),
    ) in moves

def test_generate_does_not_capture_own_piece() -> None:
    game = load_checkers()
    source = Coordinate(row=5, column=0)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    invalid_capture = Move(
        player="White",
        piece_name="Man",
        source=source,
        coordinate=Coordinate(row=3, column=2),
    )

    assert invalid_capture not in moves

def test_generate_returns_empty_tuple_when_player_has_no_moves() -> None:
    game = load_checkers()

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=0, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == ()

def test_generate_returns_only_captures_when_capture_is_available() -> None:
    game = load_checkers()
    source = Coordinate(row=5, column=2)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=source,
            coordinate=Coordinate(row=3, column=0),
        ),
    )

def test_generate_suppresses_other_pieces_ordinary_moves() -> None:
    game = load_checkers()
    ordinary_source = Coordinate(row=5, column=6)
    capturing_source = Coordinate(row=5, column=0)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=ordinary_source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=capturing_source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=capturing_source,
            coordinate=Coordinate(row=3, column=2),
        ),
    )

def test_generate_limits_capture_chain_to_forced_piece() -> None:
    game = load_checkers()
    forced_source = Coordinate(row=3, column=2)

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=forced_source,
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=6),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=2, column=3),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=5),
            ),
        ),
        current_player="White",
        turn_number=1,
        forced_capture_source=forced_source,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == (
        Move(
            player="White",
            piece_name="Man",
            source=forced_source,
            coordinate=Coordinate(row=1, column=4),
        ),
    )

def test_generate_column_moves_for_empty_board() -> None:
    game = load_connectfour()
    state = GameInitializer().initialize(game)

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == tuple(
        Move(
            player="Red",
            piece_name="Disc",
            coordinate=Coordinate(
                row=0,
                column=column,
            ),
        )
        for column in range(7)
    )

def test_generate_excludes_full_connect_four_column() -> None:
    game = load_connectfour()

    pieces = tuple(
        PlacedPiece(
            piece_name="Disc",
            owner=(
                "Red"
                if row % 2 == 0
                else "Yellow"
            ),
            coordinate=Coordinate(
                row=row,
                column=2,
            ),
        )
        for row in range(6)
    )

    state = GameState(
        rows=6,
        columns=7,
        pieces=pieces,
        current_player="Red",
        turn_number=7,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert tuple(
        move.coordinate.column
        for move in moves
    ) == (
        0,
        1,
        3,
        4,
        5,
        6,
    )

    assert all(
        move.player == "Red"
        and move.piece_name == "Disc"
        and move.source is None
        and move.coordinate.row == 0
        for move in moves
    )

def test_generate_column_moves_for_next_player() -> None:
    game = load_connectfour()
    initial_state = GameInitializer().initialize(game)

    state = MoveExecutor(game).apply(
        initial_state,
        Move(
            player="Red",
            piece_name="Disc",
            coordinate=Coordinate(
                row=0,
                column=3,
            ),
        ),
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert len(moves) == 7

    assert tuple(
        move.coordinate.column
        for move in moves
    ) == tuple(range(7))

    assert all(
        move.player == "Yellow"
        and move.piece_name == "Disc"
        and move.source is None
        and move.coordinate.row == 0
        for move in moves
    )

def test_generate_returns_no_moves_when_board_is_full() -> None:
    game = load_connectfour()

    pieces = tuple(
        PlacedPiece(
            piece_name="Disc",
            owner=(
                "Red"
                if (row + column) % 2 == 0
                else "Yellow"
            ),
            coordinate=Coordinate(
                row=row,
                column=column,
            ),
        )
        for row in range(6)
        for column in range(7)
    )

    state = GameState(
        rows=6,
        columns=7,
        pieces=pieces,
        current_player="Red",
        turn_number=43,
    )

    moves = LegalMoveGenerator(game).generate(state)

    assert moves == ()