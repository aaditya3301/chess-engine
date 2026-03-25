from __future__ import annotations

from dataclasses import dataclass
import time

import chess

from engine.evaluate import PIECE_VALUES, evaluate
from engine.time_manager import allocate_time_seconds

INF = 10**9
MATE_SCORE = 100_000
DRAW_SCORE = 0


@dataclass(frozen=True)
class SearchRunStats:
    """Search output and visited node count for a fixed-depth run."""

    best_move: chess.Move | None
    score: int
    nodes: int


@dataclass(frozen=True)
class IterativeDeepeningResult:
    """Outcome for iterative deepening under a time budget."""

    best_move: chess.Move | None
    score: int
    depth_reached: int
    nodes: int
    timed_out: bool
    time_spent_sec: float


class SearchTimeout(Exception):
    """Raised when search exceeds its deadline."""


def _check_deadline(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() >= deadline:
        raise SearchTimeout


def _evaluate_for_side_to_move(board: chess.Board) -> int:
    """Convert white-perspective eval to side-to-move perspective."""
    white_pov = evaluate(board)
    return white_pov if board.turn == chess.WHITE else -white_pov


def _terminal_score(board: chess.Board, ply: int) -> int:
    """Return a terminal node score from side-to-move perspective."""
    if board.is_checkmate():
        # Side to move is checkmated, so this is losing.
        return -MATE_SCORE + ply

    if board.is_game_over(claim_draw=True):
        return DRAW_SCORE

    return _evaluate_for_side_to_move(board)


def _ordered_legal_moves(board: chess.Board) -> list[chess.Move]:
    """Return legal moves ordered with captures first for better pruning."""
    return sorted(
        list(board.legal_moves),
        key=lambda move: (0 if board.is_capture(move) else 1, move.uci()),
    )


def _mvv_lva_score(board: chess.Board, move: chess.Move) -> int:
    """Return MVV-LVA score (higher is better for ordering captures)."""
    victim = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)
    victim_value = PIECE_VALUES.get(victim.piece_type, 0) if victim else 0
    attacker_value = PIECE_VALUES.get(attacker.piece_type, 0) if attacker else 0
    return victim_value * 10 - attacker_value


def _ordered_capture_moves(board: chess.Board) -> list[chess.Move]:
    """Return legal captures ordered by MVV-LVA."""
    captures = [move for move in board.legal_moves if board.is_capture(move)]
    return sorted(captures, key=lambda move: (-_mvv_lva_score(board, move), move.uci()))


def quiescence(
    board: chess.Board,
    alpha: int,
    beta: int,
    ply: int = 0,
    deadline: float | None = None,
) -> int:
    """Capture-only quiescence search with stand-pat evaluation."""
    _check_deadline(deadline)

    if board.is_checkmate():
        return -MATE_SCORE + ply

    if board.is_game_over(claim_draw=True):
        return DRAW_SCORE

    stand_pat = _evaluate_for_side_to_move(board)
    if stand_pat >= beta:
        return beta

    if stand_pat > alpha:
        alpha = stand_pat

    for move in _ordered_capture_moves(board):
        board.push(move)
        score = -quiescence(board, -beta, -alpha, ply + 1, deadline)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def negamax(board: chess.Board, depth: int, ply: int = 0) -> int:
    """Baseline negamax search without alpha-beta pruning."""
    if depth < 0:
        raise ValueError("depth must be >= 0")

    if depth == 0 or board.is_game_over(claim_draw=True):
        return _terminal_score(board, ply)

    best_score = -INF

    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth - 1, ply + 1)
        board.pop()

        if score > best_score:
            best_score = score

    return best_score


