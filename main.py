#!/usr/bin/env python3
"""Main CLI for running Breakthrough tournaments between LLMs."""

import argparse
import logging
import sys
from pathlib import Path

from breakthrough.config import setup_logging, load_environment_variables, check_api_keys, print_available_apis
from breakthrough.engine import Player
from breakthrough.llm_players import OpenAIPlayer, AnthropicPlayer, RandomPlayer
from breakthrough.tournament import Tournament


def create_player(player_type: str, name: str, color: Player, model: str = None) -> object:
    """Create a player of the specified type."""
    if player_type.lower() == "random":
        return RandomPlayer(name, color)
    elif player_type.lower() == "openai":
        return OpenAIPlayer(name, color, model or "gpt-4-turbo-preview")
    elif player_type.lower() == "anthropic":
        return AnthropicPlayer(name, color, model or "claude-3-5-sonnet-20241022")
    else:
        raise ValueError(f"Unknown player type: {player_type}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Run tournaments between LLM players in the game of Breakthrough",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 5 games between two random players
  python main.py --games 5 --player1 random --player2 random
  
  # Run 3 games between OpenAI and Anthropic
  python main.py --games 3 --player1 openai --player2 anthropic \\
    --model1 gpt-4-turbo-preview --model2 claude-3-5-sonnet-20241022
  
  # Check available APIs
  python main.py --check-apis
        """
    )
    
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="Number of games to play in tournament (default: 1)"
    )
    parser.add_argument(
        "--player1",
        type=str,
        default="random",
        help="Type of player 1: random, openai, anthropic (default: random)"
    )
    parser.add_argument(
        "--player2",
        type=str,
        default="random",
        help="Type of player 2: random, openai, anthropic (default: random)"
    )
    parser.add_argument(
        "--name1",
        type=str,
        help="Name for player 1 (default: based on player type)"
    )
    parser.add_argument(
        "--name2",
        type=str,
        help="Name for player 2 (default: based on player type)"
    )
    parser.add_argument(
        "--model1",
        type=str,
        help="Model for player 1 (if applicable)"
    )
    parser.add_argument(
        "--model2",
        type=str,
        help="Model for player 2 (if applicable)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="Directory for log files (default: ./logs)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Directory for tournament data (default: ./data)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--check-apis",
        action="store_true",
        help="Check which API keys are configured and exit"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Path to .env file with API keys (default: .env)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_dir, args.log_level)
    logger.info("Breakthrough AI Tournament System")
    logger.info("=" * 50)
    
    # Load environment variables
    load_environment_variables(args.env_file)
    
    # Check APIs if requested
    if args.check_apis:
        print_available_apis()
        return 0
    
    try:
        # Create players
        name1 = args.name1 or f"{args.player1.capitalize()}-Player1"
        name2 = args.name2 or f"{args.player2.capitalize()}-Player2"
        
        logger.info(f"Creating player 1: {args.player1.upper()} ({name1})")
        player1 = create_player(args.player1, name1, Player.WHITE, args.model1)
        
        logger.info(f"Creating player 2: {args.player2.upper()} ({name2})")
        player2 = create_player(args.player2, name2, Player.BLACK, args.model2)
        
        # Run tournament
        logger.info(f"Starting tournament: {args.games} game(s)")
        tournament = Tournament(
            player1,
            player2,
            num_games=args.games,
            log_dir=args.log_dir,
            data_dir=args.data_dir
        )
        
        stats = tournament.run()
        tournament.print_summary()
        
        # Print detailed results
        logger.info("Tournament complete!")
        logger.info(f"  {player1.name} wins: {stats.player1_wins}")
        logger.info(f"  {player2.name} wins: {stats.player2_wins}")
        logger.info(f"  Draws: {stats.draws}")
        logger.info(f"  Total duration: {stats.total_duration:.2f}s")
        
        return 0
        
    except Exception as e:
        logger.error(f"Tournament failed: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
