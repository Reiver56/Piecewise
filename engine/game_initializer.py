from parser.ast_nodes import (
    GameDefinition,
    PlayableCells,
)
from validation import SemanticValidator

from engine.errors import GameInitializationError
from engine.game_state import (
    Coordinate,
    GameState,
    PlacedPiece,
)


class GameInitializer:
    """Creates the initial runtime state of a validated game definition."""

    def __init__(
        self,
        validator: SemanticValidator | None = None,
    ) -> None:
        self._validator = validator or SemanticValidator()

    def initialize(self, game: GameDefinition) -> GameState:
        """Validate a game definition and create its initial runtime state."""
        issues = self._validator.validate(game)

        if issues:
            details = "\n".join(f"- {issue}" for issue in issues)

            raise GameInitializationError(
                "Cannot initialize an invalid game definition:\n"
                f"{details}"
            )

        if not game.turn_order:
            raise GameInitializationError(
                "Cannot initialize a game without a turn order."
            )

        return GameState(
            rows=game.board.rows,
            columns=game.board.columns,
            pieces=self._create_setup_pieces(game),
            current_player=game.turn_order[0],
            turn_number=1,
        )
    
    @staticmethod
    def _create_setup_pieces(
        game: GameDefinition,
    ) -> tuple[PlacedPiece, ...]:
        return tuple(
            PlacedPiece(
                piece_name=rule.piece_name,
                owner=rule.owner,
                coordinate=Coordinate(
                    row=row,
                    column=column,
                ),
            )
            for rule in game.setup
            for row in range(
                rule.first_row - 1,
                rule.last_row,
            )
            for column in range(game.board.columns)
            if (
                not rule.playable_cells_only
                or GameInitializer._is_playable_cell(
                    game,
                    row,
                    column,
                )
            )
        )
    
    @staticmethod
    def _is_playable_cell(
        game: GameDefinition,
        row: int,
        column: int,
    ) -> bool:
        playable_cells = game.board.playable_cells

        if playable_cells is PlayableCells.ALL:
            return True

        is_dark_cell = (row + column) % 2 == 1

        if playable_cells is PlayableCells.DARK:
            return is_dark_cell

        return not is_dark_cell