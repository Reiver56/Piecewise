from collections.abc import Iterator
from pathlib import Path

from cli.game_cli import GameCLI
from engine.game_state import GameStatus
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
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