def _negamax_counted(
    board: chess.Board,
    depth: int,
    ply: int,
    node_counter: dict[str, int],
) -> int:
    node_counter["nodes"] += 1

    if depth == 0 or board.is_game_over(claim_draw=True):
        return _terminal_score(board, ply)

    best_score = -INF
    for move in board.legal_moves:
        board.push(move)
        score = -_negamax_counted(board, depth - 1, ply + 1, node_counter)
        board.pop()
        if score > best_score:
            best_score = score

    return best_score


def _quiescence_counted(
    board: chess.Board,
    alpha: int,
    beta: int,
    ply: int,
    node_counter: dict[str, int],
    deadline: float | None = None,
) -> int:
    node_counter["nodes"] += 1
    _check_deadline(deadline)

    if board.is_checkmate():
        return -MATE_SCORE + ply

    if board.is_game_over(claim_draw=True):
        return DRAW_SCORE

    stand_pat = _evaluate_for_side_to_move(board)
    if stand_pat >= beta:
        return beta

    if stand_pat > alpha:
        alpha = stand_pat

    for move in _ordered_capture_moves(board):
        board.push(move)
        score = -_quiescence_counted(board, -beta, -alpha, ply + 1, node_counter, deadline)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def negamax_alpha_beta(
    board: chess.Board,
    depth: int,
    alpha: int,
    beta: int,
    ply: int = 0,
    deadline: float | None = None,
) -> int:
    """Negamax search with alpha-beta pruning."""
    if depth < 0:
        raise ValueError("depth must be >= 0")

    _check_deadline(deadline)

    if board.is_game_over(claim_draw=True):
        return _terminal_score(board, ply)

    if depth == 0:
        return quiescence(board, alpha, beta, ply, deadline)

    best_score = -INF

    for move in _ordered_legal_moves(board):
        board.push(move)
        score = -negamax_alpha_beta(board, depth - 1, -beta, -alpha, ply + 1, deadline)
        board.pop()

        if score > best_score:
            best_score = score

        if score > alpha:
            alpha = score

        if alpha >= beta:
            break

    return best_score


def _negamax_alpha_beta_counted(
    board: chess.Board,
    depth: int,
    alpha: int,
    beta: int,
    ply: int,
    node_counter: dict[str, int],
    deadline: float | None = None,
) -> int:
    node_counter["nodes"] += 1
    _check_deadline(deadline)

    if board.is_game_over(claim_draw=True):
        return _terminal_score(board, ply)

    if depth == 0:
        return _quiescence_counted(board, alpha, beta, ply, node_counter, deadline)

    best_score = -INF
    for move in _ordered_legal_moves(board):
        board.push(move)
        score = -_negamax_alpha_beta_counted(
            board,
            depth - 1,
            -beta,
            -alpha,
            ply + 1,
            node_counter,
            deadline,
        )
        board.pop()

        if score > best_score:
            best_score = score

        if score > alpha:
            alpha = score

        if alpha >= beta:
            break

    return best_score


def find_best_move(board: chess.Board, depth: int) -> chess.Move | None:
    """Return best move found by baseline negamax at fixed depth."""
    if depth < 1:
        raise ValueError("depth must be >= 1")

    best_move: chess.Move | None = None
    best_score = -INF

    for move in board.legal_moves:
        board.push(move)
        score = -negamax(board, depth - 1, ply=1)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def find_best_move_alpha_beta(
    board: chess.Board,
    depth: int,
    deadline: float | None = None,
) -> chess.Move | None:
    """Return best move found by alpha-beta negamax at fixed depth."""
    if depth < 1:
        raise ValueError("depth must be >= 1")

    best_move: chess.Move | None = None
    best_score = -INF
    alpha = -INF
    beta = INF

    for move in _ordered_legal_moves(board):
        _check_deadline(deadline)
        board.push(move)
        score = -negamax_alpha_beta(board, depth - 1, -beta, -alpha, ply=1, deadline=deadline)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

        if score > alpha:
            alpha = score

    return best_move


