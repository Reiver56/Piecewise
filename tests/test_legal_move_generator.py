from pathlib import Path

from engine.game_state import Coordinate, GameState, PlacedPiece
from engine.legal_move_generator import LegalMoveGenerator
from engine.move import Move
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_checkers():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
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