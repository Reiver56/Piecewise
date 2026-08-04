from dataclasses import dataclass

from engine.game_state import Coordinate


@dataclass(frozen=True, slots=True)
class Move:
    """A request to place a piece on the runtime board."""

    player: str
    piece_name: str
    coordinate: Coordinate

    def __post_init__(self) -> None:
        if not self.player:
            raise ValueError("Move player cannot be empty.")

        if not self.piece_name:
            raise ValueError("Move piece name cannot be empty.")