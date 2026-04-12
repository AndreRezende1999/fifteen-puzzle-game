"""
BFS Agent - Breadth-First Search for the Fifteen Puzzle.

Explores nodes level by level (FIFO queue). Guarantees the shortest path
in terms of number of moves. Cycles are avoided by tracking visited states.
"""

from collections import deque
from typing import Optional

from puzzle import Puzzle


class BFSAgent:
    """
    Agent that solves the 15-puzzle using Breadth-First Search (BFS).

    Properties
    ----------
    nodes_expanded : int
        Number of nodes expanded during the last search.
    """

    def __init__(self):
        self.nodes_expanded: int = 0

    def solve(self, initial: Puzzle, max_nodes: Optional[int] = None) -> Optional[Puzzle]:
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

        if initial.is_goal():
            return initial

        # FIFO queue for BFS
        frontier: deque = deque()
        frontier.append(initial)

        # Visited set to avoid cycles
        visited = {initial.state}

        while frontier:
            node = frontier.popleft()
            self.nodes_expanded += 1
            if node.is_goal():
                return node
            if max_nodes is not None and self.nodes_expanded >= max_nodes:
                return None

            for move, successor in node.successors():
                if successor.state not in visited:
                    if successor.is_goal():
                        self.nodes_expanded += 1
                        return successor
                    visited.add(successor.state)
                    frontier.append(successor)

        return None  # No solution found
