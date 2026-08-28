from dataclasses import replace
from pathlib import Path

import pytest

from engine.errors import InvalidMoveError
from engine.game_initializer import GameInitializer
from engine.game_state import (
    Coordinate, 
    GameState, 
    GameStatus, 
    PlacedPiece,
)
from engine.move import Move
from engine.move_executor import MoveExecutor
from parser.ast_nodes import (
    DestinationCondition,
    ForwardDirection,
    MovementDirection,
    MovementRule,
    PieceDefinition,
    PlayableCells,
    PlayerDefinition,
    CaptureCondition,
    CaptureRule,
    PromotionCondition,
    PromotionRule,
)
from parser.game_parser import GameParser


GAMES_DIRECTORY = Path(__file__).parent.parent / "games"


def load_tictactoe():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "tictactoe.game"
    )

def load_checkers():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "checkers.game"
    )

def load_connectfour():
    return GameParser().parse_game_file(
        GAMES_DIRECTORY / "connectfour.game"
    )

def create_movement_game(
    direction: MovementDirection = (
        MovementDirection.DIAGONAL_FORWARD
    ),
):
    game = load_tictactoe()

    return replace(
        game,
        board=replace(
            game.board,
            rows=8,
            columns=8,
            playable_cells=PlayableCells.DARK,
        ),
        players=(
            PlayerDefinition(
                name="White",
                forward=ForwardDirection.UP,
            ),
            PlayerDefinition(
                name="Black",
                forward=ForwardDirection.DOWN,
            ),
        ),
        turn_order=("White", "Black"),
        pieces=(
            PieceDefinition(
                name="Man",
                owners=("White", "Black"),
                movement=MovementRule(
                    direction=direction,
                    distance=1,
                    destination_condition=DestinationCondition.EMPTY,
                ),
            ),
        ),
    )

def create_capture_game(
    direction: MovementDirection = (
        MovementDirection.DIAGONAL_FORWARD
    ),
):
    game = create_movement_game(direction)
    piece = game.pieces[0]

    return replace(
        game,
        pieces=(
            replace(
                piece,
                capture=CaptureRule(
                    direction=direction,
                    distance=2,
                    condition=CaptureCondition.ENEMY,
                ),
            ),
        ),
    )

def create_promotion_game():
    game = create_capture_game()
    man = game.pieces[0]

    king = PieceDefinition(
        name="King",
        owners=man.owners,
        movement=MovementRule(
            direction=MovementDirection.DIAGONAL_ANY,
            distance=1,
            destination_condition=DestinationCondition.EMPTY,
        ),
        capture=CaptureRule(
            direction=MovementDirection.DIAGONAL_ANY,
            distance=2,
            condition=CaptureCondition.ENEMY,
        ),
    )

    return replace(
        game,
        pieces=(
            replace(
                man,
                promotion=PromotionRule(
                    condition=PromotionCondition.BACK_RANK,
                    target_piece_name="King",
                ),
            ),
            king,
        ),
    )

def create_movement_state(
    *,
    owner: str,
    coordinate: Coordinate,
    current_player: str,
    turn_number: int = 1,
) -> GameState:
    return GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner=owner,
                coordinate=coordinate,
            ),
        ),
        current_player=current_player,
        turn_number=turn_number,
    )

def test_relocation_promotes_up_player_on_back_rank() -> None:
    game = create_promotion_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=1, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=1, column=0),
        coordinate=Coordinate(row=0, column=1),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="King",
            owner="White",
            coordinate=Coordinate(row=0, column=1),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_relocation_promotes_down_player_on_back_rank() -> None:
    game = create_promotion_game()
    state = create_movement_state(
        owner="Black",
        coordinate=Coordinate(row=6, column=1),
        current_player="Black",
        turn_number=2,
    )
    move = Move(
        player="Black",
        piece_name="Man",
        source=Coordinate(row=6, column=1),
        coordinate=Coordinate(row=7, column=0),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="King",
            owner="Black",
            coordinate=Coordinate(row=7, column=0),
        ),
    )
    assert result.current_player == "White"
    assert result.turn_number == 3

