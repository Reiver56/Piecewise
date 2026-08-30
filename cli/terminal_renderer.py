from engine.board_renderer import BoardRenderer
from engine.game_state import Coordinate, GameState, PlacedPiece
from parser.ast_nodes import GameDefinition


RESET = "\x1b[0m"

OWNER_COLORS = {
    "X": "\x1b[95m",
    "O": "\x1b[96m",
    "Red": "\x1b[91m",
    "Yellow": "\x1b[93m",
    "White": "\x1b[97m",
    "Black": "\x1b[90m",
}


class TerminalRenderer:
    """Adds optional terminal colors to an aligned plain-text board."""

    def __init__(
        self,
        game: GameDefinition,
        *,
        use_color: bool = False,
    ) -> None:
        self._board_renderer = BoardRenderer(game)
        self._use_color = use_color

    def render(self, state: GameState) -> str:
        """Render the board, optionally coloring its piece symbols."""
        plain_board = self._board_renderer.render(state)

        if not self._use_color:
            return plain_board

        lines = plain_board.splitlines()
        rendered_lines = [lines[0]]

        piece_by_coordinate = {
            piece.coordinate: piece
            for piece in state.pieces
        }
        row_prefix_width = len(str(state.rows - 1)) + 3

        for row, line in enumerate(lines[1:]):
            prefix = line[:row_prefix_width]
            cells = line[row_prefix_width:].split(" | ")

            for column, cell in enumerate(cells):
                coordinate = Coordinate(
                    row=row,
                    column=column,
                )
                piece = piece_by_coordinate.get(coordinate)

                if piece is not None:
                    cells[column] = self._color_cell(
                        cell,
                        piece,
                    )

            rendered_lines.append(
                prefix + " | ".join(cells)
            )

        return "\n".join(rendered_lines)

    @staticmethod
    def _color_cell(
        cell: str,
        piece: PlacedPiece,
    ) -> str:
        color = OWNER_COLORS.get(piece.owner)

        if color is None:
            return cell

        symbol = cell.lstrip(" ")
        padding = cell[:len(cell) - len(symbol)]

        return f"{padding}{color}{symbol}{RESET}"