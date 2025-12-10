"""Unit tests for LLM players and tournament system."""

import unittest
from unittest.mock import Mock, patch
from breakthrough.engine import Game, Player, Move
from breakthrough.llm_players import RandomPlayer, LLMPlayer
from breakthrough.tournament import Tournament, GameResult


class TestRandomPlayer(unittest.TestCase):
    """Tests for RandomPlayer."""
    
    def test_random_player_initialization(self):
        """Test random player initialization."""
        player = RandomPlayer("TestBot", Player.WHITE)
        
        self.assertEqual(player.name, "TestBot")
        self.assertEqual(player.player_color, Player.WHITE)
        self.assertEqual(player.move_count, 0)
    
    def test_random_player_gets_legal_move(self):
        """Test that random player returns a legal move."""
        player = RandomPlayer("TestBot", Player.WHITE)
        game = Game()
        
        move = player.get_move(game)
        
        # Check it's a legal move
        legal_moves = game.get_legal_moves()
        self.assertIn(move, legal_moves)
        
        # Check move count was incremented
        self.assertEqual(player.move_count, 1)
    
    def test_random_player_wrong_turn(self):
        """Test that player raises error when it's not their turn."""
        player = RandomPlayer("TestBot", Player.BLACK)
        game = Game()  # White's turn
        
        with self.assertRaises(ValueError):
            player.get_move(game)
    
    def test_random_player_move_count(self):
        """Test that move count is tracked correctly."""
        player = RandomPlayer("TestBot", Player.WHITE)
        game = Game()
        
        initial_count = player.move_count
        
        # Make multiple moves
        for _ in range(3):
            move = player.get_move(game)
            game.make_move(move)
            # Switch to white's turn for testing
            if game.current_player == Player.BLACK:
                game.current_player = Player.WHITE
        
        self.assertEqual(player.move_count, 3)


class TestTournament(unittest.TestCase):
    """Tests for Tournament class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player1 = RandomPlayer("Bot1", Player.WHITE)
        self.player2 = RandomPlayer("Bot2", Player.BLACK)
    
    def test_tournament_initialization(self):
        """Test tournament initialization."""
        tournament = Tournament(self.player1, self.player2, num_games=3)
        
        self.assertEqual(tournament.player1, self.player1)
        self.assertEqual(tournament.player2, self.player2)
        self.assertEqual(tournament.num_games, 3)
        self.assertEqual(len(tournament.results), 0)
    
    def test_single_game_tournament(self):
        """Test running a single game tournament."""
        tournament = Tournament(self.player1, self.player2, num_games=1)
        stats = tournament.run()
        
        self.assertEqual(stats.total_games, 1)
        self.assertEqual(len(tournament.results), 1)
        
        # Check that exactly one player won or it was a draw
        result = tournament.results[0]
        if result.is_draw:
            self.assertIsNone(result.winner)
        else:
            self.assertIsNotNone(result.winner)
            self.assertIn(result.winner, [self.player1.name, self.player2.name])
    
    def test_tournament_color_alternation(self):
        """Test that players alternate colors."""
        tournament = Tournament(self.player1, self.player2, num_games=2)
        tournament.run()
        
        # First game: player1 is WHITE, player2 is BLACK
        self.assertEqual(tournament.results[0].player1_name, self.player1.name)
        self.assertEqual(tournament.results[0].player2_name, self.player2.name)
        
        # Second game: player2 is WHITE, player1 is BLACK
        self.assertEqual(tournament.results[1].player1_name, self.player2.name)
        self.assertEqual(tournament.results[1].player2_name, self.player1.name)
    
    def test_tournament_stats_calculation(self):
        """Test tournament statistics calculation."""
        tournament = Tournament(self.player1, self.player2, num_games=3)
        stats = tournament.run()
        
        # Check that stats add up
        total_wins = stats.player1_wins + stats.player2_wins + stats.draws
        self.assertEqual(total_wins, stats.total_games)
        self.assertEqual(stats.total_games, 3)
    
    def test_game_result_structure(self):
        """Test that game results have all required fields."""
        tournament = Tournament(self.player1, self.player2, num_games=1)
        tournament.run()
        
        result = tournament.results[0]
        
        # Check all required fields are present
        self.assertIsNotNone(result.game_id)
        self.assertIsNotNone(result.player1_name)
        self.assertIsNotNone(result.player2_name)
        self.assertIsNotNone(result.timestamp)
        self.assertIsNotNone(result.duration_seconds)
        self.assertIsInstance(result.moves, list)
        self.assertGreaterEqual(result.move_count, 0)
    
    def test_tournament_multiple_games(self):
        """Test running multiple games."""
        tournament = Tournament(self.player1, self.player2, num_games=5)
        stats = tournament.run()
        
        self.assertEqual(stats.total_games, 5)
        self.assertEqual(len(tournament.results), 5)
        
        # All games should have results
        for result in tournament.results:
            if not result.is_draw:
                self.assertIsNotNone(result.winner)


class TestLLMPlayerInterface(unittest.TestCase):
    """Tests for LLMPlayer base class."""
    
    def test_llm_player_is_abstract(self):
        """Test that LLMPlayer cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            LLMPlayer("Test", Player.WHITE)
    
    def test_format_board_for_llm(self):
        """Test board formatting for LLM."""
        player = RandomPlayer("Test", Player.WHITE)
        game = Game()
        
        board_str = player._format_board_for_llm(game)
        
        self.assertIsInstance(board_str, str)
        self.assertIn("a b c d e f g h", board_str)  # Header row
    
    def test_get_available_moves(self):
        """Test getting available moves in notation format."""
        player = RandomPlayer("Test", Player.WHITE)
        game = Game()
        
        moves = player._get_available_moves(game)
        
        self.assertIsInstance(moves, list)
        self.assertGreater(len(moves), 0)
        
        # Check format is correct (e.g., "e2 to e3")
        for move_notation in moves:
            self.assertIn(" to ", move_notation)


if __name__ == '__main__':
    unittest.main()
