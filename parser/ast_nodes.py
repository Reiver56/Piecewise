from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


class PlayableCells(str, Enum):
    ALL = "all"
    DARK = "dark"
    LIGHT = "light"


class PlacementType(str, Enum):
    ANY_EMPTY_CELL = "any_empty_cell"


class ForwardDirection(str, Enum):
    UP = "up"
    DOWN = "down"


class MovementDirection(str, Enum):
    DIAGONAL_FORWARD = "diagonal_forward"
    DIAGONAL_ANY = "diagonal_any"


class DestinationCondition(str, Enum):
    EMPTY = "empty"

class CaptureCondition(str, Enum):
    ENEMY = "enemy"

class PromotionCondition(str, Enum):
    BACK_RANK = "back_rank"

class AlignmentDirection(str, Enum):
    SAME_ROW = "same_row"
    SAME_COL = "same_col"
    DIAGONAL = "diagonal"


class Outcome(str, Enum):
    WIN = "win"
    DRAW = "draw"

class PlayerTarget(str, Enum):
    OPPONENT = "opponent"

@dataclass(frozen=True, slots=True)
class BoardDefinition:
    rows: int
    columns: int
    playable_cells: PlayableCells


@dataclass(frozen=True, slots=True)
class PlayerDefinition:
    name: str
    forward: ForwardDirection | None = None


@dataclass(frozen=True, slots=True)
class MovementRule:
    direction: MovementDirection
    distance: int
    destination_condition: DestinationCondition


@dataclass(frozen=True, slots=True)
class CaptureRule:
    direction: MovementDirection
    distance: int
    condition: CaptureCondition

@dataclass(frozen=True, slots=True)
class PromotionRule:
    condition: PromotionCondition
    target_piece_name: str

@dataclass(frozen=True, slots=True)
class PieceDefinition:
    name: str
    owners: tuple[str, ...]
    placement: PlacementType | None = None
    movement: MovementRule | None = None
    capture: CaptureRule | None = None
    promotion: PromotionRule | None = None

@dataclass(frozen=True, slots=True)
class SetupRule:
    piece_name: str
    owner: str
    first_row: int
    last_row: int
    playable_cells_only: bool


@dataclass(frozen=True, slots=True)
class AlignCondition:
    length: int
    direction: AlignmentDirection
    outcome: Outcome = Outcome.WIN


@dataclass(frozen=True, slots=True)
class BoardFullCondition:
    outcome: Outcome = Outcome.DRAW

@dataclass(frozen=True, slots=True)
class NoPiecesLeftCondition:
    target: PlayerTarget
    outcome: Outcome = Outcome.WIN

@dataclass(frozen=True, slots=True)
class NoMovesLeftCondition:
    target: PlayerTarget
    outcome: Outcome = Outcome.WIN

WinCondition: TypeAlias = (
    AlignCondition
    | BoardFullCondition
    | NoPiecesLeftCondition
    | NoMovesLeftCondition
)
@dataclass(frozen=True, slots=True)
class GameDefinition:
    name: str
    board: BoardDefinition
    players: tuple[PlayerDefinition, ...]
    turn_order: tuple[str, ...]
    pieces: tuple[PieceDefinition, ...]
    win_conditions: tuple[WinCondition, ...]
    setup: tuple[SetupRule, ...] = ()