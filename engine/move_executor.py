from parser.ast_nodes import GameDefinition, PlayableCells

from engine.errors import InvalidMoveError
from engine.game_state import GameState, GameStatus, PlacedPiece
from engine.move import Move
from engine.condition_evaluator import ConditionEvaluator


class MoveExecutor:
    """Applies valid placement moves to immutable game states."""

    def __init__(self, game: GameDefinition) -> None:
        self._game = game

    def apply(self, state: GameState, move: Move) -> GameState:
        """Apply a placement move and return the resulting state."""
        self._validate_game_is_ongoing(state)
        self._validate_player_turn(state, move)
        self._validate_coordinate(state, move)
        self._validate_playable_cell(move)
        self._validate_piece(move)
        self._validate_cell_is_empty(state, move)

        placed_piece = PlacedPiece(
            piece_name=move.piece_name,
            owner=move.player,
            coordinate=move.coordinate,
        )

        updated_state = GameState(
            rows=state.rows,
            columns=state.columns,
            pieces=(*state.pieces, placed_piece),
            current_player=self._next_player(move.player),
            turn_number=state.turn_number + 1,
        )

        return ConditionEvaluator(self._game).evaluate(
            updated_state,
            move,
        )

    def _validate_game_is_ongoing(self, state: GameState) -> None:
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
        move: Move,
    ) -> None:
        coordinate = move.coordinate

        if (
            coordinate.row >= state.rows
            or coordinate.column >= state.columns
        ):
            raise InvalidMoveError(
                f"Coordinate {coordinate} is outside the "
                f"{state.rows}x{state.columns} board."
            )

    def _validate_playable_cell(self, move: Move) -> None:
        playable_cells = self._game.board.playable_cells

        if playable_cells is PlayableCells.ALL:
            return

        coordinate_sum = (
            move.coordinate.row + move.coordinate.column
        )
        is_dark_cell = coordinate_sum % 2 == 1

        if playable_cells is PlayableCells.DARK and not is_dark_cell:
            raise InvalidMoveError(
                f"Coordinate {move.coordinate} is not a playable dark cell."
            )

        if playable_cells is PlayableCells.LIGHT and is_dark_cell:
            raise InvalidMoveError(
                f"Coordinate {move.coordinate} is not a playable light cell."
            )

    def _validate_piece(self, move: Move) -> None:
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

    def _validate_cell_is_empty(
        self,
        state: GameState,
        move: Move,
    ) -> None:
        if any(
            piece.coordinate == move.coordinate
            for piece in state.pieces
        ):
            raise InvalidMoveError(
                f"Coordinate {move.coordinate} is already occupied."
            )

    def _next_player(self, current_player: str) -> str:
        current_index = self._game.turn_order.index(current_player)
        next_index = (current_index + 1) % len(self._game.turn_order)

        return self._game.turn_order[next_index]