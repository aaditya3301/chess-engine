import chess

from engine.search import find_best_move, find_best_move_alpha_beta, negamax


def test_mate_in_one_is_found() -> None:
    board = chess.Board("6k1/8/6KQ/8/8/8/8/8 w - - 0 1")
    best_move = find_best_move(board, depth=1)

    assert best_move is not None
    assert best_move.uci() == "h6g7"


def test_free_piece_capture_is_preferred() -> None:
    board = chess.Board("q3k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    best_move = find_best_move(board, depth=1)

    assert best_move is not None
    assert best_move.uci() == "a1a8"


def test_negamax_depth_zero_returns_int_score() -> None:
    board = chess.Board()
    score = negamax(board, depth=0)

    assert isinstance(score, int)


def test_alpha_beta_matches_plain_negamax_best_move_same_depth() -> None:
    board = chess.Board("q3k3/8/8/8/8/8/8/R3K3 w - - 0 1")

    best_plain = find_best_move(board, depth=2)
    best_ab = find_best_move_alpha_beta(board, depth=2)

    assert best_plain is not None
    assert best_ab is not None
    assert best_ab == best_plain
