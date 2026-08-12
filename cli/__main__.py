from argparse import ArgumentParser
from pathlib import Path

from cli import GameCLI
from parser.game_parser import GameParser


DEFAULT_GAME_PATH = Path("games/tictactoe.game")


def build_argument_parser() -> ArgumentParser:
    """Create the command-line argument parser."""
    parser = ArgumentParser(
        prog="piecewise",
        description="Play a Piecewise board-game definition.",
    )
    parser.add_argument(
        "game",
        nargs="?",
        type=Path,
        default=DEFAULT_GAME_PATH,
        help=(
            "path to a .game definition "
            f"(default: {DEFAULT_GAME_PATH})"
        ),
    )
    return parser


def main() -> None:
    """Load the selected game and start its interactive CLI."""
    arguments = build_argument_parser().parse_args()
    game = GameParser().parse_game_file(arguments.game)
    GameCLI(game).run()


if __name__ == "__main__":
    main()
