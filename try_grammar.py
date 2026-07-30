from parser.ast_transformer import GameAstTransformer
from parser.game_parser import GameParser


parser = GameParser()
parse_tree = parser.parse_file("games/tictactoe.game")

transformer = GameAstTransformer()
game = transformer.transform(parse_tree)

print(game)
print()
print(f"Game: {game.name}")
print(f"Board: {game.board.rows}x{game.board.columns}")
print(f"Players: {[player.name for player in game.players]}")
print(f"Pieces: {[piece.name for piece in game.pieces]}")
print(f"Win conditions: {len(game.win_conditions)}")