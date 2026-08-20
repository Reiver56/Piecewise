from dataclasses import dataclass

from engine.game_state import Coordinate


@dataclass(frozen=True, slots=True)
class Move:
    """A request to place or relocate a piece on the runtime board."""

    player: str
    piece_name: str
    coordinate: Coordinate
    source: Coordinate | None = None

    def __post_init__(self) -> None:
        if not self.player:
            raise ValueError("Move player cannot be empty.")

        if not self.piece_name:
            raise ValueError("Move piece name cannot be empty.")

        if self.source == self.coordinate:
            raise ValueError(
                "Move source and destination must be different."
            )

    @property
    def destination(self) -> Coordinate:
        """Return the destination coordinate of the move."""
        return self.coordinate

    @property
    def is_placement(self) -> bool:
        """Return whether the move places a new piece."""
        return self.source is None

    @property
    def is_relocation(self) -> bool:
        """Return whether the move relocates an existing piece."""
        return self.source is not None