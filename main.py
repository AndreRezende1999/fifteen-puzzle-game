"""
Fifteen Puzzle Game - Main entry point.

Demonstrates the 15-puzzle with three solving agents:
  1. BFS  - Breadth-First Search  (optimal, slow for hard puzzles)
  2. DFS  - Depth-First Search    (non-optimal, may find solution quickly)
  3. A*   - A* with Manhattan Distance (optimal, most efficient)

Usage:
    python main.py [--moves N]

Options:
    --moves N   Number of random moves from goal to generate the puzzle
                (default: 20).  Higher values produce harder puzzles.
"""

import argparse
import time
from typing import Dict

from puzzle import Puzzle
from agents import BFSAgent, DFSAgent, AStarAgent


def print_separator(char: str = "-", width: int = 48) -> None:
    print(char * width)


def print_board(puzzle: Puzzle, title: str = "") -> None:
    if title:
        print(f"\n{title}")
    print(puzzle)
    print()


def print_solution(goal_node: Puzzle) -> None:
    path = goal_node.solution_path()
    moves = goal_node.solution_moves()
    print(f"  Moves ({len(moves)}): {' -> '.join(moves) if moves else 'Already solved'}")
    print(f"  Path length: {len(path) - 1} step(s)")


def run_agent(name: str, agent, initial: Puzzle, max_nodes: int | None = None) -> None:
    print_separator()
    print(f"Agent: {name}")
    print_separator()

    start = time.time()
    solution = agent.solve(initial, max_nodes=max_nodes)
    elapsed = time.time() - start

    if solution:
        print_solution(solution)
    else:
        print("  No solution found within search limits.")

    print(f"  Nodes expanded : {agent.nodes_expanded}")
    print(f"  Time elapsed   : {elapsed:.4f}s")

def benchmark_agents(trials: int, moves: int, max_nodes: int, dfs_limit: int) -> Dict[str, dict]:
    """
    Compare BFS, DFS and A* over multiple random, solvable initial states.

    Returns aggregated metrics per method:
      - solved
      - avg_nodes_expanded
      - avg_moves_to_solution (solved runs only)
      - avg_time_seconds
    """
    aggregates = {
        "BFS": {"solved": 0, "nodes": 0, "moves": 0, "time": 0.0},
        "DFS": {"solved": 0, "nodes": 0, "moves": 0, "time": 0.0},
        "A*": {"solved": 0, "nodes": 0, "moves": 0, "time": 0.0},
    }

    for _ in range(trials):
        initial = Puzzle.generate_random_from_goal(moves=moves)
        experiments = [
            ("BFS", BFSAgent()),
            ("DFS", DFSAgent(depth_limit=dfs_limit)),
            ("A*", AStarAgent()),
        ]
        for label, agent in experiments:
            start = time.time()
            result = agent.solve(initial, max_nodes=max_nodes)
            elapsed = time.time() - start

            aggregates[label]["nodes"] += agent.nodes_expanded
            aggregates[label]["time"] += elapsed
            if result is not None:
                aggregates[label]["solved"] += 1
                aggregates[label]["moves"] += result.cost

    summary = {}
    for label, values in aggregates.items():
        solved = values["solved"]
        summary[label] = {
            "solved": solved,
            "avg_nodes_expanded": values["nodes"] / trials,
            "avg_moves_to_solution": (values["moves"] / solved) if solved else None,
            "avg_time_seconds": values["time"] / trials,
        }
    return summary


def print_benchmark(summary: Dict[str, dict], trials: int, moves: int, max_nodes: int) -> None:
    print_separator("=")
    print("COMPARATIVE ANALYSIS")
    print_separator("=")
    print(f"Trials: {trials} | Scramble moves: {moves} | Max expanded nodes/run: {max_nodes}")
    print()
    for method in ("BFS", "DFS", "A*"):
        stats = summary[method]
        moves_info = (
            f"{stats['avg_moves_to_solution']:.2f}"
            if stats["avg_moves_to_solution"] is not None
            else "N/A"
        )
        print(f"{method}:")
        print(f"  Solved runs         : {stats['solved']}/{trials}")
        print(f"  Avg nodes expanded  : {stats['avg_nodes_expanded']:.2f}")
        print(f"  Avg moves to goal   : {moves_info}")
        print(f"  Avg time            : {stats['avg_time_seconds']:.6f}s")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Fifteen Puzzle Game solver")
    parser.add_argument(
        "--moves", type=int, default=20,
        help="Number of random moves from goal to generate the puzzle (default: 20)"
    )
    parser.add_argument(
        "--max-nodes", type=int, default=200000,
        help="Maximum number of expanded nodes allowed per run (default: 200000)"
    )
    parser.add_argument(
        "--dfs-limit", type=int, default=50,
        help="Depth limit used by DFS/IDDFS (default: 50)"
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Run comparative analysis with several random initial states"
    )
    parser.add_argument(
        "--trials", type=int, default=10,
        help="Number of random initial states used in comparative analysis (default: 10)"
    )
    args = parser.parse_args()

    print("=" * 48)
    print("         FIFTEEN PUZZLE GAME SOLVER")
    print("=" * 48)

    # Generate a solvable puzzle
    initial = Puzzle.generate_random_from_goal(moves=args.moves)

    print_board(initial, title="Initial Board:")
    print(f"Solvable: {Puzzle.is_solvable(initial.state)}")

    # ------------------------------------------------------------------ A*
    run_agent("A* (Manhattan Distance)", AStarAgent(), initial, max_nodes=args.max_nodes)

    # ------------------------------------------------------------------ BFS
    # BFS can be very slow for puzzles with many moves; warn the user.
    print()
    print("NOTE: BFS and DFS may be slow for puzzles far from the goal.")
    run_agent("BFS (Breadth-First Search)", BFSAgent(), initial, max_nodes=args.max_nodes)

    # ------------------------------------------------------------------ DFS
    run_agent(
        f"DFS (Depth-First Search, IDDFS, limit={args.dfs_limit})",
        DFSAgent(depth_limit=args.dfs_limit),
        initial,
        max_nodes=args.max_nodes
    )

    if args.compare:
        print()
        summary = benchmark_agents(
            trials=args.trials,
            moves=args.moves,
            max_nodes=args.max_nodes,
            dfs_limit=args.dfs_limit
        )
        print_benchmark(summary, args.trials, args.moves, args.max_nodes)

    print_separator("=")


if __name__ == "__main__":
    main()
