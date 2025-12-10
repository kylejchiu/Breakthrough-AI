#!/usr/bin/env python3
"""Example: Tournament between multiple random players."""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from breakthrough.config import setup_logging, analyze_tournament_results
from breakthrough.engine import Player
from breakthrough.llm_players import RandomPlayer
from breakthrough.tournament import Tournament


def main():
    """Run a tournament example."""
    # Set up logging
    logger = setup_logging(level="INFO")
    logger.info("Starting tournament example...")
    
    # Create players
    player1 = RandomPlayer("Rand-AlphaBot", Player.WHITE)
    player2 = RandomPlayer("Rand-BetaBot", Player.BLACK)
    
    # Run tournament
    tournament = Tournament(
        player1,
        player2,
        num_games=5,
        log_dir="./logs",
        data_dir="./data"
    )
    
    print("\n" + "="*60)
    print("BREAKTHROUGH TOURNAMENT")
    print("="*60)
    print(f"Players: {player1.name} vs {player2.name}")
    print(f"Games: {tournament.num_games}")
    print("="*60 + "\n")
    
    # Run the tournament
    stats = tournament.run()
    
    # Print summary
    tournament.print_summary()
    
    # Print detailed game results
    print("\nDetailed Game Results:")
    print("-" * 60)
    for result in tournament.results:
        winner = result.winner or "Draw"
        print(f"Game {result.game_id}: {winner} ({result.move_count} moves, {result.duration_seconds:.2f}s)")
    
    # Analyze results
    print("\nTournament Analysis:")
    print("-" * 60)
    analysis = analyze_tournament_results(tournament.results)
    for key, value in analysis.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
