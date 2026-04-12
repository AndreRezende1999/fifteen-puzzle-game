"""
Agents package for the Fifteen Puzzle Game.

Each agent implements a search strategy to solve the puzzle:
  - BFSAgent:   Breadth-First Search
  - DFSAgent:   Depth-First Search
  - AStarAgent: A* Search
"""

from .bfs_agent import BFSAgent
from .dfs_agent import DFSAgent
from .astar_agent import AStarAgent

__all__ = ["BFSAgent", "DFSAgent", "AStarAgent"]
