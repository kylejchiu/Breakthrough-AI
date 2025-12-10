# Breakthrough AI: LLM Tournament Simulator

A Python project to simulate games of **Breakthrough**, a 2-player strategy board game, between multiple Large Language Models (LLMs) using their APIs. Run tournaments, track statistics, and analyze LLM game-playing capabilities.

## Overview

Breakthrough is played on an 8×8 grid where each player starts with 16 pieces on their first two rows. Pieces move forward one square or capture diagonally. A piece that reaches the opponent's back row wins immediately. This project provides:

- **Complete game engine** with board management, move generation, and win detection
- **Modular LLM interface** supporting OpenAI, Anthropic, and custom implementations
- **Tournament system** for organizing multi-game matches with comprehensive logging and statistics
- **Comprehensive tests** covering game logic, move validation, and tournament mechanics
- **Secure API key management** using environment variables
- **Detailed game analysis** and results tracking

## Features

### Game Engine
- Full Breakthrough rules implementation
- Legal move generation (forward moves and diagonal captures)
- Board state management and history tracking
- Win/draw detection
- Move notation in standard format (e.g., "e2 to e3")

### LLM Integration
- Abstract `LLMPlayer` base class for extensibility
- **OpenAI** support (GPT-3.5, GPT-4, etc.)
- **Anthropic** support (Claude models)
- **Random player** for baseline testing
- Graceful fallback handling for API failures
- Configurable models per player

### Tournament System
- Multi-game tournaments with automatic color alternation
- Win/loss/draw tracking
- Move history and board state logging
- Game duration measurement
- JSON export of complete game records
- Summary statistics and analysis

### Testing
- 30+ unit tests covering game engine, moves, and tournaments
- Move validation tests
- Win condition tests
- LLM player tests
- Tournament flow tests

## Project Structure

```
breakthrough-ai/
├── breakthrough/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── engine.py          # Game engine (Board, Game, Move, Player classes)
│   ├── llm_players.py     # LLM player implementations
│   ├── tournament.py      # Tournament system
│   └── config.py          # Configuration and utilities
├── tests/                  # Unit tests
│   ├── test_engine.py     # Game engine tests
│   └── test_tournament.py # Tournament and LLM player tests
├── examples/              # Example scripts
│   ├── simple_game.py     # Simple game demo
│   └── tournament_example.py  # Tournament demo
├── logs/                  # Game logs and tournament summaries
├── data/                  # Game data (JSON format)
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository** (if applicable):
```bash
git clone https://github.com/kylejchiu/Breakthrough-AI.git
cd Breakthrough-AI
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure API keys**:

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
# OpenAI API key (for GPT-3.5, GPT-4, etc.)
OPENAI_API_KEY=sk-...

# Anthropic API key (for Claude models)
ANTHROPIC_API_KEY=sk-ant-...
```

**Never commit the `.env` file to version control!**

## Usage

### Quick Start: Simple Game

Run a game between two random players:
```bash
python examples/simple_game.py
```

### Run a Tournament

Using the CLI:

**5 games between random players:**
```bash
python main.py --games 5 --player1 random --player2 random
```

**3 games between OpenAI and Anthropic:**
```bash
python main.py --games 3 \
  --player1 openai --model1 gpt-4-turbo-preview \
  --player2 anthropic --model2 claude-3-5-sonnet-20241022 \
  --name1 "GPT-4" --name2 "Claude"
```

**Check available API keys:**
```bash
python main.py --check-apis
```

### CLI Options

```
optional arguments:
  -h, --help            show this help message and exit
  --games GAMES         Number of games to play (default: 1)
  --player1 PLAYER1     Type: random, openai, anthropic (default: random)
  --player2 PLAYER2     Type: random, openai, anthropic (default: random)
  --name1 NAME1         Custom name for player 1
  --name2 NAME2         Custom name for player 2
  --model1 MODEL1       Model for player 1 (if applicable)
  --model2 MODEL2       Model for player 2 (if applicable)
  --log-dir LOG_DIR     Directory for logs (default: ./logs)
  --data-dir DATA_DIR   Directory for data (default: ./data)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level (default: INFO)
  --check-apis          Check which API keys are configured
  --env-file ENV_FILE   Path to .env file (default: .env)
```

### Programmatic Usage

```python
from breakthrough.engine import Game, Player
from breakthrough.llm_players import OpenAIPlayer, RandomPlayer
from breakthrough.tournament import Tournament

# Create players
gpt4 = OpenAIPlayer("GPT-4", Player.WHITE, model="gpt-4-turbo-preview")
random_bot = RandomPlayer("RandomBot", Player.BLACK)

# Run a tournament
tournament = Tournament(gpt4, random_bot, num_games=3)
stats = tournament.run()

