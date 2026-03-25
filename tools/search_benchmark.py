from __future__ import annotations

import argparse
import sys
from pathlib import Path

import chess

try:
    from engine.search import compare_search_nodes
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from engine.search import compare_search_nodes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare plain negamax and alpha-beta node counts.")
    parser.add_argument("--depth", type=int, default=3, help="Search depth (>=1).")
    parser.add_argument(
        "--fen",
        type=str,
        default=chess.STARTING_FEN,
        help="FEN position to benchmark (default: starting position).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.depth < 1:
        raise ValueError("--depth must be >= 1")

    board = chess.Board(args.fen)
    plain, alpha_beta = compare_search_nodes(board, args.depth)

    reduction = 0.0
    if plain.nodes > 0:
        reduction = 100.0 * (plain.nodes - alpha_beta.nodes) / plain.nodes

    print(f"Depth: {args.depth}")
    print(f"FEN: {board.fen()}")
    print("")
    print("Plain negamax:")
    print(f"  best move: {plain.best_move}")
    print(f"  score: {plain.score}")
    print(f"  nodes: {plain.nodes}")
    print("")
    print("Alpha-beta:")
    print(f"  best move: {alpha_beta.best_move}")
    print(f"  score: {alpha_beta.score}")
    print(f"  nodes: {alpha_beta.nodes}")
    print("")
    print(f"Node reduction: {reduction:.2f}%")


if __name__ == "__main__":
    main()
