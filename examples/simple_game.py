#!/usr/bin/env python3
"""Example: Simple game between two random players."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from breakthrough.config import setup_logging
from breakthrough.engine import Game, Player
from breakthrough.llm_players import RandomPlayer


def main():
    """Run a simple game between two random players."""
    # Set up logging
    logger = setup_logging(level="INFO")
    logger.info("Starting simple game example...")
    
    # Create players
    player1 = RandomPlayer("RandomBot1", Player.WHITE)
    player2 = RandomPlayer("RandomBot2", Player.BLACK)
    
    # Create and play game
    game = Game()
    
    print("\n" + "="*60)
    print("BREAKTHROUGH GAME - Random vs Random")
    print("="*60)
    print("\nStarting position:")
    print(game)
    
    move_count = 0
    max_moves = 100
    
    while not game.game_over and move_count < max_moves:
        if game.current_player == Player.WHITE:
            player = player1
        else:
            player = player2
        
        # Get and make move
        move = player.get_move(game)
        game.make_move(move)
        move_count += 1
        
        print(f"\nMove {move_count}: {player.name} plays {move}")
        print(game)
    
    print("\n" + "="*60)
    print("GAME RESULT")
    print("="*60)
    if game.winner:
        print(f"Winner: {game.winner.name}")
    else:
        print("Result: Draw")
    print(f"Total moves: {move_count}")
    print(f"Player 1 ({player1.name}) moves: {player1.move_count}")
    print(f"Player 2 ({player2.name}) moves: {player2.move_count}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
