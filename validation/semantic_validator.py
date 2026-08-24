from collections import Counter
from collections.abc import Iterable

from parser.ast_nodes import (
    AlignCondition,
    AlignmentDirection,
    GameDefinition,
    MovementDirection,
    PieceDefinition,
    PlayerDefinition,
    PromotionCondition,
    NoMovesLeftCondition,
    NoPiecesLeftCondition,
    PlayerTarget,
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
        self._validate_setup(game, issues)
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

        players_by_name = {
            player.name: player
            for player in game.players
        }

        pieces_by_name = {
            piece.name: piece
            for piece in game.pieces
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
                if owner not in players_by_name:
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

            self._validate_piece_action(
                piece,
                issues,
            )
            self._validate_movement_rule(
                piece,
                players_by_name,
                issues,
            )
            self._validate_capture_rule(
                piece,
                players_by_name,
                issues,
            )
            self._validate_promotion_rule(
                piece,
                players_by_name,
                pieces_by_name,
                issues,
            )

    def _validate_piece_action(
        self,
        piece: PieceDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        has_placement = piece.placement is not None
        has_movement = piece.movement is not None
        path = f"pieces.{piece.name}.action"

        if not has_placement and not has_movement:
            issues.append(
                ValidationIssue(
                    code="missing_piece_action",
                    path=path,
                    message=(
                        f"Piece '{piece.name}' must declare "
                        "either placement or movement."
                    ),
                )
            )
            return

        if has_placement and has_movement:
            issues.append(
                ValidationIssue(
                    code="conflicting_piece_actions",
                    path=path,
                    message=(
                        f"Piece '{piece.name}' cannot declare "
                        "both placement and movement."
                    ),
                )
            )

    def _validate_movement_rule(
        self,
        piece: PieceDefinition,
        players_by_name: dict[str, PlayerDefinition],
        issues: list[ValidationIssue],
    ) -> None:
        movement = piece.movement

        if movement is None:
            return

        if movement.distance <= 0:
            issues.append(
                ValidationIssue(
                    code="invalid_movement_distance",
                    path=(
                        f"pieces.{piece.name}."
                        "movement.distance"
                    ),
                    message=(
                        f"Movement distance for piece "
                        f"'{piece.name}' must be greater than zero."
                    ),
                )
            )

        if movement.direction is not MovementDirection.DIAGONAL_FORWARD:
            return

        for owner in piece.owners:
            player = players_by_name.get(owner)

            if player is None or player.forward is not None:
                continue

            issues.append(
                ValidationIssue(
                    code="missing_forward_direction",
                    path=f"players.{owner}.forward",
                    message=(
                        f"Player '{owner}' must declare a forward "
                        f"direction to own piece '{piece.name}' "
                        "with a diagonal-forward movement rule."
                    ),
                )
            )

    def _validate_capture_rule(
        self,
        piece: PieceDefinition,
        players_by_name: dict[str, PlayerDefinition],
        issues: list[ValidationIssue],
    ) -> None:
        capture = piece.capture

        if capture is None:
            return

        if piece.movement is None:
            issues.append(
                ValidationIssue(
                    code="capture_requires_movement",
                    path=f"pieces.{piece.name}.capture",
                    message=(
                        f"Piece '{piece.name}' cannot declare "
                        "a capture rule without a movement rule."
                    ),
                )
            )

        if capture.distance <= 0:
            issues.append(
                ValidationIssue(
                    code="invalid_capture_distance",
                    path=(
                        f"pieces.{piece.name}."
                        "capture.distance"
                    ),
                    message=(
                        f"Capture distance for piece "
                        f"'{piece.name}' must be greater than zero."
                    ),
                )
            )

        movement_already_requires_forward = (
            piece.movement is not None
            and piece.movement.direction
            is MovementDirection.DIAGONAL_FORWARD
        )

        if (
            capture.direction is not MovementDirection.DIAGONAL_FORWARD
            or movement_already_requires_forward
        ):
            return

        for owner in piece.owners:
            player = players_by_name.get(owner)

            if player is None or player.forward is not None:
                continue

            issues.append(
                ValidationIssue(
                    code="missing_forward_direction",
                    path=f"players.{owner}.forward",
                    message=(
                        f"Player '{owner}' must declare a forward "
                        f"direction to own piece '{piece.name}' "
                        "with a diagonal-forward capture rule."
                    ),
                )
            )

    def _validate_promotion_rule(
        self,
        piece: PieceDefinition,
        players_by_name: dict[str, PlayerDefinition],
        pieces_by_name: dict[str, PieceDefinition],
        issues: list[ValidationIssue],
    ) -> None:
        promotion = piece.promotion

        if promotion is None:
            return

        if piece.movement is None:
            issues.append(
                ValidationIssue(
                    code="promotion_requires_movement",
                    path=f"pieces.{piece.name}.promotion",
                    message=(
                        f"Piece '{piece.name}' cannot declare "
                        "a promotion rule without a movement rule."
                    ),
                )
            )

        if promotion.condition is PromotionCondition.BACK_RANK:
            for owner in piece.owners:
                player = players_by_name.get(owner)

                if player is None or player.forward is not None:
                    continue

                path = f"players.{owner}.forward"

                issue_already_reported = any(
                    issue.code == "missing_forward_direction"
                    and issue.path == path
                    for issue in issues
                )

                if issue_already_reported:
                    continue

                issues.append(
                    ValidationIssue(
                        code="missing_forward_direction",
                        path=path,
                        message=(
                            f"Player '{owner}' must declare a forward "
                            f"direction to own piece '{piece.name}' "
                            "with a back-rank promotion rule."
                        ),
                    )
                )

        if promotion.target_piece_name not in pieces_by_name:
            issues.append(
                ValidationIssue(
                    code="unknown_promotion_target",
                    path=(
                        f"pieces.{piece.name}."
                        "promotion.target_piece_name"
                    ),
                    message=(
                        f"Promotion target "
                        f"'{promotion.target_piece_name}' for piece "
                        f"'{piece.name}' is not declared."
                    ),
                )
            )
            return

        if promotion.target_piece_name == piece.name:
            issues.append(
                ValidationIssue(
                    code="self_promotion_target",
                    path=(
                        f"pieces.{piece.name}."
                        "promotion.target_piece_name"
                    ),
                    message=(
                        f"Piece '{piece.name}' cannot promote "
                        "to itself."
                    ),
                )
            )
            return

        target_piece = pieces_by_name[promotion.target_piece_name]

        unsupported_owners = tuple(
            owner
            for owner in piece.owners
            if owner not in target_piece.owners
        )

        if unsupported_owners:
            owners = ", ".join(unsupported_owners)

            issues.append(
                ValidationIssue(
                    code="incompatible_promotion_owners",
                    path=(
                        f"pieces.{piece.name}."
                        "promotion.target_piece_name"
                    ),
                    message=(
                        f"Promotion target '{target_piece.name}' "
                        f"does not support owner(s): {owners}."
                    ),
                )
            )

    def _validate_setup(
        self,
        game: GameDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        pieces_by_name = {
            piece.name: piece
            for piece in game.pieces
        }

        declared_players = {
            player.name
            for player in game.players
        }

        for index, rule in enumerate(game.setup):
            piece = pieces_by_name.get(rule.piece_name)

            if piece is None:
                issues.append(
                    ValidationIssue(
                        code="unknown_setup_piece",
                        path=f"setup[{index}].piece_name",
                        message=(
                            f"Piece '{rule.piece_name}' used in setup "
                            "is not declared."
                        ),
                    )
                )

            if rule.owner not in declared_players:
                issues.append(
                    ValidationIssue(
                        code="unknown_setup_owner",
                        path=f"setup[{index}].owner",
                        message=(
                            f"Player '{rule.owner}' used in setup "
                            "is not declared."
                        ),
                    )
                )

            if (
                piece is not None
                and rule.owner in declared_players
                and rule.owner not in piece.owners
            ):
                issues.append(
                    ValidationIssue(
                        code="setup_owner_not_allowed",
                        path=f"setup[{index}].owner",
                        message=(
                            f"Player '{rule.owner}' cannot own piece "
                            f"'{rule.piece_name}' used in setup."
                        ),
                    )
                )

            has_valid_row_range = (
                    rule.first_row >= 1
                    and rule.first_row <= rule.last_row
                )

            if not has_valid_row_range:
                issues.append(
                    ValidationIssue(
                        code="invalid_setup_row_range",
                        path=f"setup[{index}].rows",
                        message=(
                            f"Setup rows {rule.first_row}..{rule.last_row} "
                            "must form an ordered one-based range."
                        ),
                    )
                )

            if (
                has_valid_row_range
                and rule.last_row > game.board.rows
            ):
                issues.append(
                    ValidationIssue(
                        code="setup_rows_out_of_bounds",
                        path=f"setup[{index}].rows",
                        message=(
                            f"Setup rows {rule.first_row}..{rule.last_row} "
                            f"do not fit a board with {game.board.rows} rows."
                        ),
                    )
                )

        valid_setup_rules = tuple(
            (index, rule)
            for index, rule in enumerate(game.setup)
            if (
                1
                <= rule.first_row
                <= rule.last_row
                <= game.board.rows
            )
        )

        for position, (index, rule) in enumerate(valid_setup_rules):
            previous_rules = valid_setup_rules[:position]

            for previous_index, previous_rule in previous_rules:
                ranges_overlap = (
                    rule.first_row <= previous_rule.last_row
                    and previous_rule.first_row <= rule.last_row
                )

                if not ranges_overlap:
                    continue

                issues.append(
                    ValidationIssue(
                        code="overlapping_setup_rules",
                        path=f"setup[{index}].rows",
                        message=(
                            f"Setup rows {rule.first_row}..{rule.last_row} "
                            f"overlap rows {previous_rule.first_row}.."
                            f"{previous_rule.last_row} from setup rule "
                            f"{previous_index}."
                        ),
                    )
                )
                break


    def _validate_win_conditions(
        self,
        game: GameDefinition,
        issues: list[ValidationIssue],
    ) -> None:
        
        for index, condition in enumerate(game.win_conditions):
            path = f"win_conditions[{index}]"

            if isinstance(
                condition,
                (
                    NoPiecesLeftCondition,
                    NoMovesLeftCondition,
                ),
            ):
                if condition.target is not PlayerTarget.OPPONENT:
                    issues.append(
                        ValidationIssue(
                            code="unsupported_player_target",
                            path=f"{path}.target",
                            message=(
                                f"Player target '{condition.target}' "
                                "is not supported."
                            ),
                        )
                    )
                    continue
                
                if len(game.players) != 2:
                    issues.append(
                        ValidationIssue(
                            code="ambiguous_opponent_target",
                            path=f"{path}.target",
                            message=(
                                "The opponent target requires exactly "
                                f"two players, but {len(game.players)} "
                                "are declared."
                            ),
                        )
                    )
            
                continue
            if not isinstance(condition, AlignCondition):
                continue

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