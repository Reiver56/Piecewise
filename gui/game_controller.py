from engine.game_session import GameSession
from engine.game_state import (
    Coordinate,
    GameState,
    PlacedPiece,
)
from parser.ast_nodes import (
    GameDefinition,
    PieceDefinition,
    PlacementType,
)
from engine.legal_move_generator import LegalMoveGenerator
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

    @property
    def legal_destinations(self) -> tuple[Coordinate, ...]:
        """Return legal destinations for the selected piece."""
        selected_source = self._selected_source

        if selected_source is None:
            return ()

        moves = LegalMoveGenerator(
            self._game
        ).generate(self.state)

        return tuple(
            move.destination
            for move in moves
            if move.source == selected_source
        )
    
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
        coordinate = Coordinate(
            row=row,
            column=column,
        )

        placement_piece = (
            self._placement_piece_for_current_player()
        )

        if placement_piece is not None:
            return self._handle_placement(
                coordinate,
                placement_piece,
            )

        return self._handle_relocation(coordinate)

    def _handle_placement(
        self,
        coordinate: Coordinate,
        piece_definition: PieceDefinition,
    ) -> GameState:
        destination = coordinate

        if (
            piece_definition.placement
            is PlacementType.ANY_NON_FULL_COLUMN
        ):
            destination = Coordinate(
                row=0,
                column=coordinate.column,
            )

        move = Move(
            player=self.state.current_player,
            piece_name=piece_definition.name,
            coordinate=destination,
        )

        return self._session.play(move)

    def _handle_relocation(
        self,
        coordinate: Coordinate,
    ) -> GameState:
        if self._selected_source is None:
            return self._select_source(coordinate)

        if coordinate == self._selected_source:
            self._selected_source = None
            return self.state

        selected_piece = self._piece_at(coordinate)

        if (
            selected_piece is not None
            and selected_piece.owner
            == self.state.current_player
        ):
            self._selected_source = coordinate
            return self.state

        source_piece = self._piece_at(
            self._selected_source
        )

        if source_piece is None:
            self._selected_source = None
            raise ValueError(
                "The selected source no longer "
                "contains a piece."
            )

        move = Move(
            player=self.state.current_player,
            piece_name=source_piece.piece_name,
            source=self._selected_source,
            coordinate=coordinate,
        )

        result = self._session.play(move)

        self._selected_source = (
            result.forced_capture_source
        )

        return result

    def _select_source(
        self,
        coordinate: Coordinate,
    ) -> GameState:
        piece = self._piece_at(coordinate)

        if piece is None:
            raise ValueError(
                f"Coordinate {coordinate} "
                "does not contain a piece."
            )

        if piece.owner != self.state.current_player:
            raise ValueError(
                f"Player '{self.state.current_player}' "
                f"cannot select a piece owned by "
                f"'{piece.owner}'."
            )

        self._selected_source = coordinate

        return self.state

    def _piece_at(
        self,
        coordinate: Coordinate,
    ) -> PlacedPiece | None:
        return next(
            (
                piece
                for piece in self.state.pieces
                if piece.coordinate == coordinate
            ),
            None,
        )