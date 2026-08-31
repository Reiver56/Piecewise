from argparse import ArgumentParser
import os
from pathlib import Path
import sys

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
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable terminal colors",
    )
    return parser


def should_use_color(*, no_color: bool = False) -> bool:
    """Enable colors for terminal output unless explicitly disabled."""
    return (
        not no_color
        and sys.stdout.isatty()
        and not os.environ.get("NO_COLOR")
        and os.environ.get("TERM", "").lower() != "dumb"
    )


def main() -> None:
    """Load the selected game and start its interactive CLI."""
    arguments = build_argument_parser().parse_args()
    game = GameParser().parse_game_file(arguments.game)

    GameCLI(
        game,
        use_color=should_use_color(
            no_color=arguments.no_color,
        ),
    ).run()


if __name__ == "__main__":
    main()