"""Breakthrough game engine implementation."""

from enum import Enum
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import copy


class Player(Enum):
    """Represents the two players in Breakthrough."""
    WHITE = 1
    BLACK = 2


class Piece:
    """Represents a single piece on the board."""
    
    def __init__(self, player: Player):
        self.player = player
    
    def __repr__(self):
        return f"{'W' if self.player == Player.WHITE else 'B'}"
    
    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.player == other.player
    
    def __hash__(self):
        return hash(self.player)


@dataclass
class Move:
    """Represents a move in the game."""
    from_pos: Tuple[int, int]  # (row, col)
    to_pos: Tuple[int, int]     # (row, col)
    is_capture: bool = False
    
    def to_notation(self) -> str:
        """Convert move to standard notation (e.g., 'e2 to e3')."""
        def pos_to_notation(pos: Tuple[int, int]) -> str:
            col = chr(ord('a') + pos[1])
            row = str(8 - pos[0])
            return f"{col}{row}"
        
        from_notation = pos_to_notation(self.from_pos)
        to_notation = pos_to_notation(self.to_pos)
        return f"{from_notation} to {to_notation}"
    
    @staticmethod
    def from_notation(notation: str) -> 'Move':
        """Parse a move from standard notation (e.g., 'e2 to e3')."""
        try:
            parts = notation.split(" to ")
            if len(parts) != 2:
                raise ValueError(f"Invalid notation format: {notation}")
            
            from_str, to_str = parts
            
            def notation_to_pos(n: str) -> Tuple[int, int]:
                col = ord(n[0]) - ord('a')
                row = 8 - int(n[1])
                return (row, col)
            
            from_pos = notation_to_pos(from_str)
            to_pos = notation_to_pos(to_str)
            
            return Move(from_pos, to_pos)
        except Exception as e:
            raise ValueError(f"Failed to parse move notation '{notation}': {e}")
    
    def __repr__(self):
        return self.to_notation()
    
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.from_pos == other.from_pos and self.to_pos == other.to_pos
    
    def __hash__(self):
        return hash((self.from_pos, self.to_pos))


class Board:
    """Represents the Breakthrough game board."""
    
    BOARD_SIZE = 8
    
    def __init__(self):
        """Initialize the board with starting positions."""
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self._init_board()
    
    def _init_board(self):
        """Set up starting positions for both players."""
        # White pieces at the bottom (rows 6-7)
        for row in [6, 7]:
            for col in range(self.BOARD_SIZE):
                self.grid[row][col] = Piece(Player.WHITE)
        
        # Black pieces at the top (rows 0-1)
        for row in [0, 1]:
            for col in range(self.BOARD_SIZE):
                self.grid[row][col] = Piece(Player.BLACK)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get the piece at the given position."""
        if not self._is_valid_position(row, col):
            return None
        return self.grid[row][col]
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set a piece at the given position."""
        if self._is_valid_position(row, col):
            self.grid[row][col] = piece
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within the board."""
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board.__new__(Board)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board
    
    def to_string(self) -> str:
        """Convert board to a string representation."""
        lines = []
        lines.append("  a b c d e f g h")
        lines.append("  +-+-+-+-+-+-+-+-+")
        
        for row in range(self.BOARD_SIZE):
            row_str = f"{8 - row}|"
            for col in range(self.BOARD_SIZE):
                piece = self.grid[row][col]
                if piece is None:
                    row_str += " |"
                else:
                    row_str += f"{piece}|"
            row_str += f"{8 - row}"
            lines.append(row_str)
            lines.append("  +-+-+-+-+-+-+-+-+")
        
        lines.append("  a b c d e f g h")
        return "\n".join(lines)
    
    def __repr__(self):
        return self.to_string()


class Game:
    """Represents a game of Breakthrough."""
    
    def __init__(self):
        """Initialize a new game."""
        self.board = Board()
        self.current_player = Player.WHITE
        self.move_history: List[Move] = []
        self.winner: Optional[Player] = None
        self.game_over = False
    
    def get_legal_moves(self) -> List[Move]:
        """Generate all legal moves for the current player."""
        moves = []
        
        for row in range(Board.BOARD_SIZE):
            for col in range(Board.BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece is None or piece.player != self.current_player:
                    continue
                
                moves.extend(self._get_piece_moves(row, col))
        
        return moves
    
    def _get_piece_moves(self, row: int, col: int) -> List[Move]:
        """Get all legal moves for a specific piece."""
        piece = self.board.get_piece(row, col)
        if piece is None:
            return []
        
        moves = []
        
        # Determine direction based on player
        if piece.player == Player.WHITE:
            direction = -1  # Moving up (decreasing row)
            forward_row = row - 1
        else:  # Player.BLACK
            direction = 1   # Moving down (increasing row)
            forward_row = row + 1
        
        # Check forward move (non-capture)
        if 0 <= forward_row < Board.BOARD_SIZE:
            if self.board.get_piece(forward_row, col) is None:
                moves.append(Move((row, col), (forward_row, col), is_capture=False))
        
        # Check diagonal captures
        for col_offset in [-1, 1]:
            capture_col = col + col_offset
            if 0 <= forward_row < Board.BOARD_SIZE and 0 <= capture_col < Board.BOARD_SIZE:
                target_piece = self.board.get_piece(forward_row, capture_col)
                if target_piece is not None and target_piece.player != piece.player:
                    moves.append(Move((row, col), (forward_row, capture_col), is_capture=True))
        
        return moves
    
    def make_move(self, move: Move) -> bool:
        """Execute a move and update game state. Returns True if successful."""
        if not self._is_legal_move(move):
            return False
        
        # Execute the move
        piece = self.board.get_piece(move.from_pos[0], move.from_pos[1])
        self.board.set_piece(move.from_pos[0], move.from_pos[1], None)
        self.board.set_piece(move.to_pos[0], move.to_pos[1], piece)
        
        # Add to history
        self.move_history.append(move)
        
        # Check for win
        if self._check_win(piece, move.to_pos):
            self.winner = piece.player
            self.game_over = True
        
        # Switch player
        self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE
        
        # Check for draw (no legal moves) only if the game isn't already over
        if not self.game_over and not self.get_legal_moves():
            self.game_over = True
            self.winner = None  # Draw
        
        return True
    
    def _is_legal_move(self, move: Move) -> bool:
        """Check if a move is legal."""
        legal_moves = self.get_legal_moves()
        return move in legal_moves
    
    def _check_win(self, piece: Piece, position: Tuple[int, int]) -> bool:
        """Check if the piece reached the opponent's back row."""
        if piece.player == Player.WHITE:
            return position[0] == 0  # White wins by reaching row 0
        else:  # Player.BLACK
            return position[0] == 7  # Black wins by reaching row 7
    
    def get_board_state(self) -> str:
        """Get the current board state as a string."""
        return self.board.to_string()
    
    def get_game_status(self) -> str:
        """Get a human-readable game status."""
        if self.game_over:
            if self.winner:
                return f"Game Over. {self.winner.name} wins!"
            else:
                return "Game Over. Draw!"
        else:
            return f"Current player: {self.current_player.name}"
    
    def copy(self) -> 'Game':
        """Create a deep copy of the game state."""
        new_game = Game.__new__(Game)
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.move_history = self.move_history.copy()
        new_game.winner = self.winner
        new_game.game_over = self.game_over
        return new_game
    
    def __repr__(self):
        return f"{self.get_board_state()}\n\n{self.get_game_status()}"