def test_relocation_does_not_promote_before_back_rank() -> None:
    game = create_promotion_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=2, column=1),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=2, column=1),
        coordinate=Coordinate(row=1, column=0),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=1, column=0),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_capture_promotes_piece_on_back_rank() -> None:
    game = create_promotion_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=2, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=1, column=2),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=2, column=1),
        coordinate=Coordinate(row=0, column=3),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="King",
            owner="White",
            coordinate=Coordinate(row=0, column=3),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_promotion_does_not_modify_previous_state() -> None:
    game = create_promotion_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=1, column=0),
        current_player="White",
    )
    original_piece = state.pieces[0]

    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=1, column=0),
        coordinate=Coordinate(row=0, column=1),
    )

    result = MoveExecutor(game).apply(state, move)

    assert state.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=1, column=0),
        ),
    )
    assert state.pieces[0] is original_piece

    assert result.pieces == (
        PlacedPiece(
            piece_name="King",
            owner="White",
            coordinate=Coordinate(row=0, column=1),
        ),
    )
    assert result.pieces is not state.pieces
    assert result.pieces[0] is not original_piece

def test_apply_captures_enemy_piece_forward() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=3, column=2),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.status is GameStatus.ONGOING 

def test_capture_keeps_turn_when_same_piece_can_capture_again() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=2, column=3),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    first_capture = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    result = MoveExecutor(game).apply(
        state,
        first_capture,
    )

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=3, column=2),
        ),
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=2, column=3),
        ),
    )
    assert result.current_player == "White"
    assert result.turn_number == 1
    assert result.forced_capture_source == Coordinate(
        row=3,
        column=2,
    )
    assert result.status is GameStatus.ONGOING

def test_capture_chain_rejects_different_source() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=6),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=2, column=3),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=5),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    first_capture = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    continuation_state = MoveExecutor(game).apply(
        state,
        first_capture,
    )

    other_piece_capture = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=6),
        coordinate=Coordinate(row=3, column=4),
    )

    with pytest.raises(
        InvalidMoveError,
        match="must continue with the same piece",
    ):
        MoveExecutor(game).apply(
            continuation_state,
            other_piece_capture,
        )

def test_capture_chain_passes_turn_after_final_capture() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=2, column=3),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=6, column=7),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    executor = MoveExecutor(game)

    continuation_state = executor.apply(
        state,
        Move(
            player="White",
            piece_name="Man",
            source=Coordinate(row=5, column=0),
            coordinate=Coordinate(row=3, column=2),
        ),
    )

    result = executor.apply(
        continuation_state,
        Move(
            player="White",
            piece_name="Man",
            source=Coordinate(row=3, column=2),
            coordinate=Coordinate(row=1, column=4),
        ),
    )

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=1, column=4),
        ),
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=6, column=7),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.forced_capture_source is None
    assert result.status is GameStatus.ONGOING

def test_capture_chain_evaluates_win_after_final_capture() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=2, column=3),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    executor = MoveExecutor(game)

    continuation_state = executor.apply(
        state,
        Move(
            player="White",
            piece_name="Man",
            source=Coordinate(row=5, column=0),
            coordinate=Coordinate(row=3, column=2),
        ),
    )

    result = executor.apply(
        continuation_state,
        Move(
            player="White",
            piece_name="Man",
            source=Coordinate(row=3, column=2),
            coordinate=Coordinate(row=1, column=4),
        ),
    )

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=1, column=4),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.forced_capture_source is None
    assert result.status is GameStatus.WON
    assert result.winner == "White"

