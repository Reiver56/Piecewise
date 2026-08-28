from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from gui.game_controller import GameController
from gui.theme import (
    BACKGROUND,
    BODY_FONT,
    BORDER,
    BUTTON_FONT,
    CARD_TITLE_FONT,
    MUTED_TEXT,
    PRIMARY,
    PRIMARY_HOVER,
    SUBTITLE_FONT,
    SURFACE,
    SURFACE_HOVER,
    TEXT,
    TITLE_FONT,
)
from gui.game_view import GameView
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"

GAME_OPTIONS = (
    (
        "Tic-Tac-Toe",
        "Place marks and align three symbols.",
        "tictactoe.game",
    ),
    (
        "Connect Four",
        "Drop discs and align four symbols.",
        "connectfour.game",
    ),
    (
        "Checkers",
        "Move, capture, chain, and promote pieces.",
        "checkers.game",
    ),
)


class PiecewiseApp(tk.Tk):
    """Main graphical application for Piecewise."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Piecewise")
        self.geometry("900x700")
        self.minsize(720, 600)
        self.configure(background=BACKGROUND)

        self._content = tk.Frame(
            self,
            background=BACKGROUND,
        )
        self._content.pack(
            fill=tk.BOTH,
            expand=True,
            padx=48,
            pady=36,
        )

        self.show_game_selector()

    def show_game_selector(self) -> None:
        """Display the available game definitions."""
        self._clear_content()

        tk.Label(
            self._content,
            text="Piecewise",
            background=BACKGROUND,
            foreground=TEXT,
            font=TITLE_FONT,
        ).pack(pady=(20, 4))

        tk.Label(
            self._content,
            text=(
                "Choose a game defined through "
                "the Piecewise DSL"
            ),
            background=BACKGROUND,
            foreground=MUTED_TEXT,
            font=SUBTITLE_FONT,
        ).pack(pady=(0, 30))

        cards = tk.Frame(
            self._content,
            background=BACKGROUND,
        )
        cards.pack(
            fill=tk.BOTH,
            expand=True,
        )

        for title, description, filename in GAME_OPTIONS:
            self._create_game_card(
                cards,
                title,
                description,
                filename,
            )

    def _create_game_card(
        self,
        parent: tk.Widget,
        title: str,
        description: str,
        filename: str,
    ) -> None:
        card = tk.Frame(
            parent,
            background=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=24,
            pady=20,
        )
        card.pack(
            fill=tk.X,
            pady=8,
        )

        tk.Label(
            card,
            text=title,
            background=SURFACE,
            foreground=TEXT,
            font=CARD_TITLE_FONT,
            anchor=tk.W,
        ).pack(fill=tk.X)

        tk.Label(
            card,
            text=description,
            background=SURFACE,
            foreground=MUTED_TEXT,
            font=BODY_FONT,
            anchor=tk.W,
        ).pack(
            fill=tk.X,
            pady=(6, 16),
        )

        button = tk.Button(
            card,
            text="Play",
            command=lambda: self._open_game(filename),
            background=PRIMARY,
            activebackground=PRIMARY_HOVER,
            foreground=TEXT,
            activeforeground=TEXT,
            font=BUTTON_FONT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            padx=22,
            pady=10,
        )
        button.pack(anchor=tk.E)

        button.bind(
            "<Enter>",
            lambda _: button.configure(
                background=PRIMARY_HOVER,
            ),
        )
        button.bind(
            "<Leave>",
            lambda _: button.configure(
                background=PRIMARY,
            ),
        )

    def _open_game(self, filename: str) -> None:
        try:
            game = GameParser().parse_game_file(
                GAMES_DIRECTORY / filename
            )
            controller = GameController(game)
        except Exception as error:
            messagebox.showerror(
                "Unable to load game",
                str(error),
                parent=self,
            )
            return

        self._show_game(controller)

    def _show_game(
        self,
        controller: GameController,
    ) -> None:
        self._clear_content()
    
        game_view = GameView(
            self._content,
            controller,
            on_back=self.show_game_selector,
        )
        game_view.pack(
            fill=tk.BOTH,
            expand=True,
        )

    def _clear_content(self) -> None:
        for widget in self._content.winfo_children():
            widget.destroy()


def main() -> None:
    app = PiecewiseApp()
    app.mainloop()