## How it works
 
A `.game` file is parsed by a [Lark](https://github.com/lark-parser/lark)-based parser, which produces an AST that the game engine interprets at runtime.
 
```
.game file -> Parser (Lark) -> AST -> Game Engine