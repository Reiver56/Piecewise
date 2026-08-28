from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

from cli.game_cli import GameCLI
from engine.game_state import Coordinate, GameStatus

from parser.ast_nodes import SetupRule
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

def load_connectfour():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "connectfour.game"
    )

def create_cli(
    inputs: list[str],
) -> tuple[GameCLI, list[str]]:
    input_iterator: Iterator[str] = iter(inputs)
    outputs: list[str] = []

    cli = GameCLI(
        load_tictactoe(),
        input_function=lambda _: next(input_iterator),
        output_function=outputs.append,
    )

    return cli, outputs

def create_checkers_cli(
    inputs: list[str],
) -> tuple[GameCLI, list[str]]:
    input_iterator: Iterator[str] = iter(inputs)
    outputs: list[str] = []

    cli = GameCLI(
        load_checkers(),
        input_function=lambda _: next(input_iterator),
        output_function=outputs.append,
    )

    return cli, outputs

def create_connectfour_cli(
    inputs: list[str],
) -> tuple[GameCLI, list[str]]:
    input_iterator: Iterator[str] = iter(inputs)
    outputs: list[str] = []

    cli = GameCLI(
        load_connectfour(),
        input_function=lambda _: next(input_iterator),
        output_function=outputs.append,
    )

    return cli, outputs

def test_run_can_be_abandoned_with_quit() -> None:
    cli, outputs = create_cli(["quit"])

    result = cli.run()

    assert result.status is GameStatus.ONGOING
    assert result.turn_number == 1
    assert result.pieces == ()
    assert outputs[0] == "Piecewise — TicTacToe"
    assert outputs[-1] == "Game abandoned."


def test_run_accepts_quit_case_insensitively() -> None:
    cli, outputs = create_cli(["  QUIT  "])

    result = cli.run()

    assert result.status is GameStatus.ONGOING
    assert outputs[-1] == "Game abandoned."


def test_run_recovers_from_invalid_input_format() -> None:
    cli, outputs = create_cli(
        [
            "0",
            "quit",
        ]
    )

    result = cli.run()

    assert result.status is GameStatus.ONGOING
    assert (
        "Invalid move: Enter a move using the format: "
        "row column."
    ) in outputs
    assert outputs[-1] == "Game abandoned."


def test_run_recovers_from_non_integer_coordinates() -> None:
    cli, outputs = create_cli(
        [
            "top left",
            "quit",
        ]
    )

    result = cli.run()

    assert result.status is GameStatus.ONGOING
    assert (
        "Invalid move: Row and column must be integers."
    ) in outputs
    assert outputs[-1] == "Game abandoned."


def test_run_recovers_from_invalid_game_move() -> None:
    cli, outputs = create_cli(
        [
            "0 0",
            "0 0",
            "quit",
        ]
    )

    result = cli.run()

    assert result.status is GameStatus.ONGOING
    assert result.turn_number == 2
    assert len(result.pieces) == 1
    assert any(
        output.startswith("Invalid move:")
        and "occupied" in output.lower()
        for output in outputs
    )
    assert outputs[-1] == "Game abandoned."

def test_run_completes_game_with_winner() -> None:
    cli, outputs = create_cli(
        [
            "0 0",  # X
            "1 0",  # O
            "0 1",  # X
            "1 1",  # O
            "0 2",  # X wins
        ]
    )

    result = cli.run()

    assert result.status is GameStatus.WON
    assert result.winner == "X"
    assert result.turn_number == 6
    assert len(result.pieces) == 5
    assert outputs[-1] == "Player X wins!"
    assert (
        "    0   1   2\n"
        "0   X | X | X\n"
        "1   O | O | .\n"
        "2   . | . | ."
    ) in outputs


def test_run_completes_game_with_draw() -> None:
    cli, outputs = create_cli(
        [
            "0 0",  # X
            "0 1",  # O
            "0 2",  # X
            "1 1",  # O
            "1 0",  # X
            "1 2",  # O
            "2 1",  # X
            "2 0",  # O
            "2 2",  # X — draw
        ]
    )

    result = cli.run()

    assert result.status is GameStatus.DRAWN
    assert result.winner is None
    assert result.turn_number == 10
    assert len(result.pieces) == 9
    assert outputs[-1] == "The game ended in a draw."
    assert (
        "    0   1   2\n"
        "0   X | O | X\n"
        "1   X | O | O\n"
        "2   O | X | X"
    ) in outputs

