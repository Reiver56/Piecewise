class GameEngineError(Exception):
    """Base exception for all game-engine errors"""

class GameInitializationError(GameEngineError):
    """Raised when the initial runtime state cannot be created"""

class InvalidMoveError(GameEngineError):
    """Raised when a move cannot be applied to the current game state."""