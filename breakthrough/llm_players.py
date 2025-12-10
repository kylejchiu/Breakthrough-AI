"""LLM player implementations for Breakthrough."""

import os
from abc import ABC, abstractmethod
from typing import Optional, List
import json
import logging

from .engine import Game, Move, Player


logger = logging.getLogger(__name__)


class LLMPlayer(ABC):
    """Abstract base class for LLM-based players."""
    
    def __init__(self, name: str, player_color: Player):
        """
        Initialize an LLM player.
        
        Args:
            name: Name of the player/LLM
            player_color: Which color this player controls (WHITE or BLACK)
        """
        self.name = name
        self.player_color = player_color
        self.move_count = 0
    
    @abstractmethod
    def get_move(self, game: Game) -> Move:
        """
        Get the next move from the LLM.
        
        Args:
            game: Current game state
            
        Returns:
            A Move object representing the LLM's choice
        """
        pass
    
    def _format_board_for_llm(self, game: Game) -> str:
        """Format the game board for LLM consumption."""
        return game.get_board_state()
    
    def _get_available_moves(self, game: Game) -> List[str]:
        """Get all legal moves in notation format."""
        return [move.to_notation() for move in game.get_legal_moves()]
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.player_color.name})"


class OpenAIPlayer(LLMPlayer):
    """LLM player using OpenAI's API."""
    
    def __init__(self, name: str, player_color: Player, model: str = "gpt-4-turbo-preview"):
        """
        Initialize an OpenAI-based player.
        
        Args:
            name: Name of the player
            player_color: Which color this player controls
            model: OpenAI model to use
        """
        super().__init__(name, player_color)
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai library not installed. Install with: pip install openai")
    
    def get_move(self, game: Game) -> Move:
        """Get next move from OpenAI API."""
        if game.current_player != self.player_color:
            raise ValueError(f"Not {self.name}'s turn")
        
        legal_moves = self._get_available_moves(game)
        board_state = self._format_board_for_llm(game)
        
        prompt = f"""You are playing Breakthrough, a strategy board game on an 8x8 board.

Current board state:
{board_state}

You are playing as {self.player_color.name}. Your pieces move forward or diagonally forward to capture.
Reach the opponent's back row to win.

Available legal moves: {', '.join(legal_moves)}

Please respond with ONLY the move in the format "column_row to column_row" (e.g., "e2 to e3").
Choose the best move strategically."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic Breakthrough player. Respond with only the move notation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=50
            )
            
            move_text = response.choices[0].message.content.strip()
            move = self._parse_move_response(move_text, legal_moves)
            self.move_count += 1
            logger.info(f"{self.name} made move: {move}")
            return move
            
        except Exception as e:
            logger.error(f"Error getting move from {self.name}: {e}")
            # Fallback to first legal move
            if legal_moves:
                return Move.from_notation(legal_moves[0])
            raise
    
    def _parse_move_response(self, response: str, legal_moves: List[str]) -> Move:
        """Parse the LLM's response to extract a move."""
        response = response.strip().lower()
        
        # Try to extract notation like "e2 to e3"
        if " to " in response:
            try:
                move = Move.from_notation(response)
                move_notation = move.to_notation().lower()
                if move_notation in [m.lower() for m in legal_moves]:
                    return move
            except:
                pass
        
        # Fallback to first legal move if parsing fails
        logger.warning(f"Could not parse move '{response}', using first legal move")
        return Move.from_notation(legal_moves[0])


class AnthropicPlayer(LLMPlayer):
    """LLM player using Anthropic's API."""
    
    def __init__(self, name: str, player_color: Player, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize an Anthropic-based player.
        
        Args:
            name: Name of the player
            player_color: Which color this player controls
            model: Anthropic model to use
        """
        super().__init__(name, player_color)
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic library not installed. Install with: pip install anthropic")
    
    def get_move(self, game: Game) -> Move:
        """Get next move from Anthropic API."""
        if game.current_player != self.player_color:
            raise ValueError(f"Not {self.name}'s turn")
        
        legal_moves = self._get_available_moves(game)
        board_state = self._format_board_for_llm(game)
        
        prompt = f"""You are playing Breakthrough, a strategy board game on an 8x8 board.

Current board state:
{board_state}

You are playing as {self.player_color.name}. Your pieces move forward or diagonally forward to capture.
Reach the opponent's back row to win.

Available legal moves: {', '.join(legal_moves)}

Please respond with ONLY the move in the format "column_row to column_row" (e.g., "e2 to e3").
Choose the best move strategically."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            move_text = response.content[0].text.strip()
            move = self._parse_move_response(move_text, legal_moves)
            self.move_count += 1
            logger.info(f"{self.name} made move: {move}")
            return move
            
        except Exception as e:
            logger.error(f"Error getting move from {self.name}: {e}")
            # Fallback to first legal move
            if legal_moves:
                return Move.from_notation(legal_moves[0])
            raise
    
    def _parse_move_response(self, response: str, legal_moves: List[str]) -> Move:
        """Parse the LLM's response to extract a move."""
        response = response.strip().lower()
        
        # Try to extract notation like "e2 to e3"
        if " to " in response:
            try:
                move = Move.from_notation(response)
                move_notation = move.to_notation().lower()
                if move_notation in [m.lower() for m in legal_moves]:
                    return move
            except:
                pass
        
        # Fallback to first legal move if parsing fails
        logger.warning(f"Could not parse move '{response}', using first legal move")
        return Move.from_notation(legal_moves[0])


class RandomPlayer(LLMPlayer):
    """Random player for testing (doesn't require API key)."""
    
    def __init__(self, name: str, player_color: Player):
        """
        Initialize a random player.
        
        Args:
            name: Name of the player
            player_color: Which color this player controls
        """
        super().__init__(name, player_color)
    
    def get_move(self, game: Game) -> Move:
        """Get a random legal move."""
        if game.current_player != self.player_color:
            raise ValueError(f"Not {self.name}'s turn")
        
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        import random
        move = random.choice(legal_moves)
        self.move_count += 1
        logger.info(f"{self.name} made move: {move}")
        return move