def test_run_accepts_relocation_coordinates_for_checkers() -> None:
    input_iterator: Iterator[str] = iter(
        [
            "5 0 4 1",
            "quit",
        ]
    )
    outputs: list[str] = []

    cli = GameCLI(
        load_checkers(),
        input_function=lambda _: next(input_iterator),
        output_function=outputs.append,
    )

    result = cli.run()

    assert not any(
        piece.coordinate == Coordinate(row=5, column=0)
        for piece in result.pieces
    )
    assert any(
        piece.piece_name == "Man"
        and piece.owner == "White"
        and piece.coordinate == Coordinate(row=4, column=1)
        for piece in result.pieces
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert outputs[-1] == "Game abandoned."

def test_run_requires_relocation_format_for_checkers() -> None:
    cli, outputs = create_checkers_cli(
        [
            "4 1",
            "quit",
        ]
    )

    result = cli.run()

    assert result.current_player == "White"
    assert result.turn_number == 1
    assert (
        "Invalid move: Enter a relocation using the format: "
        "source_row source_column "
        "destination_row destination_column."
    ) in outputs
    assert outputs[-1] == "Game abandoned."

def test_run_recovers_from_non_integer_relocation_coordinates() -> None:
    cli, outputs = create_checkers_cli(
        [
            "five zero four one",
            "quit",
        ]
    )

    result = cli.run()

    assert result.current_player == "White"
    assert result.turn_number == 1
    assert (
        "Invalid move: Source and destination coordinates "
        "must be integers."
    ) in outputs
    assert outputs[-1] == "Game abandoned."

def test_run_recovers_from_empty_relocation_source() -> None:
    cli, outputs = create_checkers_cli(
        [
            "4 1 3 2",
            "quit",
        ]
    )

    result = cli.run()

    assert result.current_player == "White"
    assert result.turn_number == 1
    assert (
        "Invalid move: Source coordinate "
        "Coordinate(row=4, column=1) "
        "does not contain a piece."
    ) in outputs
    assert outputs[-1] == "Game abandoned."

def test_run_rejects_opponent_relocation_source() -> None:
    cli, outputs = create_checkers_cli(
        [
            "2 1 3 0",
            "quit",
        ]
    )

    result = cli.run()

    assert result.current_player == "White"
    assert result.turn_number == 1
    assert any(
        output.startswith("Invalid move:")
        and "does not own" in output
        for output in outputs
    )
    assert outputs[-1] == "Game abandoned."

def test_run_completes_chained_capture_for_checkers() -> None:
    game = load_checkers()
    chain_game = replace(
        game,
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

    input_iterator: Iterator[str] = iter(
        [
            "5 0 3 2",
            "3 2 1 4",
            "quit",
        ]
    )
    outputs: list[str] = []

    cli = GameCLI(
        chain_game,
        input_function=lambda _: next(input_iterator),
        output_function=outputs.append,
    )

    result = cli.run()

    assert any(
        piece.owner == "White"
        and piece.piece_name == "Man"
        and piece.coordinate == Coordinate(row=1, column=4)
        for piece in result.pieces
    )

    captured_coordinates = {
        Coordinate(row=4, column=1),
        Coordinate(row=2, column=3),
    }

    assert not any(
        piece.owner == "Black"
        and piece.coordinate in captured_coordinates
        for piece in result.pieces
    )

    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.forced_capture_source is None
    assert outputs[-1] == "Game abandoned."

def test_run_accepts_column_input_for_connect_four() -> None:
    cli, outputs = create_connectfour_cli(
        [
            "3",
            "quit",
        ]
    )

    result = cli.run()

    assert len(result.pieces) == 1

    assert result.pieces[0].piece_name == "Disc"
    assert result.pieces[0].owner == "Red"
    assert result.pieces[0].coordinate == Coordinate(
        row=5,
        column=3,
    )

    assert result.current_player == "Yellow"
    assert result.turn_number == 2
    assert result.status is GameStatus.ONGOING
    assert outputs[-1] == "Game abandoned."

def test_run_completes_connect_four_with_vertical_win() -> None:
    cli, outputs = create_connectfour_cli(
        [
            "0",  # Red
            "1",  # Yellow
            "0",  # Red
            "1",  # Yellow
            "0",  # Red
            "1",  # Yellow
            "0",  # Red wins
        ]
    )

    result = cli.run()

    assert result.status is GameStatus.WON
    assert result.winner == "Red"
    assert result.turn_number == 8
    assert len(result.pieces) == 7

    red_coordinates = {
        piece.coordinate
        for piece in result.pieces
        if piece.owner == "Red"
    }

    assert red_coordinates == {
        Coordinate(row=5, column=0),
        Coordinate(row=4, column=0),
        Coordinate(row=3, column=0),
        Coordinate(row=2, column=0),
    }

    assert outputs[-1] == "Player Red wins!"


def test_run_recovers_from_invalid_connect_four_format() -> None:
    cli, outputs = create_connectfour_cli(
        [
            "0 1",
            "quit",
        ]
    )

    result = cli.run()

    assert result.pieces == ()
    assert (
        "Invalid move: Enter a placement using the format: "
        "column."
    ) in outputs
    assert outputs[-1] == "Game abandoned."


def test_run_recovers_from_non_integer_connect_four_column() -> None:
    cli, outputs = create_connectfour_cli(
        [
            "left",
            "quit",
        ]
    )

    result = cli.run()

    assert result.pieces == ()
    assert "Invalid move: Column must be an integer." in outputs
    assert outputs[-1] == "Game abandoned."


def test_run_recovers_from_out_of_bounds_connect_four_column() -> None:
    cli, outputs = create_connectfour_cli(
        [
            "7",
            "quit",
        ]
    )

    result = cli.run()

    assert result.pieces == ()
    assert result.current_player == "Red"
    assert result.turn_number == 1
    assert any(
        output.startswith("Invalid move:")
        and "outside the 6x7 board" in output
        for output in outputs
    )
    assert outputs[-1] == "Game abandoned."


def test_run_recovers_from_full_connect_four_column() -> None:
    cli, outputs = create_connectfour_cli(
        [
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "quit",
        ]
    )

    result = cli.run()

    assert len(result.pieces) == 6
    assert result.current_player == "Red"
    assert result.turn_number == 7
    assert result.status is GameStatus.ONGOING
    assert "Invalid move: Column 0 is full." in outputs
    assert outputs[-1] == "Game abandoned."
