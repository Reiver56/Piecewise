from parser.ast_nodes import GameDefinition, PlayableCells

from engine.game_state import Coordinate, GameState


class BoardRenderer:
    """Renders a game-state board as plain text."""

    EMPTY_CELL = "."
    NON_PLAYABLE_CELL = "#"

    def __init__(self, game: GameDefinition) -> None:
        self._game = game

    def render(self, state: GameState) -> str:
        """Return a textual representation of the current board."""
        header = self._render_header(state.columns)
        rows = [
            self._render_row(state, row)
            for row in range(state.rows)
        ]

        return "\n".join((header, *rows))

    def _render_header(self, columns: int) -> str:
        return "    " + "   ".join(
            str(column)
            for column in range(columns)
        )

    def _render_row(
        self,
        state: GameState,
        row: int,
    ) -> str:
        cells = [
            self._render_cell(
                state,
                Coordinate(row=row, column=column),
            )
            for column in range(state.columns)
        ]

        return f"{row}   " + " | ".join(cells)

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
            return piece.owner

        if not self._is_playable(coordinate):
            return self.NON_PLAYABLE_CELL

        return self.EMPTY_CELL

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