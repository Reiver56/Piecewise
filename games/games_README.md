# Defining a Game in Piecewise

Piecewise games are described using declarative `.game` files.

> Piecewise is under development. Tic-Tac-Toe is fully supported. The parser
> and AST also support the directional movement and initial-setup subset used
> by Checkers, while its capture, promotion, and end-condition constructs and
> the Connect Four extensions remain future increments.

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
- non-capturing `diagonal forward` and `diagonal any` movement rules.

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

## Designed future syntax

### Checkers

`checkers.game` explores syntax for:

- player directions;
- diagonal movement;
- capture;
- promotion;
- initial piece placement, which is now supported by the grammar and AST;
- loss caused by having no pieces or legal moves.

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
- a setup rule references an undeclared piece or player;
- a setup owner is not allowed for the referenced piece;
- a setup row range is malformed, outside the board, or overlaps another rule;
- an alignment length cannot fit on the board;
- declared players are missing from the turn order.

## Extension checklist

When adding a DSL construct:

1. define the intended syntax in a `.game` example;
2. update `grammar/piecewise.lark`;
3. extend the AST when a new concept is introduced;
4. update `GameAstTransformer`;
5. add valid and invalid tests;
6. update the relevant README files.
