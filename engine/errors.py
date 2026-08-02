class GameEngineError(Exception):
    """Base exception for all game-engine errors"""

class GameInitializationError(GameEngineError):
    """Raised when the initial runtime state cannot be created"""