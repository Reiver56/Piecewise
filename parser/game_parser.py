from pathlib import Path

from lark import Lark, Tree
from parser.ast_nodes import GameDefinition
from parser.ast_transformer import GameAstTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAMMAR_PATH = PROJECT_ROOT / "grammar" / "piecewise.lark"


class GameParser:
    """Parse Piecewise game definitions using the Lark grammar."""

    def __init__(self, grammar_path: Path | str = DEFAULT_GRAMMAR_PATH) -> None:
        self.grammar_path = Path(grammar_path)

        grammar_text = self.grammar_path.read_text(encoding="utf-8")

        self._parser = Lark(
            grammar_text,
            parser="lalr",
            start="start",
            propagate_positions=True,
        )

    def parse(self, source: str) -> Tree:
        """Parse a Piecewise game definition from a string."""
        return self._parser.parse(source)

    def parse_file(self, game_path: Path | str) -> Tree:
        """Read and parse a Piecewise .game file."""
        path = Path(game_path)

        if path.suffix != ".game":
            raise ValueError(f"Expected a .game file, received: {path}")

        source = path.read_text(encoding="utf-8")
        return self.parse(source)

    def parse_game(self, source: str) -> GameDefinition:
        """Parse source text and transform it into a game definition."""
        parse_tree = self.parse(source)
        return GameAstTransformer().transform(parse_tree)

    def parse_game_file(
        self,
        game_path: Path | str,
    ) -> GameDefinition:
        """Parse a .game file and transform it into a game definition."""
        parse_tree = self.parse_file(game_path)
        return GameAstTransformer().transform(parse_tree)