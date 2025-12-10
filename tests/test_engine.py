"""Unit tests for Breakthrough game engine."""

import unittest
from breakthrough.engine import Game, Player, Piece, Move, Board


class TestMove(unittest.TestCase):
    """Tests for Move class."""
    
    def test_move_notation_conversion(self):
        """Test converting moves to and from notation."""
        move = Move((6, 4), (5, 4))  # e2 to e3
        notation = move.to_notation()
        self.assertEqual(notation, "e2 to e3")
        
        # Parse it back
        parsed = Move.from_notation(notation)
        self.assertEqual(parsed.from_pos, (6, 4))
        self.assertEqual(parsed.to_pos, (5, 4))
    
    def test_move_notation_corners(self):
        """Test notation conversion at board corners."""
        # Top-left (a8)
        move = Move((0, 0), (1, 0))
        self.assertEqual(move.to_notation(), "a8 to a7")
        
        # Bottom-right (h1)
        move = Move((7, 7), (6, 7))
        self.assertEqual(move.to_notation(), "h1 to h2")
    
    def test_move_equality(self):
        """Test move equality."""
        move1 = Move((6, 4), (5, 4))
        move2 = Move((6, 4), (5, 4))
        move3 = Move((6, 4), (5, 5))
        
        self.assertEqual(move1, move2)
        self.assertNotEqual(move1, move3)
    
    def test_invalid_notation(self):
        """Test parsing invalid notation."""
        with self.assertRaises(ValueError):
            Move.from_notation("invalid")
        
        with self.assertRaises(ValueError):
            Move.from_notation("a1 a2")  # Missing "to"


class TestBoard(unittest.TestCase):
    """Tests for Board class."""
    
    def test_board_initialization(self):
        """Test that board is initialized correctly."""
        board = Board()
        
        # Check white pieces (rows 6-7)
        for row in [6, 7]:
            for col in range(8):
                piece = board.get_piece(row, col)
                self.assertIsNotNone(piece)
                self.assertEqual(piece.player, Player.WHITE)
        
        # Check black pieces (rows 0-1)
        for row in [0, 1]:
            for col in range(8):
                piece = board.get_piece(row, col)
                self.assertIsNotNone(piece)
                self.assertEqual(piece.player, Player.BLACK)
        
        # Check empty squares (rows 2-5)
        for row in range(2, 6):
            for col in range(8):
                piece = board.get_piece(row, col)
                self.assertIsNone(piece)
    
    def test_board_set_get_piece(self):
        """Test setting and getting pieces."""
        board = Board()
        piece = Piece(Player.WHITE)
        
        board.set_piece(4, 4, piece)
        retrieved = board.get_piece(4, 4)
        self.assertEqual(retrieved, piece)
    
    def test_board_invalid_positions(self):
        """Test that invalid positions return None."""
        board = Board()
        
        self.assertIsNone(board.get_piece(-1, 0))
        self.assertIsNone(board.get_piece(0, -1))
        self.assertIsNone(board.get_piece(8, 0))
        self.assertIsNone(board.get_piece(0, 8))
    
    def test_board_copy(self):
        """Test that board copies are independent."""
        board1 = Board()
        board2 = board1.copy()
        
        # Modify board2
        board2.set_piece(4, 4, Piece(Player.WHITE))
        
        # board1 should be unchanged
        self.assertIsNone(board1.get_piece(4, 4))


