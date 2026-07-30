# Defining a Game in Piecewise

Piecewise games are described using declarative `.game` files. A game definition specifies the board, players, pieces, initial setup, movement rules, and end-game conditions.

> The DSL is currently under development. The syntax documented here describes the initial MVP and may evolve alongside the parser and game engine.

## How it works

A `.game` file is parsed by a [Lark](https://github.com/lark-parser/lark)-based parser, which produces an AST that the game engine interprets at runtime.

```text
.game file -> Parser (Lark) -> AST -> Game Engine
```

## File structure

Create a file inside the `games/` directory using the `.game` extension:

```text
games/mygame.game
```

A complete game definition follows this general structure:

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

## Game declaration

Every file starts with the `game` keyword followed by a unique game name:

```text
game Checkers {
    ...
}
```

Game names must not contain spaces.

## Board

The `board` block defines the dimensions and usable cells of a rectangular grid.

```text
board {
    size: 8x8
    playable_cells: dark
}
```

Available cell configurations:

* `all`: every cell is playable;
* `dark`: only dark cells are playable;
* `light`: only light cells are playable.

Rows are numbered from top to bottom, starting from `1`. Columns are numbered from left to right, starting from `1`.

### Gravity

The optional `gravity` property controls how newly placed pieces behave:

```text
board {
    size: 6x7
    playable_cells: all
    gravity: down
}
```

The initial version supports `down`: a placed piece falls toward increasing row
numbers until it reaches the lowest available cell. When `gravity` is omitted,
pieces remain on the selected destination cell.

## Players

The `players` block declares the players and their turn order:

```text
players {
    player White {
        forward: up
    }

    player Black {
        forward: down
    }

    turn_order: White, Black
}
```

The optional `forward` property defines the direction associated with a player:

* `up`: toward decreasing row numbers;
* `down`: toward increasing row numbers.

Every player referenced by a piece must be declared in this block.

## Pieces

Each `piece` block defines one piece type:

```text
piece Man {
    owner: White, Black
    move: diagonal forward 1 if empty
    capture: diagonal forward 2 if enemy
    promote: back_rank -> King
}
```

### Owner

The `owner` property lists the players that may own the piece:

```text
owner: White, Black
```

### Movement

A movement rule describes its direction, orientation, distance, and destination condition:

```text
move: diagonal forward 1 if empty
```

Supported orientations in the initial version:

* `forward`: only toward the owner’s forward direction;
* `any`: both forward and backward.

The destination must be a playable cell inside the board.

### Capture

A capture rule describes a jump over an enemy piece:

```text
capture: diagonal any 2 if enemy
```

A successful capture removes the enemy piece that was jumped over.

The initial version does not support mandatory captures or multiple captures during the same turn.

### Promotion

A piece may be transformed when it reaches the opponent’s back rank:

```text
promote: back_rank -> King
```

The target piece type, such as `King`, must be declared in the same game file.

## Initial setup

The `setup` block defines the pieces placed on the board at the beginning of the game:

```text
setup {
    place: Man owned_by White on rows 6..8 playable_cells
    place: Man owned_by Black on rows 1..3 playable_cells
}
```

Each placement specifies:

* the piece type;
* its owner;
* the rows on which it is placed;
* whether placement is restricted to playable cells.

A game such as Tic-Tac-Toe may begin with an empty board and therefore does not require initial piece placement.

## Placement games

Games that create pieces during play use a `place` rule instead of a movement
rule.

### Free placement

```text
piece Mark {
    owner: X, O
    place: any_empty_cell
}
```

`any_empty_cell` allows the current player to place one owned piece on any empty
playable cell. This rule is suitable for games such as Tic-Tac-Toe.

### Column placement

```text
piece Disc {
    owner: Red, Yellow
    place: any_non_full_column
}
```

`any_non_full_column` allows the current player to select a column containing at
least one empty cell. If the board defines `gravity: down`, the engine places
the piece in the lowest available cell of the selected column.

## Win and draw conditions

The `win_condition` block defines when the game ends:

```text
win_condition {
    no_pieces_left: opponent -> win
    no_moves_left: opponent -> win
}
```

Examples of supported conditions include:

```text
align: 3 same_row -> win
align: 3 same_col -> win
align: 3 diagonal -> win
board_full: no_winner -> draw
```

An `align` condition specifies how many consecutive pieces owned by the same
player are required. Supported directions are:

* `same_row`: horizontal alignment;
* `same_col`: vertical alignment;
* `diagonal`: alignment in either diagonal direction.

All end-game conditions are evaluated after a valid action has been completed.

## Checkers example

```text
game Checkers {

    board {
        size: 8x8
        playable_cells: dark
    }

    players {
        player White {
            forward: up
        }

        player Black {
            forward: down
        }

        turn_order: White, Black
    }

    piece Man {
        owner: White, Black
        move: diagonal forward 1 if empty
        capture: diagonal forward 2 if enemy
        promote: back_rank -> King
    }

    piece King {
        owner: White, Black
        move: diagonal any 1 if empty
        capture: diagonal any 2 if enemy
    }

    setup {
        place: Man owned_by White on rows 6..8 playable_cells
        place: Man owned_by Black on rows 1..3 playable_cells
    }

    win_condition {
        no_pieces_left: opponent -> win
        no_moves_left: opponent -> win
    }
}
```

## Connect Four example

```text
game ConnectFour {

    board {
        size: 6x7
        playable_cells: all
        gravity: down
    }

    players {
        player Red
        player Yellow
        turn_order: Red, Yellow
    }

    piece Disc {
        owner: Red, Yellow
        place: any_non_full_column
    }

    win_condition {
        align: 4 same_row -> win
        align: 4 same_col -> win
        align: 4 diagonal -> win
        board_full: no_winner -> draw
    }
}
```

## Validation rules

A game definition is invalid when:

* the game does not declare a board;
* fewer than two players are declared;
* `turn_order` references an undeclared player;
* a piece references an undeclared owner;
* a promotion references an undeclared piece type;
* the setup references an undeclared player or piece;
* a setup position falls outside the board;
* the same initial cell receives more than one piece;
* `gravity` has an unsupported value;
* `any_non_full_column` is used on a board without columns;
* an `align` condition requires fewer than two pieces;
* the required alignment cannot fit on the board in any declared direction;
* a piece declares neither a `move` rule nor a `place` rule;
* no win or draw condition is declared.
