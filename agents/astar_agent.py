"""
A* Agent for the Fifteen Puzzle.

Uses the A* search algorithm with the Manhattan Distance heuristic.

Cost function:  f(n) = g(n) + h(n)
  g(n) = number of moves made so far (path cost)
  h(n) = Manhattan distance: sum of the distances of each tile from its
         goal position (admissible and consistent heuristic)

A* with an admissible heuristic guarantees an optimal solution.
Cycles are avoided by maintaining a visited set with the best known g(n)
for each state.
"""

import heapq
from typing import Dict, Optional, Tuple

from puzzle import Puzzle, BOARD_SIZE, GOAL_STATE

# Pre-compute the goal position of each tile for fast heuristic evaluation.
# goal_positions[tile] = (goal_row, goal_col)
GOAL_POSITIONS: Dict[int, Tuple[int, int]] = {
    GOAL_STATE[i]: divmod(i, BOARD_SIZE) for i in range(BOARD_SIZE * BOARD_SIZE)
}


def manhattan_distance(state: Tuple[int, ...]) -> int:
    """
    Compute the total Manhattan distance of all tiles from their goal positions.
    The blank tile (0) is excluded from the calculation.
    """
    total = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        row, col = divmod(idx, BOARD_SIZE)
        goal_row, goal_col = GOAL_POSITIONS[tile]
        total += abs(row - goal_row) + abs(col - goal_col)
    return total


class AStarAgent:
    """
    Agent that solves the 15-puzzle using the A* algorithm.

    The cost of each move is 1 (uniform step cost), so the total path cost
    g(n) equals the number of moves made. The heuristic h(n) is the
    Manhattan distance.

    Properties
    ----------
    nodes_expanded : int
        Number of nodes expanded during the last search.
    """

    def __init__(self):
        self.nodes_expanded: int = 0

    def solve(self, initial: Puzzle) -> Optional[Puzzle]:
        """
        Search for the goal state starting from *initial*.

        Parameters
        ----------
        initial : Puzzle
            The starting puzzle configuration.

        Returns
        -------
        Puzzle or None
            The goal node (with parent chain for path reconstruction) if a
            solution is found, otherwise None.
        """
        self.nodes_expanded = 0

        h = manhattan_distance(initial.state)
        # Priority queue entries: (f, tie_breaker, puzzle_node)
        counter = 0  # tie-breaker to avoid comparing Puzzle objects
        frontier: list = []
        heapq.heappush(frontier, (h, counter, initial))

        # Best known g(n) for each visited state
        best_g: Dict[Tuple[int, ...], int] = {initial.state: 0}

        while frontier:
            f, _, node = heapq.heappop(frontier)

            self.nodes_expanded += 1

            if node.is_goal():
                return node

            # Skip if we've already found a cheaper path to this state
            if node.cost > best_g.get(node.state, float("inf")):
                continue

            for move, successor in node.successors():
                g = successor.cost  # g(n) = parent.cost + 1
                if g < best_g.get(successor.state, float("inf")):
                    best_g[successor.state] = g
                    h = manhattan_distance(successor.state)
                    counter += 1
                    heapq.heappush(frontier, (g + h, counter, successor))

        return None  # No solution found