def test_promoted_piece_continues_capture_chain_as_king() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=2, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=1, column=2),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=1, column=4),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=6, column=7),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    executor = MoveExecutor(game)

    continuation_state = executor.apply(
        state,
        Move(
            player="White",
            piece_name="Man",
            source=Coordinate(row=2, column=1),
            coordinate=Coordinate(row=0, column=3),
        ),
    )

    assert continuation_state.pieces[0] == PlacedPiece(
        piece_name="King",
        owner="White",
        coordinate=Coordinate(row=0, column=3),
    )
    assert continuation_state.current_player == "White"
    assert continuation_state.turn_number == 1
    assert continuation_state.forced_capture_source == Coordinate(
        row=0,
        column=3,
    )

    result = executor.apply(
        continuation_state,
        Move(
            player="White",
            piece_name="King",
            source=Coordinate(row=0, column=3),
            coordinate=Coordinate(row=2, column=5),
        ),
    )

    assert result.pieces == (
        PlacedPiece(
            piece_name="King",
            owner="White",
            coordinate=Coordinate(row=2, column=5),
        ),
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=6, column=7),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.forced_capture_source is None
    assert result.status is GameStatus.ONGOING

def test_capture_of_last_opponent_piece_ends_game() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=3, column=2),
        ),
    )
    assert result.status is GameStatus.WON
    assert result.winner == "White"
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_move_ends_game_when_opponent_has_no_legal_moves() -> None:
    game = load_checkers()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=3, column=2),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=7, column=0),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=3, column=2),
        coordinate=Coordinate(row=2, column=3),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=2, column=3),
        ),
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=7, column=0),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2
    assert result.status is GameStatus.WON
    assert result.winner == "White"

def test_capture_does_not_modify_previous_state() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    pieces_before_capture = state.pieces

    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert state.pieces is pieces_before_capture
    assert state.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=5, column=0),
        ),
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=4, column=1),
        ),
    )

    assert result is not state
    assert result.pieces is not pieces_before_capture
    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=3, column=2),
        ),
    )

def test_capture_rejects_empty_intermediate_cell() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    with pytest.raises(
        InvalidMoveError,
        match="does not contain a piece",
    ):
        MoveExecutor(game).apply(state, move)

def test_capture_rejects_own_piece() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    with pytest.raises(
        InvalidMoveError,
        match="cannot capture their own piece",
    ):
        MoveExecutor(game).apply(state, move)

def test_diagonal_any_allows_backward_capture() -> None:
    game = create_capture_game(
        MovementDirection.DIAGONAL_ANY,
    )
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=3, column=2),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=3),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=3, column=2),
        coordinate=Coordinate(row=5, column=4),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=5, column=4),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_forward_capture_rejects_backward_direction() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=3, column=2),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=3),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=3, column=2),
        coordinate=Coordinate(row=5, column=4),
    )

    with pytest.raises(
        InvalidMoveError,
        match="must capture piece 'Man' forward",
    ):
        MoveExecutor(game).apply(state, move)

def test_apply_captures_enemy_piece_forward_for_down_player() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=2, column=1),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=3, column=2),
            ),
        ),
        current_player="Black",
        turn_number=2,
    )
    move = Move(
        player="Black",
        piece_name="Man",
        source=Coordinate(row=2, column=1),
        coordinate=Coordinate(row=4, column=3),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=4, column=3),
        ),
    )
    assert result.current_player == "White"
    assert result.turn_number == 3

def test_forward_capture_requires_player_direction() -> None:
    game = create_capture_game()
    white, black = game.players
    piece = game.pieces[0]
    movement = piece.movement

    assert movement is not None

    invalid_game = replace(
        game,
        players=(
            replace(
                white,
                forward=None,
            ),
            black,
        ),
        pieces=(
            replace(
                piece,
                movement=replace(
                    movement,
                    direction=MovementDirection.DIAGONAL_ANY,
                ),
            ),
        ),
    )

    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    with pytest.raises(
        InvalidMoveError,
        match="has no forward direction",
    ):
        MoveExecutor(invalid_game).apply(state, move)

def test_apply_relocates_piece_forward_for_up_player() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=4, column=1),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=4, column=1),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_apply_relocates_piece_forward_for_down_player() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="Black",
        coordinate=Coordinate(row=2, column=1),
        current_player="Black",
        turn_number=2,
    )
    move = Move(
        player="Black",
        piece_name="Man",
        source=Coordinate(row=2, column=1),
        coordinate=Coordinate(row=3, column=0),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="Black",
            coordinate=Coordinate(row=3, column=0),
        ),
    )
    assert result.current_player == "White"
    assert result.turn_number == 3

