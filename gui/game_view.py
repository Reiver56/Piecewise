from collections.abc import Callable
import tkinter as tk

from engine.errors import InvalidMoveError
from engine.game_state import (
    Coordinate,
    GameStatus,
    PlacedPiece,
)
from gui.game_controller import GameController
from gui.theme import (
    BACKGROUND,
    BOARD_FONT,
    BORDER,
    BUTTON_FONT,
    CARD_TITLE_FONT,
    CELL,
    CELL_HOVER,
    ERROR,
    MUTED_TEXT,
    NON_PLAYABLE_CELL,
    OWNER_COLORS,
    PRIMARY,
    PRIMARY_HOVER,
    STATUS_FONT,
    SURFACE,
    SURFACE_HOVER,
    TEXT,
    SELECTED_CELL,
    LEGAL_CELL,
    SUCCESS,
)

from parser.ast_nodes import (
    PlacementType,
    PlayableCells,
)


class GameView(tk.Frame):
    """Displays and controls one graphical game session."""

    def __init__(
        self,
        parent: tk.Misc,
        controller: GameController,
        *,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(
            parent,
            background=BACKGROUND,
        )

        self._controller = controller
        self._on_back = on_back
        self._buttons: dict[Coordinate, tk.Button] = {}

        self._build_header()
        self._build_status()
        self._build_board()
        self._build_actions()
        self._refresh()

    def _build_header(self) -> None:
        header = tk.Frame(
            self,
            background=BACKGROUND,
        )
        header.pack(
            fill=tk.X,
            pady=(0, 20),
        )

        back_button = tk.Button(
            header,
            text="← Games",
            command=self._on_back,
            background=SURFACE,
            activebackground=SURFACE_HOVER,
            foreground=TEXT,
            activeforeground=TEXT,
            font=BUTTON_FONT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            padx=16,
            pady=8,
        )
        back_button.pack(side=tk.LEFT)

        tk.Label(
            header,
            text=self._controller.game.name,
            background=BACKGROUND,
            foreground=TEXT,
            font=CARD_TITLE_FONT,
        ).pack(
            side=tk.LEFT,
            expand=True,
        )

        restart_button = tk.Button(
            header,
            text="Restart",
            command=self._restart,
            background=PRIMARY,
            activebackground=PRIMARY_HOVER,
            foreground=TEXT,
            activeforeground=TEXT,
            font=BUTTON_FONT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            padx=16,
            pady=8,
        )
        restart_button.pack(side=tk.RIGHT)

    def _build_status(self) -> None:
        self._status_label = tk.Label(
            self,
            background=BACKGROUND,
            foreground=TEXT,
            font=STATUS_FONT,
        )
        self._status_label.pack(
            pady=(0, 18),
        )

    def _build_board(self) -> None:
        board_container = tk.Frame(
            self,
            background=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=10,
            pady=10,
        )
        board_container.pack(
            expand=True,
        )

        tk.Label(
            board_container,
            text="",
            background=SURFACE,
        ).grid(row=0, column=0)

        for column in range(self._controller.state.columns):
            board_container.grid_columnconfigure(
                column + 1,
                weight=1,
            )

            tk.Label(
                board_container,
                text=str(column),
                background=SURFACE,
                foreground=MUTED_TEXT,
                font=BUTTON_FONT,
            ).grid(
                row=0,
                column=column + 1,
                pady=(0, 6),
            )

        for row in range(self._controller.state.rows):

            board_container.grid_rowconfigure(
                row + 1, 
                weight=1
            )

            tk.Label(
                board_container,
                text=str(row),
                background=SURFACE,
                foreground=MUTED_TEXT,
                font=BUTTON_FONT,
            ).grid(
                row=row + 1,
                column=0,
                padx=(0, 8),
            )

            for column in range(
                self._controller.state.columns
            ):
                board_container.grid_columnconfigure(
                    column,
                    weight=1,
                )

                coordinate = Coordinate(
                    row=row,
                    column=column,
                )

                button = tk.Button(
                    board_container,
                    text="",
                    command=lambda selected=coordinate: (
                        self._handle_cell(selected)
                    ),
                    font=BOARD_FONT,
                    relief=tk.FLAT,
                    borderwidth=1,
                    cursor="hand2",
                    width=4,
                    height=2,
                )
                button.grid(
                    row=row + 1,
                    column=column + 1,
                    padx=2,
                    pady=2,
                    sticky=tk.NSEW,
                )

                self._buttons[coordinate] = button

    def _build_actions(self) -> None:
        self._help_label = tk.Label(
            self,
            text="Select a cell to play.",
            background=BACKGROUND,
            foreground=MUTED_TEXT,
            font=BUTTON_FONT,
        )
        self._help_label.pack(
            pady=(18, 0),
        )

    def _handle_cell(
        self,
        coordinate: Coordinate,
    ) -> None:
        try:
            self._controller.handle_cell(
                coordinate.row,
                coordinate.column,
            )
        except (InvalidMoveError, ValueError) as error:
            self._status_label.configure(
                text=f"Invalid move: {error}",
                foreground=ERROR,
            )
            return

        self._refresh()

    def _restart(self) -> None:
        self._controller.restart()
        self._refresh()

    def _refresh(self) -> None:
        state = self._controller.state

        piece_by_coordinate = {
            piece.coordinate: piece
            for piece in state.pieces
        }

        legal_destinations = set(
            self._controller.legal_destinations
        )

        for coordinate, button in self._buttons.items():
            piece = piece_by_coordinate.get(coordinate)
            playable = self._is_playable(coordinate)

            selected = (
                coordinate
                == self._controller.selected_source
            )
            legal_destination = (
                coordinate in legal_destinations
            )

            if not playable:
                button.configure(
                    text="",
                    background=NON_PLAYABLE_CELL,
                    activebackground=NON_PLAYABLE_CELL,
                    state=tk.DISABLED,
                    cursor="arrow",
                    highlightthickness=0,
                )
                continue

            symbol = self._piece_symbol(piece)

            symbol_color = (
                OWNER_COLORS.get(piece.owner, TEXT)
                if piece is not None
                else TEXT
            )

            if selected:
                cell_background = SELECTED_CELL
                border_color = PRIMARY
            elif legal_destination:
                cell_background = LEGAL_CELL
                border_color = SUCCESS
            else:
                cell_background = CELL
                border_color = BORDER

            button.configure(
                text=symbol,
                background=cell_background,
                activebackground=cell_background,
                foreground=symbol_color,
                activeforeground=symbol_color,
                disabledforeground=symbol_color,
                state=(
                    tk.DISABLED
                    if state.status
                    is not GameStatus.ONGOING
                    else tk.NORMAL
                ),
                cursor=(
                    "arrow"
                    if state.status
                    is not GameStatus.ONGOING
                    else "hand2"
                ),
                relief=(
                    tk.SUNKEN
                    if selected
                    else tk.FLAT
                ),
                highlightbackground=border_color,
                highlightcolor=border_color,
                highlightthickness=(
                    3
                    if selected or legal_destination
                    else 0
                ),
            )

        self._refresh_status()

    def _refresh_status(self) -> None:
        state = self._controller.state

        if state.status is GameStatus.WON:
            self._status_label.configure(
                text=f"Player {state.winner} wins!",
                foreground=OWNER_COLORS.get(
                    state.winner,
                    TEXT,
                ),
            )
            self._help_label.configure(
                text="Restart or choose another game."
            )
            return

        if state.status is GameStatus.DRAWN:
            self._status_label.configure(
                text="The game ended in a draw.",
                foreground=MUTED_TEXT,
            )
            self._help_label.configure(
                text="Restart or choose another game."
            )
            return

        self._status_label.configure(
            text=(
                "Current player: "
                f"{state.current_player}"
            ),
            foreground=OWNER_COLORS.get(
                state.current_player,
                TEXT,
            ),
        )
        self._help_label.configure(
            text=self._ongoing_help_text()
        )

    def _ongoing_help_text(self) -> str:
        selected_source = (
            self._controller.selected_source
        )
    
        if selected_source is not None:
            return (
                "Selected source: "
                f"({selected_source.row}, "
                f"{selected_source.column}). "
                "Green cells are legal destinations; "
                "click the source again to cancel."
            )
    
        current_player = (
            self._controller.state.current_player
        )
    
        uses_relocation = any(
            piece.movement is not None
            and current_player in piece.owners
            for piece in self._controller.game.pieces
        )
    
        if uses_relocation:
            return (
                f"Select one of {current_player}'s pieces."
            )
    
        uses_column_placement = any(
            piece.placement
            is PlacementType.ANY_NON_FULL_COLUMN
            and current_player in piece.owners
            for piece in self._controller.game.pieces
        )
    
        if uses_column_placement:
            return "Select a column to drop a piece."
    
        return "Select an empty cell to place a piece."

    def _is_playable(
        self,
        coordinate: Coordinate,
    ) -> bool:
        playable_cells = (
            self._controller.game.board.playable_cells
        )

        if playable_cells is PlayableCells.ALL:
            return True

        is_dark = (
            coordinate.row + coordinate.column
        ) % 2 == 1

        if playable_cells is PlayableCells.DARK:
            return is_dark

        return not is_dark

    @staticmethod
    def _piece_symbol(
        piece: PlacedPiece | None,
    ) -> str:
        if piece is None:
            return ""

        owner_symbol = piece.owner[0].upper()

        if piece.piece_name == "King":
            return f"{owner_symbol}K"

        return owner_symbol