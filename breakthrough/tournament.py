"""Tournament system for organizing multiple games between LLM players."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import os

from .engine import Game, Player, Move
from .llm_players import LLMPlayer


logger = logging.getLogger(__name__)


@dataclass
class GameResult:
    """Result of a single game."""
    game_id: int
    player1_name: str
    player2_name: str
    winner: Optional[str]
    loser: Optional[str]
    is_draw: bool
    moves: List[str]
    move_count: int
    timestamp: str
    duration_seconds: float
    board_history: List[str]


@dataclass
class TournamentStats:
    """Statistics for a tournament."""
    total_games: int
    player1_wins: int
    player2_wins: int
    draws: int
    total_duration: float
    avg_game_duration: float


class Tournament:
    """Manages tournaments between LLM players."""
    
    def __init__(self, player1: LLMPlayer, player2: LLMPlayer, num_games: int = 1, 
                 log_dir: str = "./logs", data_dir: str = "./data"):
        """
        Initialize a tournament.
        
        Args:
            player1: First player (will play WHITE first)
            player2: Second player (will play BLACK first)
            num_games: Number of games to play
            log_dir: Directory for game logs
            data_dir: Directory for game data
        """
        self.player1 = player1
        self.player2 = player2
        self.num_games = num_games
        self.log_dir = Path(log_dir)
        self.data_dir = Path(data_dir)
        
        # Create directories if they don't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.results: List[GameResult] = []
        self.tournament_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def run(self) -> TournamentStats:
        """
        Run the tournament.
        
        Returns:
            Tournament statistics
        """
        logger.info(f"Starting tournament: {self.player1.name} vs {self.player2.name}")
        logger.info(f"Number of games: {self.num_games}")
        
        total_duration = 0
        
        for game_num in range(1, self.num_games + 1):
            # Alternate colors
            if game_num % 2 == 1:
                white_player = self.player1
                black_player = self.player2
            else:
                white_player = self.player2
                black_player = self.player1
            
            logger.info(f"\nGame {game_num}/{self.num_games}: {white_player.name} (WHITE) vs {black_player.name} (BLACK)")
            
            result, duration = self._play_game(game_num, white_player, black_player)
            self.results.append(result)
            total_duration += duration
            
            logger.info(f"Game {game_num} finished: {result.winner or 'Draw'}")
        
        # Calculate statistics
        stats = self._calculate_stats(total_duration)
        
        # Save results
        self._save_results()
        
        logger.info(f"\nTournament completed!")
        logger.info(f"Results: {self.player1.name} wins: {stats.player1_wins}, "
                   f"{self.player2.name} wins: {stats.player2_wins}, Draws: {stats.draws}")
        
        return stats
    
    def _play_game(self, game_id: int, white_player: LLMPlayer, black_player: LLMPlayer) -> Tuple[GameResult, float]:
        """
        Play a single game.
        
        Args:
            game_id: ID for this game
            white_player: Player controlling WHITE
            black_player: Player controlling BLACK
            
        Returns:
            Tuple of (GameResult, duration in seconds)
        """
        import time
        start_time = time.time()
        
        game = Game()
        white_player.move_count = 0
        black_player.move_count = 0
        
        board_history = [game.get_board_state()]
        moves = []
        
        max_moves = 200  # Prevent infinite games
        move_count = 0
        
        while not game.game_over and move_count < max_moves:
            if game.current_player == Player.WHITE:
                player = white_player
            else:
                player = black_player
            
            try:
                move = player.get_move(game)
                if not game.make_move(move):
                    logger.error(f"Invalid move by {player.name}: {move}")
                    break
                
                moves.append(move.to_notation())
                board_history.append(game.get_board_state())
                move_count += 1
                
            except Exception as e:
                logger.error(f"Error during game {game_id}: {e}")
                break
        
        duration = time.time() - start_time
        
        # Determine result
        if game.winner == Player.WHITE:
            winner = white_player.name
            loser = black_player.name
            is_draw = False
        elif game.winner == Player.BLACK:
            winner = black_player.name
            loser = white_player.name
            is_draw = False
        else:
            winner = None
            loser = None
            is_draw = True
        
        result = GameResult(
            game_id=game_id,
            player1_name=white_player.name,
            player2_name=black_player.name,
            winner=winner,
            loser=loser,
            is_draw=is_draw,
            moves=moves,
            move_count=len(moves),
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            board_history=board_history
        )
        
        logger.info(f"Game {game_id} ended in {duration:.2f}s after {len(moves)} moves")
        
        return result, duration
    
    def _calculate_stats(self, total_duration: float) -> TournamentStats:
        """Calculate tournament statistics."""
        player1_wins = sum(1 for r in self.results if r.winner == self.player1.name)
        player2_wins = sum(1 for r in self.results if r.winner == self.player2.name)
        draws = sum(1 for r in self.results if r.is_draw)
        
        avg_duration = total_duration / len(self.results) if self.results else 0
        
        return TournamentStats(
            total_games=len(self.results),
            player1_wins=player1_wins,
            player2_wins=player2_wins,
            draws=draws,
            total_duration=total_duration,
            avg_game_duration=avg_duration
        )
    
    def _save_results(self):
        """Save tournament results to files."""
        # Save as JSON
        json_file = self.data_dir / f"tournament_{self.tournament_id}.json"
        results_data = {
            "tournament_id": self.tournament_id,
            "player1": self.player1.name,
            "player2": self.player2.name,
            "num_games": self.num_games,
            "timestamp": datetime.now().isoformat(),
            "games": [asdict(r) for r in self.results]
        }
        
        with open(json_file, "w") as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Tournament results saved to {json_file}")
        
        # Save summary as text
        summary_file = self.log_dir / f"tournament_{self.tournament_id}_summary.txt"
        stats = self._calculate_stats(sum(r.duration_seconds for r in self.results))
        
        with open(summary_file, "w") as f:
            f.write(f"Tournament Summary\n")
            f.write(f"==================\n")
            f.write(f"Tournament ID: {self.tournament_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(f"Players:\n")
            f.write(f"  Player 1: {self.player1.name}\n")
            f.write(f"  Player 2: {self.player2.name}\n\n")
            f.write(f"Results:\n")
            f.write(f"  {self.player1.name} wins: {stats.player1_wins}\n")
            f.write(f"  {self.player2.name} wins: {stats.player2_wins}\n")
            f.write(f"  Draws: {stats.draws}\n")
            f.write(f"  Total games: {stats.total_games}\n\n")
            f.write(f"Timing:\n")
            f.write(f"  Total duration: {stats.total_duration:.2f}s\n")
            f.write(f"  Avg game duration: {stats.avg_game_duration:.2f}s\n\n")
            f.write(f"Game Details:\n")
            f.write(f"{'Game':<6} {'Winner':<20} {'Loser':<20} {'Moves':<8} {'Duration':<12}\n")
            f.write(f"{'-'*66}\n")
            
            for result in self.results:
                winner = result.winner or "Draw"
                loser = result.loser or "-"
                duration_str = f"{result.duration_seconds:.2f}s"
                f.write(f"{result.game_id:<6} {winner:<20} {loser:<20} {result.move_count:<8} {duration_str:<12}\n")
        
        logger.info(f"Tournament summary saved to {summary_file}")
    
    def get_results(self) -> List[GameResult]:
        """Get all game results."""
        return self.results
    
    def print_summary(self):
        """Print tournament summary to console."""
        stats = self._calculate_stats(sum(r.duration_seconds for r in self.results))
        
        print("\n" + "="*60)
        print("TOURNAMENT SUMMARY")
        print("="*60)
        print(f"\nPlayers:")
        print(f"  {self.player1.name}")
        print(f"  {self.player2.name}")
        print(f"\nResults:")
        print(f"  {self.player1.name} wins: {stats.player1_wins}")
        print(f"  {self.player2.name} wins: {stats.player2_wins}")
        print(f"  Draws: {stats.draws}")
        print(f"\nTotal games: {stats.total_games}")
        print(f"Total duration: {stats.total_duration:.2f} seconds")
        print(f"Average game duration: {stats.avg_game_duration:.2f} seconds")
        print("="*60 + "\n")
