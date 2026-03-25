# Chess Engine Master Plan and Constraints

This document is the canonical implementation reference for this project.
It captures the phase-wise roadmap, quality gates, constraints, and operating rules.

## 1) Project Goal
Build a working Python chess engine that:
- Plays legal and reasonably strong chess.
- Integrates with UCI GUIs (Arena/Cutechess).
- Is developed incrementally with tests and measurable progress.

Target profile:
- Not grandmaster-level.
- Strong enough to beat many casual players after iterative tuning.

## 2) Core Build Principles (Non-Negotiable)
1. Build in order: setup -> board/state -> eval -> search -> TT -> UCI -> tuning.
2. Test-first habit: every phase must add tests before complexity.
3. Measure everything: puzzle score, nodes/sec, depth reached, match results.
4. Keep engine deterministic where possible during testing.
5. Never break UCI stdout protocol with debug prints.

## 3) Global Technical Decisions
- Language: Python 3.10+
- Core chess library: python-chess
- Testing: pytest
- Editor: VS Code + Pylance
- Type hints: required for new code
- GUI for integration/testing: Arena (UCI), later Cutechess-cli for gauntlets

## 4) Repository Structure (Planned)
- engine/
  - __init__.py
  - main.py                  # terminal runner for early phases
  - board_utils.py           # FEN/state/move helpers
  - evaluate.py              # static evaluation
  - search.py                # negamax/alpha-beta/quiescence/iterative deepening
  - tt.py                    # transposition table implementation
  - uci.py                   # UCI protocol loop and command handling
  - time_manager.py          # simple clock logic
- tests/
  - test_basics.py
  - test_board_state.py
  - test_evaluation.py
  - test_search.py
  - test_uci_protocol.py
- tools/
  - run_puzzles.py
  - selfplay.py
  - benchmark.py
- requirements.txt
- README.md
- ENGINE_MASTER_PLAN.md      # this file

## 5) Phase-Wise Implementation Plan

### Phase 1: Setup and Tooling (Week 1)
Goal:
- Working environment, runnable board, initial tests.

Deliverables:
- requirements.txt: python-chess, pytest
- Minimal engine/main.py to print board
- Basic terminal move loop (human vs human)
- test_basics.py + legal move sanity test

Acceptance Criteria:
- Board renders from start position without errors.
- legal_moves iterable returns valid opening moves.
- pytest discovers and passes baseline tests.
- 5+ plies can be played in terminal loop.

Pitfalls to avoid:
- Starting engine logic before tests.
- Mixing package managers in one workflow.

---

### Phase 2: Board Representation and State Mastery (Week 1-2)
Goal:
- Full confidence in board state transitions and FEN operations.

Deliverables:
- FEN load/print utility.
- Move inspector (from/to, capture, promotion, castle, en passant).
- State checker utility (check/checkmate/stalemate/draw status).
- Push/pop roundtrip tests.

Acceptance Criteria:
- Known FEN positions load correctly.
- Piece counts match expected values.
- push+pop restores exact board state.
- checkmate and draw detection pass known cases.

Critical constraints:
- board.push() mutates in-place; always board.pop() in search paths.
- Use legal moves (not pseudo-legal) for correctness.

---

### Phase 3: Evaluation Function v1 (Week 2-4)
Goal:
- Score positions in centipawns with meaningful outputs.

Deliverables:
- Material evaluation.
- PSQT for all piece types.
- Optional tapered eval (opening/endgame blend).
- Lightweight mobility bonus.
- Single evaluate(board) -> int API.

Default piece values (cp):
- Pawn 100, Knight 320, Bishop 330, Rook 500, Queen 900

Acceptance Criteria:
- Start position near 0.
- Winning a free queen shifts score around +900/-900.
- Centralization effects visible via PSQT.
- Color-flipped positions negate score as expected.

Pitfalls to avoid:
- Not mirroring PSQT for black.
- Overcomplicated eval before search is stable.

---

### Phase 4: Search Core (Week 4-7)
Goal:
- Engine picks moves by lookahead with alpha-beta pruning.

Build order:
1. Plain minimax/negamax baseline.
2. Alpha-beta pruning.
3. Move ordering (captures first; MVV-LVA).
4. Quiescence search (captures-only initially).
5. Iterative deepening.
6. Simple fixed movetime control (e.g., 2 seconds).

