from dataclasses import replace

from parser.ast_nodes import (
    ForwardDirection,
    GameDefinition,
    MovementDirection,
    PieceDefinition,
    PlayableCells,
)

from engine.condition_evaluator import ConditionEvaluator
from engine.errors import InvalidMoveError
from engine.game_state import (
    Coordinate,
    GameState,
    GameStatus,
    PlacedPiece,
)
from engine.move import Move


class MoveExecutor:
    """Applies valid placement or relocation moves."""

    def __init__(self, game: GameDefinition) -> None:
        self._game = game

    def apply(self, state: GameState, move: Move) -> GameState:
        """Apply a valid move and return the resulting state."""
        self._validate_game_is_ongoing(state)
        self._validate_player_turn(state, move)
        self._validate_coordinate(
            state,
            move.destination,
        )
        self._validate_playable_cell(move.destination)

        piece_definition = self._validate_piece(move)

        self._validate_cell_is_empty(
            state,
            move.destination,
        )

        if move.is_placement:
            updated_pieces = self._apply_placement(
                state,
                move,
                piece_definition,
            )
        else:
            updated_pieces = self._apply_relocation(
                state,
                move,
                piece_definition,
            )

        updated_state = GameState(
            rows=state.rows,
            columns=state.columns,
            pieces=updated_pieces,
            current_player=self._next_player(move.player),
            turn_number=state.turn_number + 1,
        )

        return ConditionEvaluator(self._game).evaluate(
            updated_state,
            move,
        )

    def _apply_placement(
        self,
        state: GameState,
        move: Move,
        piece_definition: PieceDefinition,
    ) -> tuple[PlacedPiece, ...]:
        if piece_definition.placement is None:
            raise InvalidMoveError(
                f"Piece '{piece_definition.name}' "
                "does not support placement."
            )

        placed_piece = PlacedPiece(
            piece_name=move.piece_name,
            owner=move.player,
            coordinate=move.destination,
        )

        return (*state.pieces, placed_piece)

    def _apply_relocation(
        self,
        state: GameState,
        move: Move,
        piece_definition: PieceDefinition,
    ) -> tuple[PlacedPiece, ...]:
        source = move.source

        if source is None:
            raise InvalidMoveError(
                "A relocation move requires a source coordinate."
            )

        self._validate_coordinate(state, source)
        self._validate_playable_cell(source)

        movement = piece_definition.movement

        if movement is None:
            raise InvalidMoveError(
                f"Piece '{piece_definition.name}' "
                "does not support relocation."
            )

        source_piece = next(
            (
                piece
                for piece in state.pieces
                if piece.coordinate == source
            ),
            None,
        )

        if source_piece is None:
            raise InvalidMoveError(
                f"Coordinate {source} does not contain a piece."
            )

        if source_piece.owner != move.player:
            raise InvalidMoveError(
                f"Player '{move.player}' does not own "
                f"the piece at coordinate {source}."
            )

        if source_piece.piece_name != move.piece_name:
            raise InvalidMoveError(
                f"Piece at coordinate {source} is "
                f"'{source_piece.piece_name}', "
                f"not '{move.piece_name}'."
            )

        self._validate_relocation_geometry(
            move,
            piece_definition,
        )

        return tuple(
            replace(
                piece,
                coordinate=move.destination,
            )
            if piece is source_piece
            else piece
            for piece in state.pieces
        )

    def _validate_relocation_geometry(
        self,
        move: Move,
        piece_definition: PieceDefinition,
    ) -> None:
        source = move.source
        movement = piece_definition.movement

        if source is None or movement is None:
            return

        row_delta = move.destination.row - source.row
        column_delta = (
            move.destination.column - source.column
        )
        distance = movement.distance

        if (
            abs(row_delta) != distance
            or abs(column_delta) != distance
        ):
            raise InvalidMoveError(
                f"Piece '{piece_definition.name}' must move "
                f"diagonally by {distance} cell(s)."
            )

        if (
            movement.direction
            is MovementDirection.DIAGONAL_ANY
        ):
            return

        forward = self._forward_direction(move.player)

        expected_row_delta = (
            -distance
            if forward is ForwardDirection.UP
            else distance
        )

        if row_delta != expected_row_delta:
            raise InvalidMoveError(
                f"Player '{move.player}' must move "
                f"piece '{piece_definition.name}' forward."
            )

    def _forward_direction(
        self,
        player_name: str,
    ) -> ForwardDirection:
        player = next(
            (
                player
                for player in self._game.players
                if player.name == player_name
            ),
            None,
        )

        if player is None or player.forward is None:
            raise InvalidMoveError(
                f"Player '{player_name}' has no "
                "forward direction."
            )

        return player.forward

    def _validate_game_is_ongoing(
        self,
        state: GameState,
    ) -> None:
        if state.status is not GameStatus.ONGOING:
            raise InvalidMoveError(
                "Cannot apply a move after the game has ended."
            )

    def _validate_player_turn(
        self,
        state: GameState,
        move: Move,
    ) -> None:
        if move.player != state.current_player:
            raise InvalidMoveError(
                f"It is {state.current_player}'s turn, "
                f"not {move.player}'s."
            )

    def _validate_coordinate(
        self,
        state: GameState,
        coordinate: Coordinate,
    ) -> None:
        if (
            coordinate.row >= state.rows
            or coordinate.column >= state.columns
        ):
            raise InvalidMoveError(
                f"Coordinate {coordinate} is outside the "
                f"{state.rows}x{state.columns} board."
            )

    def _validate_playable_cell(
        self,
        coordinate: Coordinate,
    ) -> None:
        playable_cells = self._game.board.playable_cells

        if playable_cells is PlayableCells.ALL:
            return

        is_dark_cell = (
            coordinate.row + coordinate.column
        ) % 2 == 1

        if (
            playable_cells is PlayableCells.DARK
            and not is_dark_cell
        ):
            raise InvalidMoveError(
                f"Coordinate {coordinate} "
                "is not a playable dark cell."
            )

        if (
            playable_cells is PlayableCells.LIGHT
            and is_dark_cell
        ):
            raise InvalidMoveError(
                f"Coordinate {coordinate} "
                "is not a playable light cell."
            )

    def _validate_piece(
        self,
        move: Move,
    ) -> PieceDefinition:
        piece_definition = next(
            (
                piece
                for piece in self._game.pieces
                if piece.name == move.piece_name
            ),
            None,
        )

        if piece_definition is None:
            raise InvalidMoveError(
                f"Unknown piece type '{move.piece_name}'."
            )

        if move.player not in piece_definition.owners:
            raise InvalidMoveError(
                f"Player '{move.player}' does not own "
                f"piece '{move.piece_name}'."
            )

        return piece_definition

    def _validate_cell_is_empty(
        self,
        state: GameState,
        coordinate: Coordinate,
    ) -> None:
        if any(
            piece.coordinate == coordinate
            for piece in state.pieces
        ):
            raise InvalidMoveError(
                f"Coordinate {coordinate} is already occupied."
            )

    def _next_player(self, current_player: str) -> str:
        current_index = self._game.turn_order.index(
            current_player
        )
        next_index = (
            current_index + 1
        ) % len(self._game.turn_order)

        return self._game.turn_order[next_index]