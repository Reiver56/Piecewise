from engine.game_session import GameSession
from engine.game_state import Coordinate, GameState
from parser.ast_nodes import (
    GameDefinition,
    PieceDefinition,
    PlacementType,
)
from engine.move import Move



class GameController:
    """Coordinates a game session for a graphical interface."""

    def __init__(self, game: GameDefinition) -> None:
        self._game = game
        self._session = GameSession(game)
        self._selected_source: Coordinate | None = None

    @property
    def game(self) -> GameDefinition:
        """Return the game definition managed by the controller."""
        return self._game

    @property
    def state(self) -> GameState:
        """Return the current immutable game-state snapshot."""
        return self._session.state

    @property
    def selected_source(self) -> Coordinate | None:
        """Return the currently selected relocation source."""
        return self._selected_source

    def restart(self) -> GameState:
        """Start a fresh session for the current game."""
        self._session = GameSession(self._game)
        self._selected_source = None

        return self.state

    def _placement_piece_for_current_player(
        self,
    ) -> PieceDefinition | None:
        return next(
            (
                piece
                for piece in self._game.pieces
                if (
                    self.state.current_player in piece.owners
                    and piece.placement is not None
                )
            ),
            None,
        )

    def handle_cell(
        self,
        row: int,
        column: int,
    ) -> GameState:
        """Handle a board-cell interaction."""
        piece_definition = (
            self._placement_piece_for_current_player()
        )

        if piece_definition is None:
            raise ValueError(
                f"Player '{self.state.current_player}' "
                "has no placement piece."
            )

        destination_row = row

        if (
            piece_definition.placement
            is PlacementType.ANY_NON_FULL_COLUMN
        ):
            destination_row = 0

        move = Move(
            player=self.state.current_player,
            piece_name=piece_definition.name,
            coordinate=Coordinate(
                row=destination_row,
                column=column,
            ),
        )

        return self._session.play(move)