class TestGame(unittest.TestCase):
    """Tests for Game class."""
    
    def test_game_initialization(self):
        """Test game initialization."""
        game = Game()
        
        self.assertEqual(game.current_player, Player.WHITE)
        self.assertFalse(game.game_over)
        self.assertIsNone(game.winner)
        self.assertEqual(len(game.move_history), 0)
    
    def test_get_legal_moves_starting_position(self):
        """Test that starting position has correct number of legal moves."""
        game = Game()
        legal_moves = game.get_legal_moves()
        
        # Each of 8 white pawns can move forward (1 move) = 8 moves
        self.assertEqual(len(legal_moves), 8)
        
        # All should be forward (non-capture) moves
        for move in legal_moves:
            self.assertFalse(move.is_capture)
    
    def test_white_initial_moves(self):
        """Test that white can only move forward from starting position."""
        game = Game()
        legal_moves = game.get_legal_moves()
        
        # All moves should be from row 6 or 7 to row 5 or 6
        for move in legal_moves:
            self.assertIn(move.from_pos[0], [6, 7])
            self.assertIn(move.to_pos[0], [5, 6])
            # All should be in the same column (forward, not diagonal)
            self.assertEqual(move.from_pos[1], move.to_pos[1])
    
    def test_make_valid_move(self):
        """Test making a valid move."""
        game = Game()
        
        # White moves e2 to e3
        move = Move((6, 4), (5, 4))
        result = game.make_move(move)
        
        self.assertTrue(result)
        self.assertEqual(game.current_player, Player.BLACK)
        self.assertIsNotNone(game.board.get_piece(5, 4))
        self.assertIsNone(game.board.get_piece(6, 4))
    
    def test_make_invalid_move(self):
        """Test that invalid moves are rejected."""
        game = Game()
        
        # Try to move a black piece (not white's turn)
        move = Move((1, 4), (2, 4))
        result = game.make_move(move)
        
        self.assertFalse(result)
        self.assertEqual(game.current_player, Player.WHITE)  # Should stay white's turn
    
    def test_move_history(self):
        """Test that moves are tracked in history."""
        game = Game()
        
        move1 = Move((6, 4), (5, 4))
        move2 = Move((1, 4), (2, 4))
        
        game.make_move(move1)
        game.make_move(move2)
        
        self.assertEqual(len(game.move_history), 2)
        self.assertEqual(game.move_history[0], move1)
        self.assertEqual(game.move_history[1], move2)
    
    def test_capture_moves(self):
        """Test capture move generation."""
        game = Game()
        
        # Set up a capture scenario: white at (5,4), black at (4,3) and (4,5)
        game.board.set_piece(5, 4, Piece(Player.WHITE))
        game.board.set_piece(4, 3, Piece(Player.BLACK))
        game.board.set_piece(4, 5, Piece(Player.BLACK))
        game.board.set_piece(6, 4, None)  # Remove the piece from starting position
        game.board.set_piece(6, 3, None)
        game.board.set_piece(6, 5, None)
        
        # Set up the board to make it white's turn
        game.current_player = Player.WHITE
        
        legal_moves = game.get_legal_moves()
        
        # Should have moves to (4,3) and (4,5) as captures
        capture_moves = [m for m in legal_moves if m.is_capture]
        self.assertGreaterEqual(len(capture_moves), 2)
    
    def test_game_copy(self):
        """Test that game copies are independent."""
        game1 = Game()
        move = Move((6, 4), (5, 4))
        game1.make_move(move)
        
        game2 = game1.copy()
        
        # Make a move in game2
        move2 = Move((1, 4), (2, 4))
        game2.make_move(move2)
        
        # game1 should be unchanged
        self.assertEqual(len(game1.move_history), 1)
        self.assertEqual(len(game2.move_history), 2)


class TestWinCondition(unittest.TestCase):
    """Tests for win detection."""
    
    def test_white_wins_at_row_zero(self):
        """Test that white wins by reaching row 0."""
        game = Game()
        
        # Clear the board and set up white piece at row 1
        for row in range(8):
            for col in range(8):
                game.board.set_piece(row, col, None)
        
        game.board.set_piece(1, 4, Piece(Player.WHITE))
        game.current_player = Player.WHITE
        
        # Move to row 0 (winning position)
        move = Move((1, 4), (0, 4))
        game.make_move(move)
        
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, Player.WHITE)
    
    def test_black_wins_at_row_seven(self):
        """Test that black wins by reaching row 7."""
        game = Game()
        
        # Clear the board and set up black piece at row 6
        for row in range(8):
            for col in range(8):
                game.board.set_piece(row, col, None)
        
        game.board.set_piece(6, 4, Piece(Player.BLACK))
        game.current_player = Player.BLACK
        
        # Move to row 7 (winning position)
        move = Move((6, 4), (7, 4))
        game.make_move(move)
        
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, Player.BLACK)


class TestGameFlow(unittest.TestCase):
    """Tests for complete game flow."""
    
    def test_alternating_turns(self):
        """Test that players alternate turns."""
        game = Game()
        
        for i in range(4):
            if i % 2 == 0:
                self.assertEqual(game.current_player, Player.WHITE)
            else:
                self.assertEqual(game.current_player, Player.BLACK)
            
            legal_moves = game.get_legal_moves()
            if legal_moves:
                game.make_move(legal_moves[0])
    
    def test_simple_game_sequence(self):
        """Test a simple game sequence."""
        game = Game()
        
        # White moves e2 to e3
        move1 = Move((6, 4), (5, 4))
        self.assertTrue(game.make_move(move1))
        self.assertEqual(game.current_player, Player.BLACK)
        
        # Black moves e7 to e6
        move2 = Move((1, 4), (2, 4))
        self.assertTrue(game.make_move(move2))
        self.assertEqual(game.current_player, Player.WHITE)
        
        self.assertEqual(len(game.move_history), 2)


if __name__ == '__main__':
    unittest.main()
