from collections import Counter
from collections.abc import Iterable

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    GameDefinition,
)
from validation.errors import (
    SemanticValidationError,
    ValidationIssue,
)


class SemanticValidator:
    """Validate the semantic consistency of a Piecewise game definition."""

    def validate(
        self,
        game: GameDefinition,
    ) -> tuple[ValidationIssue, ...]:
        """Return every semantic issue found in the game definition."""
        issues: list[ValidationIssue] = []

        self._validate_board(game, issues)
        self._validate_players(game, issues)
        self._validate_pieces(game, issues)
        self._validate_win_conditions(game, issues)

        return tuple(issues)

    def validate_or_raise(self, game: GameDefinition) -> None:
        """Raise SemanticValidationError if the game is invalid."""
        issues = self.validate(game)

        if issues:
            raise SemanticValidationError(issues)

    def _validate_board(
        self,
        game: GameDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        if game.board.rows <= 0:
            issues.append(
                ValidationIssue(
                    code="invalid_board_rows",
                    path="board.rows",
                    message="Board rows must be greater than zero.",
                )
            )

        if game.board.columns <= 0:
            issues.append(
                ValidationIssue(
                    code="invalid_board_columns",
                    path="board.columns",
                    message="Board columns must be greater than zero.",
                )
            )

    def _validate_players(
        self,
        game: GameDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        player_names = tuple(player.name for player in game.players)
        declared_players = set(player_names)

        for name in self._duplicates(player_names):
            issues.append(
                ValidationIssue(
                    code="duplicate_player",
                    path="players",
                    message=f"Player '{name}' is declared more than once.",
                )
            )

        for name in self._duplicates(game.turn_order):
            issues.append(
                ValidationIssue(
                    code="duplicate_turn_player",
                    path="turn_order",
                    message=(
                        f"Player '{name}' appears more than once "
                        "in the turn order."
                    ),
                )
            )

        for name in game.turn_order:
            if name not in declared_players:
                issues.append(
                    ValidationIssue(
                        code="unknown_turn_player",
                        path="turn_order",
                        message=(
                            f"Player '{name}' in the turn order "
                            "is not declared."
                        ),
                    )
                )

        turn_players = set(game.turn_order)

        for name in dict.fromkeys(player_names):
            if name not in turn_players:
                issues.append(
                    ValidationIssue(
                        code="missing_turn_player",
                        path="turn_order",
                        message=(
                            f"Declared player '{name}' is missing "
                            "from the turn order."
                        ),
                    )
                )

    def _validate_pieces(
        self,
        game: GameDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        piece_names = tuple(piece.name for piece in game.pieces)
        declared_players = {
            player.name for player in game.players
        }

        for name in self._duplicates(piece_names):
            issues.append(
                ValidationIssue(
                    code="duplicate_piece",
                    path="pieces",
                    message=f"Piece '{name}' is declared more than once.",
                )
            )

        for piece in game.pieces:
            for owner in piece.owners:
                if owner not in declared_players:
                    issues.append(
                        ValidationIssue(
                            code="unknown_piece_owner",
                            path=f"pieces.{piece.name}.owners",
                            message=(
                                f"Player '{owner}' owning piece "
                                f"'{piece.name}' is not declared."
                            ),
                        )
                    )

    def _validate_win_conditions(
        self,
        game: GameDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        for index, condition in enumerate(game.win_conditions):
            if not isinstance(condition, AlignCondition):
                continue

            path = f"win_conditions[{index}]"

            if condition.length <= 0:
                issues.append(
                    ValidationIssue(
                        code="invalid_alignment_length",
                        path=f"{path}.length",
                        message=(
                            "Alignment length must be greater than zero."
                        ),
                    )
                )
                continue

            maximum = self._maximum_alignment_length(
                game,
                condition.direction,
            )

            if condition.length > maximum:
                issues.append(
                    ValidationIssue(
                        code="alignment_does_not_fit",
                        path=f"{path}.length",
                        message=(
                            f"Alignment length {condition.length} does not "
                            f"fit the {game.board.rows}x"
                            f"{game.board.columns} board for direction "
                            f"'{condition.direction.value}'."
                        ),
                    )
                )

    @staticmethod
    def _maximum_alignment_length(
        game: GameDefinition,
        direction: AlignmentDirection,
    ) -> int:
        if direction is AlignmentDirection.SAME_ROW:
            return game.board.columns

        if direction is AlignmentDirection.SAME_COL:
            return game.board.rows

        return min(game.board.rows, game.board.columns)

    @staticmethod
    def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
        counts = Counter(values)
        return tuple(
            value
            for value, count in counts.items()
            if count > 1
        )