Acceptance Criteria:
- Finds mate in one in known tactical positions.
- Avoids obvious blunders at shallow depth.
- Alpha-beta searches significantly fewer nodes than plain minimax.
- Quiescence reduces horizon tactical errors.

Pitfalls to avoid:
- Forgetting to pop moves after recursive search.
- Score sign mistakes in negamax recursion.
- Infinite/unstable quiescence.

---

### Phase 5: Transposition Table (Week 7-8)
Goal:
- Reuse computed search results via hash-based cache.

Deliverables:
- TTEntry dataclass with score, depth, flag, best_move.
- Key from board._transposition_key().
- Probe/store integrated in search.
- Bounded cache and replacement policy.

Flags:
- EXACT, LOWERBOUND, UPPERBOUND

Acceptance Criteria:
- Repeated transpositions produce TT hits.
- Same depth/time explores fewer nodes than no-TT version.
- Stable long-run behavior without key or state errors.

Pitfalls to avoid:
- Using FEN string as hash key (slow).
- Misusing bound flags (can corrupt search correctness).

---

### Phase 6: UCI Protocol and GUI Integration (Week 8-9)
Goal:
- Engine works as a standard UCI engine in Arena/Cutechess.

Deliverables:
- UCI command loop handling:
  - uci, isready, ucinewgame, quit
  - position startpos moves ...
  - position fen ... moves ...
  - go (movetime, wtime/btime, infinite)
  - stop
- Search threading with safe stop signal.
- info lines during search.
- setoption support (at minimum Hash).

Acceptance Criteria:
- uci -> uciok and isready -> readyok.
- GUI loads engine and games run without protocol errors.
- No illegal moves generated.
- Infinite analysis mode works with stop.

Critical constraint:
- Do not print non-UCI debug content to stdout.

---

### Phase 7: Testing, Tuning, Iteration (Week 9-14)
Goal:
- Improve practical playing strength through controlled experiments.

Deliverables:
- Puzzle runner (initially 100-200 tactical positions).
- Self-play harness (vN vs vN+1).
- Match automation for Elo trend estimation.
- Heuristics: killer/history moves; null move pruning with safeguards.

Acceptance Criteria:
- Puzzle pass-rate trend improves over versions.
- New version wins meaningfully vs baseline in A/B matches.
- Stable in long gauntlets (no crashes/illegal moves).

Pitfalls to avoid:
- Evaluating only on puzzles.
- Tuning without fixed baseline.
- Unsafe NMP in zugzwang-prone endings.

## 6) Definition of Done Per Phase
A phase is done only when all are true:
1. Feature implementation complete.
2. Tests added and passing.
3. Verification checklist passed.
4. Regression check against previous baseline done.
5. Notes updated with decisions and metrics.

## 7) Metrics to Track Every Milestone
- Depth reached in fixed time.
- Nodes searched and nodes/second.
- Puzzle solve rate (%).
- Match score vs previous version.
- Crash count / illegal move count.

## 8) Coding and Quality Constraints
- Use type hints in all new modules/functions.
- Keep modules focused and small.
- Avoid global mutable state unless necessary.
- Keep side effects out of eval/search pure logic where possible.
- Add targeted tests for each bug fix to prevent regressions.

## 9) UCI and Runtime Safety Rules
- Engine core should not write protocol text directly except via UCI layer.
- Flush stdout after each UCI response line.
- Use file-based logging for debug output (not stdout).
- Handle stop/quit cleanly and promptly.

## 10) Practical Timeline Guidance
- Part-time weekends: roughly 10-14 weeks.
- Consistent evenings: roughly 4-6 weeks.

Suggested checkpoint outcomes:
- End of Phase 2: robust board/state correctness.
- End of Phase 4: tactically functional engine.
- End of Phase 5: major speed/strength jump.
- End of Phase 6: full GUI compatibility.
- End of Phase 7: stable, decent-strength personal engine.

## 11) Next Immediate Action
Start Phase 1 implementation:
1. Create repository skeleton.
2. Add requirements and starter engine/main.py.
3. Add baseline pytest tests.
4. Run tests and verify first playable terminal loop.
