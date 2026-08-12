from collections.abc import Callable

from engine.board_renderer import BoardRenderer
from engine.errors import InvalidMoveError
from engine.game_session import GameSession
from engine.game_state import Coordinate, GameState, GameStatus
from engine.move import Move
from parser.ast_nodes import GameDefinition


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
    ) -> None:
        self._game = game
        self._session = GameSession(game)
        self._renderer = BoardRenderer(game)
        self._input = input_function
        self._output = output_function

    @property
    def state(self) -> GameState:
        """Return the current immutable game-state snapshot."""
        return self._session.state

    def run(self) -> GameState:
        """Run the interactive game loop and return its final state."""
        self._output(f"Piecewise — {self._game.name}")

        while self.state.status is GameStatus.ONGOING:
            self._output("")
            self._output(self._renderer.render(self.state))

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
                self._output(f"Invalid move: {error}")

        self._output("")
        self._output(self._renderer.render(self.state))
        self._output_result()

        return self.state

    def _parse_move(self, raw_input: str) -> Move:
        parts = raw_input.split()

        if len(parts) != 2:
            raise ValueError(
                "Enter a move using the format: row column."
            )

        try:
            row, column = (
                int(value)
                for value in parts
            )
        except ValueError as error:
            raise ValueError(
                "Row and column must be integers."
            ) from error

        return Move(
            player=self.state.current_player,
            piece_name=self._piece_name_for_current_player(),
            coordinate=Coordinate(
                row=row,
                column=column,
            ),
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
            self._output(f"Player {self.state.winner} wins!")
            return

        self._output("The game ended in a draw.")