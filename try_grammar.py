from pathlib import Path
from parser.game_parser import GameParser

from lark import Lark

parser = GameParser()
tree = parser.parse_file("games/tictactoe.game")

print("Parsing completed successfully!")
print(tree.pretty())