def test_apply_diagonal_any_allows_backward_relocation() -> None:
    game = create_movement_game(
        MovementDirection.DIAGONAL_ANY,
    )
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=4, column=1),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=4, column=1),
        coordinate=Coordinate(row=5, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.pieces[0].coordinate == Coordinate(
        row=5,
        column=2,
    )
    assert result.current_player == "Black"

def test_relocation_does_not_modify_previous_state() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    original_piece = state.pieces[0]
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=4, column=1),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result is not state
    assert state.pieces == (original_piece,)
    assert state.pieces[0].coordinate == Coordinate(
        row=5,
        column=0,
    )
    assert result.pieces[0].coordinate == Coordinate(
        row=4,
        column=1,
    )

def test_apply_places_piece_and_advances_turn() -> None:
    game = load_tictactoe()
    initial_state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=1, column=1),
    )

    new_state = MoveExecutor(game).apply(initial_state, move)

    assert new_state.pieces == (
        PlacedPiece(
            piece_name="Mark",
            owner="X",
            coordinate=Coordinate(row=1, column=1),
        ),
    )
    assert new_state.current_player == "O"
    assert new_state.turn_number == 2
    assert new_state.status is GameStatus.ONGOING

def test_apply_does_not_modify_previous_state() -> None:
    game = load_tictactoe()
    initial_state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    new_state = MoveExecutor(game).apply(initial_state, move)

    assert new_state is not initial_state
    assert initial_state.pieces == ()
    assert initial_state.current_player == "X"
    assert initial_state.turn_number == 1

def test_apply_rotates_back_to_first_player() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
        ),
        current_player="O",
        turn_number=2,
    )
    move = Move(
        player="O",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=1),
    )

    new_state = MoveExecutor(game).apply(state, move)

    assert new_state.current_player == "X"
    assert new_state.turn_number == 3

def test_apply_rejects_move_after_game_has_ended() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(),
        current_player="X",
        turn_number=6,
        status=GameStatus.WON,
        winner="X",
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="game has ended"):
        MoveExecutor(game).apply(state, move)

def test_apply_rejects_wrong_player_turn() -> None:
    game = load_tictactoe()
    state = GameInitializer().initialize(game)
    move = Move(
        player="O",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="It is X's turn"):
        MoveExecutor(game).apply(state, move)


@pytest.mark.parametrize(
    "coordinate",
    [
        Coordinate(row=3, column=0),
        Coordinate(row=0, column=3),
    ],
)
def test_apply_rejects_coordinate_outside_board(
    coordinate: Coordinate,
) -> None:
    game = load_tictactoe()
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=coordinate,
    )

    with pytest.raises(InvalidMoveError, match="outside"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_unknown_piece_type() -> None:
    game = load_tictactoe()
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Unknown",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="Unknown piece type"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_piece_not_owned_by_player() -> None:
    game = load_tictactoe()
    mark = next(piece for piece in game.pieces if piece.name == "Mark")
    restricted_mark = replace(mark, owners=("O",))
    restricted_game = replace(
        game,
        pieces=(restricted_mark,),
    )
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="does not own"):
        MoveExecutor(restricted_game).apply(state, move)


def test_apply_rejects_occupied_cell() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=1),
            ),
        ),
        current_player="X",
        turn_number=2,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=1, column=1),
    )

    with pytest.raises(InvalidMoveError, match="already occupied"):
        MoveExecutor(game).apply(state, move)


def test_apply_rejects_non_playable_cell() -> None:
    game = load_tictactoe()
    dark_board = replace(
        game.board,
        playable_cells=PlayableCells.DARK,
    )
    dark_cells_game = replace(game, board=dark_board)
    state = GameInitializer().initialize(game)
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=0),
    )

    with pytest.raises(InvalidMoveError, match="not a playable dark cell"):
        MoveExecutor(dark_cells_game).apply(state, move)

def test_apply_marks_state_as_won_after_winning_move() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=1),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=1),
            ),
        ),
        current_player="X",
        turn_number=5,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=0, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.status is GameStatus.WON
    assert result.winner == "X"
    assert result.turn_number == 6
    assert result.current_player == "O"


