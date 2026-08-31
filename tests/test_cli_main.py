from pathlib import Path

import pytest

from cli import __main__ as cli_main


@pytest.mark.parametrize(
    (
        "is_terminal",
        "disabled",
        "no_color_env",
        "terminal_type",
        "expected",
    ),
    [
        (True, False, None, "xterm", True),
        (False, False, None, "xterm", False),
        (True, True, None, "xterm", False),
        (True, False, "1", "xterm", False),
        (True, False, None, "dumb", False),
    ],
)
def test_should_use_color(
    monkeypatch: pytest.MonkeyPatch,
    is_terminal: bool,
    disabled: bool,
    no_color_env: str | None,
    terminal_type: str,
    expected: bool,
) -> None:
    monkeypatch.setattr(
        cli_main.sys.stdout,
        "isatty",
        lambda: is_terminal,
    )
    monkeypatch.setenv("TERM", terminal_type)

    if no_color_env is None:
        monkeypatch.delenv("NO_COLOR", raising=False)
    else:
        monkeypatch.setenv("NO_COLOR", no_color_env)

    result = cli_main.should_use_color(
        no_color=disabled,
    )

    assert result is expected


def test_argument_parser_accepts_no_color() -> None:
    parser = cli_main.build_argument_parser()

    arguments = parser.parse_args(
        ["games/checkers.game", "--no-color"]
    )

    assert arguments.game == Path("games/checkers.game")
    assert arguments.no_color is True