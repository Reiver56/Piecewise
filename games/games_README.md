# Defining a Game in Piecewise

Piecewise games are described using declarative `.game` files.

> Piecewise is under development. Tic-Tac-Toe is fully supported. The parser
> and AST also support the directional movement, capture, promotion, and
> initial-setup subset used by Checkers. Single captures and back-rank
> promotion already execute at runtime; Checkers end-condition targets are
> validated semantically. Their runtime evaluation and the Connect Four
> extensions remain future increments.

## Processing pipeline

```text
.game file -> Lark parser -> Parse tree -> AST transformer -> GameDefinition -> SemanticValidator
```

Semantic validation and runtime execution are separate processing stages. The
currently supported Tic-Tac-Toe rules can be executed by the engine.

## Create a game file

Place the definition in `games/` and use the `.game` extension:

```text
games/mygame.game
```

The currently supported structure is:

```text
game GameName {
    board {
        ...
    }

    players {
        ...
    }

    piece PieceName {
        ...
    }

    setup {
        ...
    }

    win_condition {
        ...
    }
}
```

The order of these blocks is significant in the current grammar. The `setup`
block is optional; when present, it must follow every piece block and precede
`win_condition`.

## Currently supported syntax

### Game declaration

```text
game TicTacToe {
    ...
}
```

Names use identifier syntax: they may contain letters, digits, and underscores,
but cannot contain spaces or start with a digit.

### Board

```text
board {
    size: 3x3
    playable_cells: all
}
```

`size` defines rows followed by columns. `playable_cells` accepts:

- `all`;
- `dark`;
- `light`.

Only `all` is currently exercised by the implemented Tic-Tac-Toe example.

### Players

```text
players {
    player X
    player O
    turn_order: X, O
}
```

At least one `player` declaration is required syntactically. Whether the turn
order contains exactly the declared players is checked by the semantic
validator.

### Pieces

```text
piece Mark {
    owner: X, O
    place: any_empty_cell
}
```

The current grammar supports:

- a list of owners;
- placement on any empty cell;
- non-capturing `diagonal forward` and `diagonal any` movement rules;
- `diagonal forward` and `diagonal any` capture rules using `if enemy`;
- back-rank promotion to a named piece type.

For example:

```text
piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
    capture: diagonal forward 2 if enemy
    promote: back_rank -> King
}
```

Capture declarations are parsed, validated, and supported for single runtime
jumps. Promotion declarations are parsed into immutable `PromotionRule`
objects; target validation and runtime replacement are not implemented yet.

### Initial setup

The optional setup block follows all piece blocks:

```text
setup {
    place: Man owned_by White on rows 6..8 playable_cells
    place: Man owned_by Black on rows 1..3 playable_cells
}
```

Each rule selects a piece type, its owner, an inclusive one-based row range,
and playable cells only. The parser preserves these declarations as ordered,
immutable `SetupRule` objects. Semantic validation checks references, ownership,
row ordering, board bounds, and overlapping ranges. `GameInitializer` then
converts the one-based rows to zero-based coordinates and places pieces only on
the selected playable cells.

### Win and draw conditions

```text
win_condition {
    align: 3 same_row -> win
    align: 3 same_col -> win
    align: 3 diagonal -> win
    board_full: no_winner -> draw
}
```

Supported alignment directions are:

- `same_row`;
- `same_col`;
- `diagonal`.

The parser records these conditions in the AST, and the engine evaluates the
currently supported alignment and full-board conditions.

Checkers also uses player-state victory conditions:

```text
win_condition {
    no_pieces_left: opponent -> win
    no_moves_left: opponent -> win
}
```

The only supported target is currently `opponent`. These declarations become
immutable `NoPiecesLeftCondition` and `NoMovesLeftCondition` objects containing
`PlayerTarget.OPPONENT`. Parsing, AST transformation, and semantic validation
are implemented. The semantic validator requires exactly two declared players
so that `opponent` is unambiguous; runtime evaluation remains a future
increment.

## Complete supported example

```text
game TicTacToe {

    board {
        size: 3x3
        playable_cells: all
    }

    players {
        player X
        player O
        turn_order: X, O
    }

    piece Mark {
        owner: X, O
        place: any_empty_cell
    }

    win_condition {
        align: 3 same_row -> win
        align: 3 same_col -> win
        align: 3 diagonal -> win
        board_full: no_winner -> draw
    }
}
```

This file can be parsed with:

```python
from parser.game_parser import GameParser

game = GameParser().parse_game_file("games/tictactoe.game")
```

## Partially supported and future syntax

### Checkers

`checkers.game` combines:

- supported player directions, diagonal movement, single capture, promotion,
  initial piece placement, and player-state end-condition syntax/AST;
- supported single-jump capture and back-rank promotion execution;
- supported semantic validation of the `opponent` target with exactly two
  declared players;
- planned runtime evaluation of victory caused by the opponent having no
  pieces or legal moves;
- planned multiple- and mandatory-capture behaviour.

### Connect Four

`connectfour.game` explores syntax for:

- downward gravity;
- placement in non-full columns;
- alignments of four pieces.

The remaining constructs must be introduced together with AST changes and
automated tests.

## Semantic rules

The current semantic validator rejects definitions when:

- board dimensions are not positive;
- player or piece names are duplicated;
- `turn_order` references undeclared players;
- a piece references an undeclared owner;
- a piece declares neither placement nor movement, or declares both;
- a movement distance is not positive;
- a forward-moving owner has no declared forward direction;
- a capture lacks movement, has a non-positive distance, or needs an undeclared
  forward direction;
- a setup rule references an undeclared piece or player;
- a setup owner is not allowed for the referenced piece;
- a setup row range is malformed, outside the board, or overlaps another rule;
- an alignment length cannot fit on the board;
- declared players are missing from the turn order.

Promotion references are not yet checked semantically.

## Extension checklist

When adding a DSL construct:

1. define the intended syntax in a `.game` example;
2. update `grammar/piecewise.lark`;
3. extend the AST when a new concept is introduced;
4. update `GameAstTransformer`;
5. add valid and invalid tests;
6. update the relevant README files.
