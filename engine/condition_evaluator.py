from dataclasses import replace

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    BoardFullCondition,
    GameDefinition,
    Outcome,
    PlayableCells,
    NoPiecesLeftCondition,
    PlayerTarget,
)

from engine.game_state import Coordinate, GameState, GameStatus
from engine.move import Move


_DIRECTION_STEPS = {
    AlignmentDirection.SAME_ROW: ((0, 1),),
    AlignmentDirection.SAME_COL: ((1, 0),),
    AlignmentDirection.DIAGONAL: ((1, 1), (1, -1)),
}


class ConditionEvaluator:
    """Evaluates win and draw conditions after a placement move."""

    def __init__(self, game: GameDefinition) -> None:
        self._game = game

    def evaluate(
        self,
        state: GameState,
        last_move: Move,
    ) -> GameState:
        """Return the state resulting from condition evaluation."""
        if self._has_winning_alignment(state, last_move):
            return replace(
                state,
                status=GameStatus.WON,
                winner=last_move.player,
            )

        if self._has_no_pieces_left_win(state, last_move):
            return replace(
                state,
                status=GameStatus.WON,
                winner=last_move.player,
            )

        if self._has_board_full_draw(state):
            return replace(
                state,
                status=GameStatus.DRAWN,
            )

        return state

    def _has_winning_alignment(
        self,
        state: GameState,
        last_move: Move,
    ) -> bool:
        for condition in self._game.win_conditions:
            if not isinstance(condition, AlignCondition):
                continue

            if condition.outcome is not Outcome.WIN:
                continue

            if self._matches_alignment(
                state,
                last_move,
                condition,
            ):
                return True

        return False
    

    def _matches_alignment(
        self,
        state: GameState,
        last_move: Move,
        condition: AlignCondition,
    ) -> bool:
        owner_by_coordinate = {
            piece.coordinate: piece.owner
            for piece in state.pieces
        }

        for row_step, column_step in _DIRECTION_STEPS[
            condition.direction
        ]:
            aligned_count = 1

            aligned_count += self._count_direction(
                owner_by_coordinate,
                last_move.coordinate,
                last_move.player,
                row_step,
                column_step,
            )
            aligned_count += self._count_direction(
                owner_by_coordinate,
                last_move.coordinate,
                last_move.player,
                -row_step,
                -column_step,
            )

            if aligned_count >= condition.length:
                return True

        return False

    def _count_direction(
        self,
        owner_by_coordinate: dict[Coordinate, str],
        origin: Coordinate,
        player: str,
        row_step: int,
        column_step: int,
    ) -> int:
        count = 0
        row = origin.row + row_step
        column = origin.column + column_step

        while row >= 0 and column >= 0:
            coordinate = Coordinate(row=row, column=column)

            if owner_by_coordinate.get(coordinate) != player:
                break

            count += 1
            row += row_step
            column += column_step

        return count

    def _has_no_pieces_left_win(
        self,
        state: GameState,
        last_move: Move,
    ) -> bool:
        has_condition = any(
            isinstance(condition, NoPiecesLeftCondition)
            and condition.target is PlayerTarget.OPPONENT
            and condition.outcome is Outcome.WIN
            for condition in self._game.win_conditions
        )
    
        if not has_condition:
            return False
    
        opponents = tuple(
            player.name
            for player in self._game.players
            if player.name != last_move.player
        )
    
        if len(opponents) != 1:
            return False
    
        opponent = opponents[0]
    
        return not any(
            piece.owner == opponent
            for piece in state.pieces
        )

    def _has_board_full_draw(self, state: GameState) -> bool:
        has_draw_condition = any(
            isinstance(condition, BoardFullCondition)
            and condition.outcome is Outcome.DRAW
            for condition in self._game.win_conditions
        )

        if not has_draw_condition:
            return False

        occupied_coordinates = {
            piece.coordinate
            for piece in state.pieces
        }

        return all(
            Coordinate(row=row, column=column)
            in occupied_coordinates
            for row in range(state.rows)
            for column in range(state.columns)
            if self._is_playable_cell(row, column)
        )

    def _is_playable_cell(
        self,
        row: int,
        column: int,
    ) -> bool:
        playable_cells = self._game.board.playable_cells

        if playable_cells is PlayableCells.ALL:
            return True

        is_dark_cell = (row + column) % 2 == 1

        if playable_cells is PlayableCells.DARK:
            return is_dark_cell

        return not is_dark_cell