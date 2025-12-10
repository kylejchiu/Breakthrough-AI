"""Configuration and utility functions."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv


def setup_logging(log_dir: str = "./logs", level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_dir: Directory to store log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("breakthrough")
    logger.setLevel(getattr(logging, level))
    
    # File handler
    log_file = Path(log_dir) / "breakthrough.log"
    fh = logging.FileHandler(log_file)
    fh.setLevel(getattr(logging, level))
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def load_environment_variables(env_file: str = ".env") -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file
    """
    if Path(env_file).exists():
        load_dotenv(env_file)
    else:
        print(f"Warning: {env_file} not found. Make sure to set environment variables manually.")


def check_api_keys() -> dict:
    """
    Check which API keys are available.
    
    Returns:
        Dictionary with API provider names as keys and availability as boolean values
    """
    available_keys = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
    
    return available_keys


def print_available_apis():
    """Print available API keys."""
    available = check_api_keys()
    
    print("\nAvailable APIs:")
    for provider, available_flag in available.items():
        status = "✓ Available" if available_flag else "✗ Not configured"
        print(f"  {provider.capitalize()}: {status}")
    
    if not any(available.values()):
        print("\nNo API keys configured! Set up environment variables in .env file:")
        print("  OPENAI_API_KEY=your_key_here")
        print("  ANTHROPIC_API_KEY=your_key_here")


# Game analysis utilities

def analyze_game_moves(moves: list) -> dict:
    """
    Analyze game moves.
    
    Args:
        moves: List of moves in notation format
        
    Returns:
        Dictionary with move statistics
    """
    return {
        "total_moves": len(moves),
        "average_move_notation_length": sum(len(m) for m in moves) / len(moves) if moves else 0,
    }


def analyze_tournament_results(results: list) -> dict:
    """
    Analyze tournament results.
    
    Args:
        results: List of GameResult objects
        
    Returns:
        Dictionary with tournament statistics
    """
    if not results:
        return {}
    
    player1_wins = sum(1 for r in results if r.winner == results[0].player1_name)
    player2_wins = sum(1 for r in results if r.winner == results[0].player2_name)
    draws = sum(1 for r in results if r.is_draw)
    
    total_moves = sum(r.move_count for r in results)
    avg_moves = total_moves / len(results) if results else 0
    
    return {
        f"{results[0].player1_name}_wins": player1_wins,
        f"{results[0].player2_name}_wins": player2_wins,
        "draws": draws,
        "total_games": len(results),
        "total_moves": total_moves,
        "avg_moves_per_game": avg_moves,
        "avg_game_duration": sum(r.duration_seconds for r in results) / len(results) if results else 0,
    }
