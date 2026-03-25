# Chess Engine (Phase 1-5)

Minimal starter project for building a Python chess engine incrementally.

Current status:
- Phase 1 complete: setup, terminal loop, baseline tests.
- Phase 2 started: board/FEN/state utilities and tests.
- Phase 3 v3: material + tapered PSQT + lightweight mobility with tests.
- Phase 4 complete baseline: alpha-beta, quiescence, iterative deepening, time budgeting.
- Phase 5 started: transposition table (TT) integrated into alpha-beta.

## Setup

1. Create/activate your virtual environment.
2. Install dependencies:

   c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe -m pip install -r requirements.txt

## Run Terminal Game Loop

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe -m engine.main

Moves must be entered in UCI format, for example:
- e2e4
- g8f6
- e7e8q (promotion)

Type q to quit.

## Run Tests

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe -m pytest -q

## Board Utilities (Phase 2)

Key helpers are in engine/board_utils.py:
- FEN loader with validation
- Pretty board rendering with coordinates
- Move inspection helpers (capture/castle/en-passant/promotion/check)
- Game-state summary helper

Command-line board inspector is in tools/board_cli.py.

Examples:

1. Start position overview:

   c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/board_cli.py --startpos

2. Start position + moves + legal move sample:

   c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/board_cli.py --startpos --moves e2e4 e7e5 --show-legal --max-legal 10

3. Load a custom FEN:

   c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/board_cli.py --fen "7k/8/8/8/8/6k1/6q1/7K w - - 0 1" --show-legal

4. List available named presets:

   c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/board_cli.py --list-presets

5. Load a named preset and inspect legal moves:

   c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/board_cli.py --preset fools_mate --show-legal

## Evaluation (Phase 3)

Evaluator is in engine/evaluate.py.

Current behavior:
- Returns centipawns from White perspective
- Piece values: P=100, N=320, B=330, R=500, Q=900, K=0
- Positive score means White is better; negative means Black is better
- Includes tapered PSQT positional bonus with mirrored scoring for Black pieces
- Uses game phase blending (opening -> endgame)
- Adds a lightweight mobility term (legal moves difference)

Quick evaluator example:

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe -c "import chess; from engine.evaluate import evaluate; print(evaluate(chess.Board('7k/8/8/8/4N3/8/8/7K w - - 0 1')))"

## Search (Phase 4-5)

Baseline search is in engine/search.py.

Current behavior:
- Fixed-depth negamax (baseline)
- Alpha-beta pruning variant for the same search model
- Basic move ordering in alpha-beta (captures first)
- Quiescence search at alpha-beta leaf nodes (captures-only)
- Iterative deepening with a simple time budget
- Simple clock-aware wrapper for movetime or wtime/btime allocation
- Transposition table probe/store with EXACT/LOWER/UPPER bounds
- TT best-move reuse for move ordering
- Mate scoring support in terminal nodes
- Helper: find_best_move(board, depth)
- Helper: find_best_move_alpha_beta(board, depth)
- Helper: iterative_deepening_search(board, max_depth, time_budget_sec)
- Helper: search_with_time_controls(...)

Benchmark node counts:

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/search_benchmark.py --depth 3

Benchmark TT impact:

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe tools/search_benchmark.py --depth 4 --tt --tt-size 100000

Quick iterative deepening example:

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe -c "import chess; from engine.search import iterative_deepening_search; r = iterative_deepening_search(chess.Board(), max_depth=4, time_budget_sec=0.2); print(r)"

Quick clock-aware example:

c:/Users/onlys/Desktop/chess-engine/.venv/Scripts/python.exe -c "import chess; from engine.search import search_with_time_controls; r = search_with_time_controls(chess.Board(), max_depth=5, movetime_ms=200); print(r.best_move, r.depth_reached, r.time_spent_sec)"
