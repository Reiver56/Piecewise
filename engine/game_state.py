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

    def __post_init__(self) -> None:
        if self.rows <= 0:
            raise ValueError("Game state rows must be greater than zero.")

        if self.columns <= 0:
            raise ValueError("Game state columns must be greater than zero.")

        if self.turn_number < 1:
            raise ValueError("Turn number must be at least one.")

        if not self.current_player:
            raise ValueError("Current player cannot be empty.")

        if self.status is GameStatus.WON and self.winner is None:
            raise ValueError("A won game must have a winner.")

        if self.status is not GameStatus.WON and self.winner is not None:
            raise ValueError("Only a won game can have a winner.")

        occupied_coordinates: set[Coordinate] = set()

        for piece in self.pieces:
            coordinate = piece.coordinate

            if coordinate.row >= self.rows:
                raise ValueError(
                    f"Piece coordinate row {coordinate.row} "
                    f"is outside the {self.rows}x{self.columns} board."
                )

            if coordinate.column >= self.columns:
                raise ValueError(
                    f"Piece coordinate column {coordinate.column} "
                    f"is outside the {self.rows}x{self.columns} board."
                )

            if coordinate in occupied_coordinates:
                raise ValueError(
                    f"Multiple pieces occupy coordinate {coordinate}."
                )

            occupied_coordinates.add(coordinate)