def test_apply_marks_state_as_drawn_after_board_filling_move() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=0, column=1),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=2),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=1, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=1),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=1, column=2),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="O",
                coordinate=Coordinate(row=2, column=0),
            ),
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=2, column=1),
            ),
        ),
        current_player="X",
        turn_number=9,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        coordinate=Coordinate(row=2, column=2),
    )

    result = MoveExecutor(game).apply(state, move)

    assert result.status is GameStatus.DRAWN
    assert result.winner is None
    assert result.turn_number == 10
    assert result.current_player == "O"

def test_relocation_rejects_source_outside_board() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=8, column=1),
        coordinate=Coordinate(row=4, column=1),
    )

    with pytest.raises(InvalidMoveError, match="outside"):
        MoveExecutor(game).apply(state, move)


def test_relocation_rejects_empty_source() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=2),
        coordinate=Coordinate(row=4, column=3),
    )

    with pytest.raises(
        InvalidMoveError,
        match="does not contain a piece",
    ):
        MoveExecutor(game).apply(state, move)


def test_relocation_rejects_opponent_piece() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="Black",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=4, column=1),
    )

    with pytest.raises(
        InvalidMoveError,
        match="does not own",
    ):
        MoveExecutor(game).apply(state, move)


def test_relocation_rejects_wrong_piece_type() -> None:
    game = create_movement_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="King",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=4, column=1),
    )

    with pytest.raises(
        InvalidMoveError,
        match="'King', not 'Man'",
    ):
        MoveExecutor(game).apply(state, move)


@pytest.mark.parametrize(
    "destination",
    [
        Coordinate(row=5, column=2),
        Coordinate(row=3, column=2),
    ],
)
def test_relocation_rejects_invalid_diagonal_geometry(
    destination: Coordinate,
) -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=destination,
    )

    with pytest.raises(
        InvalidMoveError,
        match="must move diagonally by 1",
    ):
        MoveExecutor(game).apply(state, move)


def test_forward_relocation_rejects_backward_direction() -> None:
    game = create_movement_game()
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=4, column=1),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=4, column=1),
        coordinate=Coordinate(row=5, column=2),
    )

    with pytest.raises(
        InvalidMoveError,
        match="must move piece 'Man' forward",
    ):
        MoveExecutor(game).apply(state, move)


def test_relocation_rejects_occupied_destination() -> None:
    game = create_movement_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=4, column=1),
    )

    with pytest.raises(
        InvalidMoveError,
        match="already occupied",
    ):
        MoveExecutor(game).apply(state, move)


def test_movement_piece_rejects_placement_request() -> None:
    game = create_movement_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(),
        current_player="White",
        turn_number=1,
    )
    move = Move(
        player="White",
        piece_name="Man",
        coordinate=Coordinate(row=5, column=0),
    )

    with pytest.raises(
        InvalidMoveError,
        match="does not support placement",
    ):
        MoveExecutor(game).apply(state, move)


def test_placement_piece_rejects_relocation_request() -> None:
    game = load_tictactoe()
    state = GameState(
        rows=3,
        columns=3,
        pieces=(
            PlacedPiece(
                piece_name="Mark",
                owner="X",
                coordinate=Coordinate(row=0, column=0),
            ),
        ),
        current_player="X",
        turn_number=2,
    )
    move = Move(
        player="X",
        piece_name="Mark",
        source=Coordinate(row=0, column=0),
        coordinate=Coordinate(row=1, column=1),
    )

    with pytest.raises(
        InvalidMoveError,
        match="does not support relocation",
    ):
        MoveExecutor(game).apply(state, move)


def test_forward_relocation_requires_player_direction() -> None:
    game = create_movement_game()
    white, black = game.players
    invalid_game = replace(
        game,
        players=(
            replace(white, forward=None),
            black,
        ),
    )
    state = create_movement_state(
        owner="White",
        coordinate=Coordinate(row=5, column=0),
        current_player="White",
    )
    move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=4, column=1),
    )

    with pytest.raises(
        InvalidMoveError,
        match="has no forward direction",
    ):
        MoveExecutor(invalid_game).apply(state, move)