# Print results
tournament.print_summary()
```

## Game Rules

### Objective
Reach the opponent's back row with one of your pieces.

### Starting Position
- White pieces: Rows 6-7 (bottom)
- Black pieces: Rows 0-1 (top)

### Movement
- **Forward move**: One square directly forward to an empty square
- **Capture**: One square diagonally forward to capture an opponent's piece
- White moves up (decreasing row), Black moves down (increasing row)

### Winning
A piece that reaches the opponent's back row (row 0 for White, row 7 for Black) immediately wins the game.

### Draw
If a player has no legal moves on their turn, the game is a draw.

## Move Notation

Moves are represented in standard notation: `"column row to column row"`

Examples:
- `"e2 to e3"` - Move from e2 to e3
- `"d4 to c5"` - Diagonal capture from d4 to c5

Columns: a-h (left to right)
Rows: 1-8 (bottom to top for White, top to bottom for Black)

## Output and Logging

### Tournament Results
Tournament results are automatically saved to:

- **JSON format**: `data/tournament_YYYYMMDD_HHMMSS.json`
  - Complete game records
  - All moves and board states
  - Timing and player information

- **Text summary**: `logs/tournament_YYYYMMDD_HHMMSS_summary.txt`
  - Win/loss statistics
  - Game durations
  - Player performance

### Console Logging
Detailed logs are printed to the console and saved to `logs/breakthrough.log`

Example:
```
2024-12-08 15:30:45 - breakthrough - INFO - Starting tournament: 5 game(s)
2024-12-08 15:30:45 - breakthrough - INFO - Game 1/5: GPT-4 (WHITE) vs Claude (BLACK)
2024-12-08 15:31:22 - breakthrough - INFO - Game 1 ended in 37.45s after 47 moves
```

## Testing

Run all tests:
```bash
python -m pytest tests/
```

Run specific test file:
```bash
python -m pytest tests/test_engine.py -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=breakthrough --cov-report=html
```

Test coverage includes:
- Move notation and parsing
- Board initialization and manipulation
- Legal move generation
- Move execution and board updates
- Win/draw detection
- Game state tracking
- LLM player initialization and moves
- Tournament execution and statistics

## Extending the System

### Adding a New LLM Provider

Create a new player class inheriting from `LLMPlayer`:

```python
from breakthrough.llm_players import LLMPlayer
from breakthrough.engine import Game, Move, Player

class MistralPlayer(LLMPlayer):
    """Mistral API player implementation."""
    
    def __init__(self, name: str, player_color: Player, model: str = "mistral-7b"):
        super().__init__(name, player_color)
        self.model = model
        # Initialize Mistral client
    
    def get_move(self, game: Game) -> Move:
        """Get move from Mistral API."""
        legal_moves = self._get_available_moves(game)
        board_state = self._format_board_for_llm(game)
        
        # Call Mistral API
        # Parse response
        # Return Move object
        pass
```

Then use it:
```python
mistral_player = MistralPlayer("MistralBot", Player.WHITE)
```

### Custom Move Selection Strategies

You can modify the move selection in the LLM prompt to try different strategies:

```python
prompt = f"""...

Strategic considerations:
1. Prioritize reaching the opponent's back row
2. Protect your advancing pieces
3. Capture opponent pieces when advantageous
4. Maintain formation with other pieces

Choose the best move: {', '.join(legal_moves)}
"""
```

## API Documentation

### Board class
- `get_piece(row, col)`: Get piece at position
- `set_piece(row, col, piece)`: Place piece at position
- `copy()`: Create independent board copy
- `to_string()`: Get ASCII representation

### Game class
- `get_legal_moves()`: List all legal moves
- `make_move(move)`: Execute a move
- `get_board_state()`: Get board as string
- `copy()`: Create independent game state

### Move class
- `to_notation()`: Convert to "e2 to e3" format
- `from_notation(notation)`: Parse from string format

### Tournament class
- `run()`: Execute tournament
- `get_results()`: Get list of GameResult objects
- `print_summary()`: Print formatted results

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"
- Check that `.env` file exists in the project root
- Verify the key format is correct: `OPENAI_API_KEY=sk-...`
- Reload your shell: `source venv/bin/activate`

### "anthropic library not installed"
- Run: `pip install -r requirements.txt`

### API Rate Limits
- The system catches API errors and falls back to random moves
- Add delays between games for high-volume tournaments
- Check your API provider's rate limits

### Games Running Slowly
- Use `--log-level WARNING` to reduce logging overhead
- Reduce the number of games in the tournament
- Use simpler models (GPT-3.5 instead of GPT-4) for faster responses

## Performance Tips

1. **Batch tournaments**: Run multiple games to gather statistics
2. **Use appropriate models**: Faster models for more games, better models for quality analysis
3. **Monitor API usage**: Track costs with token counts
4. **Cache board states**: The system maintains full game history for analysis

## Limitations and Future Work

### Current Limitations
- Web-based UI not yet implemented
- Only supports 2-player games
- Limited to API-based LLMs

### Planned Features
- Web dashboard for tournament visualization
- Support for local/open-source LLMs
- Advanced evaluation metrics (piece counting, board control)
- Parallel game execution
- Interactive game replay viewer

## License

This project is provided as-is. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the test files for usage examples

## References

### Breakthrough Game
- [MindSports: Breakthrough](https://www.mindsports.net/games/abstract/breakthrough.html)
- [Wikipedia: Breakthrough (board game)](https://en.wikipedia.org/wiki/Breakthrough_(board_game))

### LLM APIs
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com)

---

**Last Updated**: December 2024
**Version**: 1.0.0
