from parser.ast_nodes import GameDefinition, PlayableCells

from engine.game_state import ( 
    Coordinate, 
    GameState,
    PlacedPiece,
    )


class BoardRenderer:
    """Renders a game-state board as plain text."""

    EMPTY_CELL = "."
    NON_PLAYABLE_CELL = "#"

    def __init__(self, game: GameDefinition) -> None:
        self._game = game

    def render(self, state: GameState) -> str:
        """Return an aligned textual representation of the board."""
        row_label_width = len(str(state.rows - 1))

        cell_width = max(
            1,
            len(str(state.columns - 1)),
            max(
                (
                    len(self._piece_symbol(piece))
                    for piece in state.pieces
                ),
                default=1,
            ),
        )

        header = self._render_header(
            state.columns,
            row_label_width,
            cell_width,
        )
        rows = [
            self._render_row(
                state,
                row,
                row_label_width,
                cell_width,
            )
            for row in range(state.rows)
        ]

        return "\n".join((header, *rows))

    def _render_header(
        self,
        columns: int,
        row_label_width: int,
        cell_width: int,
    ) -> str:
        prefix = " " * (row_label_width + 3)

        labels = [
            str(column).rjust(cell_width)
            for column in range(columns)
        ]

        return prefix + "   ".join(labels)

    def _render_row(
        self,
        state: GameState,
        row: int,
        row_label_width: int,
        cell_width: int,
    ) -> str:
        cells = [
            self._render_cell(
                state,
                Coordinate(row=row, column=column),
            ).rjust(cell_width)
            for column in range(state.columns)
        ]

        row_label = str(row).rjust(row_label_width)

        return f"{row_label}   " + " | ".join(cells)

    def _render_cell(
        self,
        state: GameState,
        coordinate: Coordinate,
    ) -> str:
        piece = next(
            (
                piece
                for piece in state.pieces
                if piece.coordinate == coordinate
            ),
            None,
        )

        if piece is not None:
            return self._piece_symbol(piece)

        if not self._is_playable(coordinate):
            return self.NON_PLAYABLE_CELL

        return self.EMPTY_CELL

    @staticmethod
    def _piece_symbol(piece: PlacedPiece) -> str:
        """Return the compact uppercase symbol for a piece owner."""
        if (piece.piece_name == "King"): return piece.owner[0].upper()+"K"
        else: return piece.owner[0].upper()
        
    
    def _is_playable(self, coordinate: Coordinate) -> bool:
        playable_cells = self._game.board.playable_cells

        if playable_cells is PlayableCells.ALL:
            return True

        is_dark_cell = (
            coordinate.row + coordinate.column
        ) % 2 == 1

        if playable_cells is PlayableCells.DARK:
            return is_dark_cell

        return not is_dark_cell