def test_relocation_rejects_ordinary_move_when_capture_is_available() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=6),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    ordinary_move = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=6),
        coordinate=Coordinate(row=4, column=7),
    )

    with pytest.raises(
        InvalidMoveError,
        match="A capture is mandatory when available",
    ):
        MoveExecutor(game).apply(
            state,
            ordinary_move,
        )

def test_relocation_allows_mandatory_capture() -> None:
    game = create_capture_game()
    state = GameState(
        rows=8,
        columns=8,
        pieces=(
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=6),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="White",
                coordinate=Coordinate(row=5, column=0),
            ),
            PlacedPiece(
                piece_name="Man",
                owner="Black",
                coordinate=Coordinate(row=4, column=1),
            ),
        ),
        current_player="White",
        turn_number=1,
    )
    capture = Move(
        player="White",
        piece_name="Man",
        source=Coordinate(row=5, column=0),
        coordinate=Coordinate(row=3, column=2),
    )

    result = MoveExecutor(game).apply(
        state,
        capture,
    )

    assert result.pieces == (
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=5, column=6),
        ),
        PlacedPiece(
            piece_name="Man",
            owner="White",
            coordinate=Coordinate(row=3, column=2),
        ),
    )
    assert result.current_player == "Black"
    assert result.turn_number == 2

def test_column_placement_falls_to_bottom_row() -> None:
    game = load_connectfour()
    initial_state = GameInitializer().initialize(game)
    executor = MoveExecutor(game)

    result = executor.apply(
        initial_state,
        Move(
            player="Red",
            piece_name="Disc",
            coordinate=Coordinate(
                row=0,
                column=3,
            ),
        ),
    )

    assert initial_state.pieces == ()
    assert result.pieces == (
        PlacedPiece(
            piece_name="Disc",
            owner="Red",
            coordinate=Coordinate(
                row=5,
                column=3,
            ),
        ),
    )
    assert result.current_player == "Yellow"
    assert result.turn_number == 2
    assert result.status is GameStatus.ONGOING

def test_column_placement_stacks_pieces_upward() -> None:
    game = load_connectfour()
    executor = MoveExecutor(game)
    state = GameInitializer().initialize(game)

    state = executor.apply(
        state,
        Move(
            player="Red",
            piece_name="Disc",
            coordinate=Coordinate(
                row=0,
                column=3,
            ),
        ),
    )

    result = executor.apply(
        state,
        Move(
            player="Yellow",
            piece_name="Disc",
            coordinate=Coordinate(
                row=0,
                column=3,
            ),
        ),
    )

    assert result.pieces[-2] == PlacedPiece(
        piece_name="Disc",
        owner="Red",
        coordinate=Coordinate(
            row=5,
            column=3,
        ),
    )
    assert result.pieces[-1] == PlacedPiece(
        piece_name="Disc",
        owner="Yellow",
        coordinate=Coordinate(
            row=4,
            column=3,
        ),
    )
    assert result.current_player == "Red"
    assert result.turn_number == 3
    assert result.status is GameStatus.ONGOING

def test_column_placement_rejects_full_column() -> None:
    game = load_connectfour()
    executor = MoveExecutor(game)

    pieces = tuple(
        PlacedPiece(
            piece_name="Disc",
            owner=(
                "Red"
                if row % 2 == 0
                else "Yellow"
            ),
            coordinate=Coordinate(
                row=row,
                column=3,
            ),
        )
        for row in range(6)
    )

    state = GameState(
        rows=6,
        columns=7,
        pieces=pieces,
        current_player="Red",
        turn_number=7,
    )

    with pytest.raises(
        InvalidMoveError,
        match=r"Column 3 is full\.",
    ):
        executor.apply(
            state,
            Move(
                player="Red",
                piece_name="Disc",
                coordinate=Coordinate(
                    row=0,
                    column=3,
                ),
            ),
        )

    assert state.pieces is pieces
    assert state.current_player == "Red"
    assert state.turn_number == 7
    assert state.status is GameStatus.ONGOING