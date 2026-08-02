from dataclasses import dataclass
from enum import Enum


class GameStatus(str, Enum):
    """Possible lifecycle states of a running game."""

    ONGOING = "ongoing"
    WON = "won"
    DRAWN = "drawn"


@dataclass(frozen=True, slots=True, order=True)
class Coordinate:
    """A zero-based position on the runtime board."""

    row: int
    column: int

    def __post_init__(self) -> None:
        if self.row < 0:
            raise ValueError("Coordinate row cannot be negative.")

        if self.column < 0:
            raise ValueError("Coordinate column cannot be negative.")


@dataclass(frozen=True, slots=True)
class PlacedPiece:
    """A piece currently placed on the runtime board."""

    piece_name: str
    owner: str
    coordinate: Coordinate


@dataclass(frozen=True, slots=True)
class GameState:
    """Immutable snapshot of a running Piecewise game."""

    rows: int
    columns: int
    pieces: tuple[PlacedPiece, ...]
    current_player: str
    turn_number: int
    status: GameStatus = GameStatus.ONGOING
    winner: str | None = None