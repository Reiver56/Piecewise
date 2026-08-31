from collections.abc import Callable

from cli.terminal_renderer import TerminalRenderer
from engine.errors import InvalidMoveError
from engine.game_session import GameSession
from engine.game_state import Coordinate, GameState, GameStatus
from engine.move import Move
from parser.ast_nodes import (
    GameDefinition,
    PlacementType,
)


InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


class GameCLI:
    """Runs an interactive game session in a terminal-like environment."""

    def __init__(
        self,
        game: GameDefinition,
        *,
        input_function: InputFunction = input,
        output_function: OutputFunction = print,
        use_color: bool = False,
    ) -> None:
        self._game = game
        self._session = GameSession(game)
        self._renderer = TerminalRenderer(
            game,
            use_color=use_color,
        )
        self._input = input_function
        self._output = output_function

    @property
    def state(self) -> GameState:
        """Return the current immutable game-state snapshot."""
        return self._session.state

    def run(self) -> GameState:
        """Run the interactive game loop and return its final state."""
        self._output(
            self._renderer.render_title(self._game.name)
        )

        while self.state.status is GameStatus.ONGOING:
            self._output("")
            self._output(
                f"Turn {self.state.turn_number} | "
                f"Player {self.state.current_player}"
            )
            self._output(self._renderer.render(self.state))
            self._output(self._input_help_text())

            raw_input = self._input(
                f"Player {self.state.current_player} > "
            )

            if raw_input.strip().lower() == "quit":
                self._output("Game abandoned.")
                return self.state

            try:
                move = self._parse_move(raw_input)
                self._session.play(move)
            except (ValueError, InvalidMoveError) as error:
                self._output(
                    self._renderer.render_error(str(error))
                )

        self._output("")
        self._output(self._renderer.render(self.state))
        self._output_result()

        return self.state

    def _input_help_text(self) -> str:
        """Return input instructions for the current player's actions."""
        if self._uses_relocation_format():
            return (
                "Move: from_row from_col to_row to_col "
                "| quit: exit"
            )

        if self._uses_column_placement_format():
            return "Move: column | quit: exit"

        return "Move: row column | quit: exit"
    
    def _parse_move(self, raw_input: str) -> Move:
        parts = raw_input.split()

        uses_relocation_format = (
            self._uses_relocation_format()
        )
        uses_column_format = (
            self._uses_column_placement_format()
        )

        if uses_relocation_format:
            expected_values = 4
        elif uses_column_format:
            expected_values = 1
        else:
            expected_values = 2

        if len(parts) != expected_values:
            if uses_relocation_format:
                raise ValueError(
                    "Enter a relocation using the format: "
                    "source_row source_column "
                    "destination_row destination_column."
                )

            if uses_column_format:
                raise ValueError(
                    "Enter a placement using the format: column."
                )

            raise ValueError(
                "Enter a move using the format: row column."
            )

        try:
            coordinates = tuple(
                int(value)
                for value in parts
            )
        except ValueError as error:
            if uses_relocation_format:
                raise ValueError(
                    "Source and destination coordinates "
                    "must be integers."
                ) from error

            if uses_column_format:
                raise ValueError(
                    "Column must be an integer."
                ) from error

            raise ValueError(
                "Row and column must be integers."
            ) from error

        if not uses_relocation_format:
            if uses_column_format:
                column, = coordinates
                row = 0
            else:
                row, column = coordinates

            return Move(
                player=self.state.current_player,
                piece_name=self._piece_name_for_current_player(),
                coordinate=Coordinate(
                    row=row,
                    column=column,
                ),
            )

        (
            source_row,
            source_column,
            destination_row,
            destination_column,
        ) = coordinates

        source = Coordinate(
            row=source_row,
            column=source_column,
        )

        source_piece = next(
            (
                piece
                for piece in self.state.pieces
                if piece.coordinate == source
            ),
            None,
        )

        if source_piece is None:
            raise ValueError(
                f"Source coordinate {source} "
                "does not contain a piece."
            )

        return Move(
            player=self.state.current_player,
            piece_name=source_piece.piece_name,
            source=source,
            coordinate=Coordinate(
                row=destination_row,
                column=destination_column,
            ),
        )

    def _uses_relocation_format(self) -> bool:
        return any(
            piece.movement is not None
            and self.state.current_player in piece.owners
            for piece in self._game.pieces
        )

    def _uses_column_placement_format(self) -> bool:
        return any(
            piece.placement
            is PlacementType.ANY_NON_FULL_COLUMN
            and self.state.current_player in piece.owners
            for piece in self._game.pieces
        )

    def _piece_name_for_current_player(self) -> str:
        piece = next(
            (
                piece
                for piece in self._game.pieces
                if self.state.current_player in piece.owners
            ),
            None,
        )

        if piece is None:
            raise ValueError(
                f"Player '{self.state.current_player}' "
                "has no available piece."
            )

        return piece.name

    def _output_result(self) -> None:
        if self.state.status is GameStatus.WON:
            message = f"Player {self.state.winner} wins!"
        else:
            message = "The game ended in a draw."

        self._output(
            self._renderer.render_result(message)
        )