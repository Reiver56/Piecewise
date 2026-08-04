from parser.ast_nodes import GameDefinition

from engine.game_initializer import GameInitializer
from engine.game_state import GameState
from engine.move import Move
from engine.move_executor import MoveExecutor


class GameSession:
    """Manages the current state of a complete game session."""

    def __init__(self, game: GameDefinition) -> None:
        """Initialize a new session from a validated game definition."""
        self._move_executor = MoveExecutor(game)
        self._state = GameInitializer().initialize(game)

    @property
    def state(self) -> GameState:
        """Return the current immutable game-state snapshot."""
        return self._state

    def play(self, move: Move) -> GameState:
        """Apply a move and update the current session state."""
        self._state = self._move_executor.apply(
            self._state,
            move,
        )
        return self._state