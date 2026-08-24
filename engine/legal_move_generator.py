from parser.ast_nodes import (
    DestinationCondition,
    ForwardDirection,
    GameDefinition,
    MovementDirection,
    MovementRule,
    PieceDefinition,
    PlayableCells,
    CaptureCondition,
    CaptureRule,
)
from engine.game_state import Coordinate, GameState, PlacedPiece

from engine.move import Move


class LegalMoveGenerator:
    """Generates legal moves for the current player."""

    def __init__(self, game: GameDefinition) -> None:
        self._game = game

    def generate(self, state: GameState) -> tuple[Move, ...]:
        """Return ordinary legal moves for the current player."""
        occupied_coordinates = {
            piece.coordinate
            for piece in state.pieces
        }
        moves: list[Move] = []

        for placed_piece in state.pieces:
            if placed_piece.owner != state.current_player:
                continue

            piece_definition = self._piece_definition(
                placed_piece.piece_name
            )

            if (
                piece_definition is None
                or piece_definition.movement is None
            ):
                continue

            movement = piece_definition.movement

            if (
                movement.destination_condition
                is not DestinationCondition.EMPTY
            ):
                continue

            for row_step in self._row_steps(
                movement,
                placed_piece.owner,
            ):
                for column_step in (
                    -movement.distance,
                    movement.distance,
                ):
                    row = (
                        placed_piece.coordinate.row
                        + row_step
                    )
                    column = (
                        placed_piece.coordinate.column
                        + column_step
                    )

                    if not self._is_inside_board(
                        state,
                        row,
                        column,
                    ):
                        continue

                    destination = Coordinate(
                        row=row,
                        column=column,
                    )

                    if destination in occupied_coordinates:
                        continue

                    if not self._is_playable(destination):
                        continue

                    moves.append(
                        Move(
                            player=placed_piece.owner,
                            piece_name=placed_piece.piece_name,
                            source=placed_piece.coordinate,
                            coordinate=destination,
                        )
                    )

            moves.extend(
                self._capture_moves(
                    state,
                    placed_piece,
                    piece_definition,
                    occupied_coordinates,
                )
            )
        return tuple(moves)

    def _capture_moves(
        self,
        state: GameState,
        placed_piece: PlacedPiece,
        piece_definition: PieceDefinition,
        occupied_coordinates: set[Coordinate],
    ) -> tuple[Move, ...]:
        capture = piece_definition.capture
    
        if (
            capture is None
            or capture.condition is not CaptureCondition.ENEMY
        ):
            return ()
    
        moves: list[Move] = []
    
        for row_step in self._row_steps(
            capture,
            placed_piece.owner,
        ):
            for column_step in (
                -capture.distance,
                capture.distance,
            ):
                row = placed_piece.coordinate.row + row_step
                column = (
                    placed_piece.coordinate.column
                    + column_step
                )
    
                if not self._is_inside_board(
                    state,
                    row,
                    column,
                ):
                    continue
                
                destination = Coordinate(
                    row=row,
                    column=column,
                )
    
                if destination in occupied_coordinates:
                    continue
                
                if not self._is_playable(destination):
                    continue
                
                captured_coordinate = Coordinate(
                    row=(
                        placed_piece.coordinate.row
                        + destination.row
                    ) // 2,
                    column=(
                        placed_piece.coordinate.column
                        + destination.column
                    ) // 2,
                )
    
                captured_piece = next(
                    (
                        piece
                        for piece in state.pieces
                        if piece.coordinate
                        == captured_coordinate
                    ),
                    None,
                )
    
                if (
                    captured_piece is None
                    or captured_piece.owner
                    == placed_piece.owner
                ):
                    continue
                
                moves.append(
                    Move(
                        player=placed_piece.owner,
                        piece_name=placed_piece.piece_name,
                        source=placed_piece.coordinate,
                        coordinate=destination,
                    )
                )
    
        return tuple(moves)

    def _piece_definition(
        self,
        piece_name: str,
    ) -> PieceDefinition | None:
        return next(
            (
                piece
                for piece in self._game.pieces
                if piece.name == piece_name
            ),
            None,
        )

    def _row_steps(
        self,
        movement: MovementRule,
        owner: str,
    ) -> tuple[int, ...]:
        if (
            movement.direction
            is MovementDirection.DIAGONAL_ANY
        ):
            return (
                -movement.distance,
                movement.distance,
            )

        player = next(
            (
                player
                for player in self._game.players
                if player.name == owner
            ),
            None,
        )

        if player is None or player.forward is None:
            return ()

        if player.forward is ForwardDirection.UP:
            return (-movement.distance,)

        return (movement.distance,)

    @staticmethod
    def _is_inside_board(
        state: GameState,
        row: int,
        column: int,
    ) -> bool:
        return (
            0 <= row < state.rows
            and 0 <= column < state.columns
        )

    def _is_playable(
        self,
        coordinate: Coordinate,
    ) -> bool:
        playable_cells = self._game.board.playable_cells

        if playable_cells is PlayableCells.ALL:
            return True

        is_dark_cell = (
            coordinate.row + coordinate.column
        ) % 2 == 1

        if playable_cells is PlayableCells.DARK:
            return is_dark_cell

        return not is_dark_cell