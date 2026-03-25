from __future__ import annotations

import chess

from engine.evaluate import evaluate

INF = 10**9
MATE_SCORE = 100_000
DRAW_SCORE = 0


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
