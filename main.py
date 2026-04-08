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


def run_agent(name: str, agent, initial: Puzzle) -> None:
    print_separator()
    print(f"Agent: {name}")
    print_separator()

    start = time.time()
    solution = agent.solve(initial)
    elapsed = time.time() - start

    if solution:
        print_solution(solution)
    else:
        print("  No solution found within search limits.")

    print(f"  Nodes expanded : {agent.nodes_expanded}")
    print(f"  Time elapsed   : {elapsed:.4f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fifteen Puzzle Game solver")
    parser.add_argument(
        "--moves", type=int, default=20,
        help="Number of random moves from goal to generate the puzzle (default: 20)"
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
    run_agent("A* (Manhattan Distance)", AStarAgent(), initial)

    # ------------------------------------------------------------------ BFS
    # BFS can be very slow for puzzles with many moves; warn the user.
    print()
    print("NOTE: BFS and DFS may be slow for puzzles far from the goal.")
    run_agent("BFS (Breadth-First Search)", BFSAgent(), initial)

    # ------------------------------------------------------------------ DFS
    run_agent("DFS (Depth-First Search, IDDFS, limit=50)", DFSAgent(), initial)

    print_separator("=")


if __name__ == "__main__":
    main()
