# Chess Engine

Python chess engine project built incrementally from core board handling to UCI integration and tuning workflows.

## Project Scope

This project is a basic, fast-built engine implementation, not a deeply trained system.

- Built as a practical engineering exercise in roughly 3-4 hours of focused implementation.
- No reinforcement learning, no neural-network training, and no large-scale training pipeline.
- Goal was to improve from a low baseline and reach a stronger practical rating through classic search/evaluation improvements.

## Features

- UCI engine loop with `go movetime`, `go depth`, `go wtime/btime`, `go infinite`, and `stop`
- Search stack: negamax, alpha-beta, quiescence, iterative deepening, transposition table
- Heuristics: capture ordering, killer/history moves, guarded null-move pruning
- Tooling for benchmarking and phase-7 iteration:
  - puzzle runner
  - self-play harness
  - PGN match quality report (illegal move tracking)

## Repository Layout

- `engine/`: engine core (evaluation, search, TT, UCI)
- `tools/`: utilities for smoke tests, puzzles, self-play, and reporting
- `tests/`: pytest suite

## Quick Start (Windows)

1. Create virtual environment:

```powershell
python -m venv .venv
```

2. Activate environment:

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Run tests:

```powershell
python -m pytest -q
```

## Run the Engine

Run UCI loop directly:

```powershell
python -m engine.uci
```

Or run launcher:

```powershell
python engine.py
```

Run UCI smoke check:

```powershell
python tools/uci_smoke.py
```

## Benchmark and Tuning Tools

Search benchmark:

```powershell
python tools/search_benchmark.py --depth 4 --tt --tt-size 100000
```

Puzzle suite:

```powershell
python tools/run_puzzles.py --depth 2 --show-failures
```

Self-play harness:

```powershell
python tools/selfplay.py --games 20 --white-depth 3 --black-depth 4 --white-movetime 80 --black-movetime 80 --pgnout selfplay_vN_vs_vN1.pgn
```

Match quality report from PGN:

```powershell
python tools/match_report.py --pgn "elo_200_fast_1400_rerun.pgn"
```

## Git and Artifact Policy

Do not commit generated experiment outputs or downloaded binaries.

Do not commit:

- `*.pgn`, `ordo_*.txt`, `ordo_*.csv`
- local engine binaries like `stockfish-*.exe`, `cutechess-cli.exe`
- local virtual environment and caches

These are already ignored in `.gitignore`.

Recommended workflow:

1. Keep source code, tests, and docs in Git.
2. Keep Elo/Ordo/PGN outputs as local experiment artifacts.
3. If needed, publish large datasets/results in releases or external storage, and link from README.

## Notes

- For protocol safety, engine debug output should not go to stdout; use log files.
