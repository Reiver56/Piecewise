

# Piecewise
<p align="center">
  <img src="giphy.gif" alt="demo" width="600"/>
</p>
A Domain-Specific Language (DSL) for defining turn-based board games.

# What is it?

Piecewise lets you describe any board game in a simple, declarative language. You define the board, the pieces, the movement rules, and the win conditions — the engine does the rest.

## Project structure
 
```
piecewise/
├── grammar/        # Lark grammar definition
├── parser/         # Parser and AST transformer
├── engine/         # Game engine (move validation, turn management)
├── games/          # Example .game files (Checkers, Tic-Tac-Toe, ...)
└── tests/          # Unit tests
```
