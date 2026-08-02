# Defining a Game in Piecewise

Piecewise games are described using declarative `.game` files.

> Piecewise is under development. The current parser supports the Tic-Tac-Toe
> subset documented below. Checkers and Connect Four are design examples for
> future language increments and cannot be parsed by the current grammar yet.

## Processing pipeline

```text
.game file -> Lark parser -> Parse tree -> AST transformer -> GameDefinition -> SemanticValidator
```

Semantic validation is available as a separate processing stage. Game execution
will be added in a future increment.

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

    win_condition {
        ...
    }
}
```

The order of these blocks is significant in the current grammar.

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
- placement on any empty cell.

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

The parser records these conditions in the AST. The engine does not evaluate
them yet.

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
- initial piece placement;
- loss caused by having no pieces or legal moves.

### Connect Four

`connectfour.game` explores syntax for:

- downward gravity;
- placement in non-full columns;
- alignments of four pieces.

These constructs are not part of `grammar/piecewise.lark` yet. They must be
introduced together with AST changes and automated tests.

## Semantic rules

The current semantic validator rejects definitions when:

- board dimensions are not positive;
- player or piece names are duplicated;
- `turn_order` references undeclared players;
- a piece references an undeclared owner;
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

