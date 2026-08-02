from parser.ast_nodes import GameDefinition
from validation import SemanticValidator

from engine.errors import GameInitializationError
from engine.game_state import GameState


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
            pieces=(),
            current_player=game.turn_order[0],
            turn_number=1,
        )