from dataclasses import dataclass
from typing import Any

from lark import Transformer

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    BoardDefinition,
    BoardFullCondition,
    DestinationCondition,
    ForwardDirection,
    GameDefinition,
    MovementDirection,
    MovementRule,
    PieceDefinition,
    PlacementType,
    PlayableCells,
    PlayerDefinition,
    PlayerTarget,
    SetupRule,
    WinCondition,
    CaptureCondition,
    CaptureRule,
    PromotionCondition,
    PromotionRule,
    NoMovesLeftCondition,
    NoPiecesLeftCondition,
    PlayerTarget,
)


@dataclass(frozen=True, slots=True)
class _PlayersBlock:
    players: tuple[PlayerDefinition, ...]
    turn_order: tuple[str, ...]

@dataclass
class _SetupBlock:
    rules: tuple[SetupRule, ...]

class GameAstTransformer(Transformer[Any, GameDefinition]):
    """Transform a Lark parse tree into the Piecewise domain model."""

    def start(self, children: list[Any]) -> GameDefinition:
        return children[0]

    def name_list(self, children: list[Any]) -> tuple[str, ...]:
        return tuple(str(child) for child in children)

    # Board

    def size_property(
        self,
        children: list[Any],
    ) -> tuple[str, tuple[int, int]]:
        rows, columns = children
        return "size", (int(rows), int(columns))

    def all_cells(self, children: list[Any]) -> PlayableCells:
        return PlayableCells.ALL

    def dark_cells(self, children: list[Any]) -> PlayableCells:
        return PlayableCells.DARK

    def light_cells(self, children: list[Any]) -> PlayableCells:
        return PlayableCells.LIGHT

    def playable_cells_property(
        self,
        children: list[Any],
    ) -> tuple[str, PlayableCells]:
        return "playable_cells", children[0]

    def board_block(self, children: list[Any]) -> BoardDefinition:
        properties = dict(children)
        rows, columns = properties["size"]

        return BoardDefinition(
            rows=rows,
            columns=columns,
            playable_cells=properties["playable_cells"],
        )

    # Players

    def forward_up(
        self,
        children: list[Any],
    ) -> ForwardDirection:
        return ForwardDirection.UP

    def forward_down(
        self,
        children: list[Any],
    ) -> ForwardDirection:
        return ForwardDirection.DOWN

    def forward_property(
        self,
        children: list[Any],
    ) -> tuple[str, ForwardDirection]:
        return "forward", children[0]

    def player_block(
        self,
        children: list[Any],
    ) -> dict[str, ForwardDirection]:
        return dict(children)

    def player_declaration(
        self,
        children: list[Any],
    ) -> PlayerDefinition:
        name = str(children[0])
        properties = children[1] if len(children) > 1 else {}

        return PlayerDefinition(
            name=name,
            forward=properties.get("forward"),
        )

    def turn_order(self, children: list[Any]) -> tuple[str, ...]:
        return children[0]

    def players_block(self, children: list[Any]) -> _PlayersBlock:
        players = tuple(
            child
            for child in children
            if isinstance(child, PlayerDefinition)
        )

        turn_order = next(
            child
            for child in children
            if isinstance(child, tuple)
        )

        return _PlayersBlock(
            players=players,
            turn_order=turn_order,
        )

    # Pieces

    def owner_property(
        self,
        children: list[Any],
    ) -> tuple[str, tuple[str, ...]]:
        return "owners", children[0]

    def place_property(
        self,
        children: list[Any],
    ) -> tuple[str, PlacementType]:
        return "placement", PlacementType.ANY_EMPTY_CELL

    def diagonal_forward(
        self,
        children: list[Any],
    ) -> MovementDirection:
        return MovementDirection.DIAGONAL_FORWARD

    def diagonal_any(
        self,
        children: list[Any],
    ) -> MovementDirection:
        return MovementDirection.DIAGONAL_ANY

    def empty_destination(
        self,
        children: list[Any],
    ) -> DestinationCondition:
        return DestinationCondition.EMPTY

    def enemy_capture(
        self,
        children: list[Any],
    ) -> CaptureCondition:
        return CaptureCondition.ENEMY

    def capture_property(
        self,
        children: list[Any],
    ) -> tuple[str, CaptureRule]:
        direction, distance, condition = children

        return (
            "capture",
            CaptureRule(
                direction=direction,
                distance=int(distance),
                condition=condition,
            ),
        )

    def back_rank_promotion(
        self,
        children: list[Any],
    ) -> PromotionCondition:
        return PromotionCondition.BACK_RANK

    def promote_property(
        self,
        children: list[Any],
    ) -> tuple[str, PromotionRule]:
        condition, target_piece_name = children

        return (
            "promotion",
            PromotionRule(
                condition=condition,
                target_piece_name=str(target_piece_name),
            ),
        )

    def move_property(
        self,
        children: list[Any],
    ) -> tuple[str, MovementRule]:
        direction, distance, destination_condition = children

        return (
            "movement",
            MovementRule(
                direction=direction,
                distance=int(distance),
                destination_condition=destination_condition,
            ),
        )

    def piece_block(self, children: list[Any]) -> PieceDefinition:
        name = str(children[0])
        properties = dict(children[1:])

        return PieceDefinition(
            name=name,
            owners=properties["owners"],
            placement=properties.get("placement"),
            movement=properties.get("movement"),
            capture=properties.get("capture"),
            promotion=properties.get("promotion"),
        )

    # Win conditions

    def same_row(self, children: list[Any]) -> AlignmentDirection:
        return AlignmentDirection.SAME_ROW

    def same_col(self, children: list[Any]) -> AlignmentDirection:
        return AlignmentDirection.SAME_COL

    def diagonal(self, children: list[Any]) -> AlignmentDirection:
        return AlignmentDirection.DIAGONAL

    def align_condition(self, children: list[Any]) -> AlignCondition:
        length, direction = children

        return AlignCondition(
            length=int(length),
            direction=direction,
        )

    def opponent_target(
        self,
        children: list[Any],
    ) -> PlayerTarget:
        return PlayerTarget.OPPONENT

    def board_full_condition(
        self,
        children: list[Any],
    ) -> BoardFullCondition:
        return BoardFullCondition()

    def no_pieces_left_condition(
        self,
        children: list[Any],
    ) -> NoPiecesLeftCondition:
        target = children[0]

        return NoPiecesLeftCondition(
            target=target,
        )


    def no_moves_left_condition(
        self,
        children: list[Any],
    ) -> NoMovesLeftCondition:
        target = children[0]

        return NoMovesLeftCondition(
            target=target,
        )

    def win_condition_block(
        self,
        children: list[Any],
    ) -> tuple[WinCondition, ...]:
        return tuple(children)

    # Setup

    def setup_rule(self, children: list[Any]) -> SetupRule:
        piece_name, owner, first_row, last_row = children

        return SetupRule(
            piece_name=str(piece_name),
            owner=str(owner),
            first_row=int(first_row),
            last_row=int(last_row),
            playable_cells_only=True,
        )

    def setup_block(self, children: list[Any]) -> _SetupBlock:
        return _SetupBlock(
            rules=tuple(children),
        )

    # Complete game

    def game_definition(self, children: list[Any]) -> GameDefinition:
        name = str(children[0])
        board = children[1]
        players_block = children[2]
        game_components = children[3:-1]

        pieces = tuple(
            component
            for component in game_components
            if isinstance(component, PieceDefinition)
        )

        setup_block = next(
            (
                component
                for component in game_components
                if isinstance(component, _SetupBlock)
            ),
            None,
        )

        win_conditions = children[-1]

        return GameDefinition(
            name=name,
            board=board,
            players=players_block.players,
            turn_order=players_block.turn_order,
            pieces=pieces,
            win_conditions=win_conditions,
            setup=(
                setup_block.rules
                if setup_block is not None
                else ()
            ),
        )