def find_best_move_with_stats(board: chess.Board, depth: int) -> SearchRunStats:
    """Run baseline negamax and return best move, score, and visited nodes."""
    if depth < 1:
        raise ValueError("depth must be >= 1")

    best_move: chess.Move | None = None
    best_score = -INF
    counter = {"nodes": 0}

    for move in board.legal_moves:
        board.push(move)
        score = -_negamax_counted(board, depth - 1, 1, counter)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    return SearchRunStats(best_move=best_move, score=best_score, nodes=counter["nodes"])


def find_best_move_alpha_beta_with_stats(
    board: chess.Board,
    depth: int,
    deadline: float | None = None,
) -> SearchRunStats:
    """Run alpha-beta negamax and return best move, score, and visited nodes."""
    if depth < 1:
        raise ValueError("depth must be >= 1")

    best_move: chess.Move | None = None
    best_score = -INF
    alpha = -INF
    beta = INF
    counter = {"nodes": 0}

    for move in _ordered_legal_moves(board):
        _check_deadline(deadline)
        board.push(move)
        score = -_negamax_alpha_beta_counted(
            board,
            depth - 1,
            -beta,
            -alpha,
            1,
            counter,
            deadline,
        )
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

        if score > alpha:
            alpha = score

    return SearchRunStats(best_move=best_move, score=best_score, nodes=counter["nodes"])


def compare_search_nodes(board: chess.Board, depth: int) -> tuple[SearchRunStats, SearchRunStats]:
    """Return (plain_negamax_stats, alpha_beta_stats) at the same depth."""
    plain = find_best_move_with_stats(board, depth)
    alpha_beta = find_best_move_alpha_beta_with_stats(board, depth)
    return plain, alpha_beta


def iterative_deepening_search(
    board: chess.Board,
    max_depth: int,
    time_budget_sec: float,
) -> IterativeDeepeningResult:
    """Iterative deepening over alpha-beta+quiescence within a time budget."""
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")
    if time_budget_sec <= 0:
        raise ValueError("time_budget_sec must be > 0")

    start = time.monotonic()
    deadline = start + time_budget_sec

    best_move: chess.Move | None = None
    best_score = -INF
    depth_reached = 0
    total_nodes = 0
    timed_out = False

    for depth in range(1, max_depth + 1):
        try:
            stats = find_best_move_alpha_beta_with_stats(board, depth, deadline=deadline)
        except SearchTimeout:
            timed_out = True
            break

        total_nodes += stats.nodes
        if stats.best_move is not None:
            best_move = stats.best_move
            best_score = stats.score
            depth_reached = depth

    if best_move is None:
        best_move = next(iter(board.legal_moves), None)
        best_score = 0

    elapsed = time.monotonic() - start
    if elapsed >= time_budget_sec and depth_reached < max_depth:
        timed_out = True

    return IterativeDeepeningResult(
        best_move=best_move,
        score=best_score,
        depth_reached=depth_reached,
        nodes=total_nodes,
        timed_out=timed_out,
        time_spent_sec=elapsed,
    )


def search_with_time_controls(
    board: chess.Board,
    max_depth: int,
    movetime_ms: int | None = None,
    wtime_ms: int | None = None,
    btime_ms: int | None = None,
    winc_ms: int = 0,
    binc_ms: int = 0,
    fallback_ms: int = 2000,
) -> IterativeDeepeningResult:
    """Run iterative deepening using either movetime or simple clock allocation."""
    if movetime_ms is not None:
        if movetime_ms <= 0:
            raise ValueError("movetime_ms must be > 0")
        budget_sec = movetime_ms / 1000.0
    else:
        budget_sec = allocate_time_seconds(
            board=board,
            wtime_ms=wtime_ms,
            btime_ms=btime_ms,
            winc_ms=winc_ms,
            binc_ms=binc_ms,
            fallback_ms=fallback_ms,
        )

    return iterative_deepening_search(
        board=board,
        max_depth=max_depth,
        time_budget_sec=budget_sec,
    )
