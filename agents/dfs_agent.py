"""
DFS Agent - Depth-First Search for the Fifteen Puzzle.

Explores nodes along each branch before backtracking (LIFO stack). Cycles
are avoided by tracking the states on the current path (recursion stack) as
well as a global visited set.

Note: DFS does NOT guarantee the shortest path. A depth limit is used to
prevent infinite recursion on the 15-puzzle's large state space.
"""

from typing import Optional, Set

from puzzle import Puzzle

# Default depth limit to prevent very deep (potentially infinite) searches.
DEFAULT_DEPTH_LIMIT = 50


class DFSAgent:
    """
    Agent that solves the 15-puzzle using Depth-First Search (DFS).

    Parameters
    ----------
    depth_limit : int
        Maximum search depth. Defaults to DEFAULT_DEPTH_LIMIT.

    Properties
    ----------
    nodes_expanded : int
        Number of nodes expanded during the last search.
    """

    def __init__(self, depth_limit: int = DEFAULT_DEPTH_LIMIT):
        self.depth_limit = depth_limit
        self.nodes_expanded: int = 0

    def solve(self, initial: Puzzle) -> Optional[Puzzle]:
        """
        Search for the goal state starting from *initial* using iterative
        deepening DFS (IDDFS) to combine the space efficiency of DFS with
        completeness across increasing depth bounds.

        Parameters
        ----------
        initial : Puzzle
            The starting puzzle configuration.

        Returns
        -------
        Puzzle or None
            The goal node (with parent chain for path reconstruction) if a
            solution is found within the depth limit, otherwise None.
        """
        self.nodes_expanded = 0

        for limit in range(self.depth_limit + 1):
            visited: Set[tuple] = set()
            result = self._dfs(initial, limit, visited)
            if result is not None:
                return result

        return None  # No solution found within depth limit

    def _dfs(self, node: Puzzle, remaining_depth: int,
             visited: Set[tuple]) -> Optional[Puzzle]:
        """Recursive DFS with cycle detection and depth limiting."""
        self.nodes_expanded += 1

        if node.is_goal():
            return node

        if remaining_depth == 0:
            return None

        visited.add(node.state)

        for move, successor in node.successors():
            if successor.state not in visited:
                result = self._dfs(successor, remaining_depth - 1, visited)
                if result is not None:
                    return result

        # Backtrack: remove from visited so other paths can use this state
        visited.discard(node.state)

        return None
