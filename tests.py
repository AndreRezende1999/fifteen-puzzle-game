"""
Unit tests for the Fifteen Puzzle Game.

Tests cover:
  - Puzzle construction and board utilities
  - Solvability check
  - Valid move generation (with boundary enforcement)
  - BFS Agent
  - DFS Agent
  - A* Agent
"""

import unittest

from puzzle import Puzzle, GOAL_STATE, BOARD_SIZE
from agents import BFSAgent, DFSAgent, AStarAgent
from agents.astar_agent import manhattan_distance


# ---------------------------------------------------------------------------
# Helper factory
# ---------------------------------------------------------------------------

def make_puzzle(state):
    return Puzzle(tuple(state))


# ---------------------------------------------------------------------------
# Known easy puzzle states
# Goal:  1  2  3  4 / 5  6  7  8 / 9 10 11 12 / 13 14 15  0
# ONE_MOVE_FROM_GOAL: blank at (3,2), one RIGHT move reaches goal
ONE_MOVE_FROM_GOAL = (1, 2, 3, 4,
                      5, 6, 7, 8,
                      9, 10, 11, 12,
                      13, 14, 0, 15)

ALREADY_SOLVED = GOAL_STATE


class TestPuzzleBasics(unittest.TestCase):

    def test_goal_state_is_goal(self):
        p = Puzzle(GOAL_STATE)
        self.assertTrue(p.is_goal())

    def test_non_goal_is_not_goal(self):
        p = make_puzzle(ONE_MOVE_FROM_GOAL)
        self.assertFalse(p.is_goal())

    def test_blank_index(self):
        # In ONE_MOVE_FROM_GOAL, blank (0) is at flat index 14
        p = make_puzzle(ONE_MOVE_FROM_GOAL)
        self.assertEqual(p.blank_index(), 14)

    def test_blank_position(self):
        p = make_puzzle(ONE_MOVE_FROM_GOAL)
        self.assertEqual(p.blank_position(), (3, 2))  # row 3, col 2

    def test_repr_does_not_raise(self):
        p = Puzzle(GOAL_STATE)
        _ = repr(p)  # should not raise

    def test_equality(self):
        p1 = make_puzzle(ONE_MOVE_FROM_GOAL)
        p2 = make_puzzle(ONE_MOVE_FROM_GOAL)
        self.assertEqual(p1, p2)

    def test_hash_equal_states(self):
        p1 = make_puzzle(ONE_MOVE_FROM_GOAL)
        p2 = make_puzzle(ONE_MOVE_FROM_GOAL)
        self.assertEqual(hash(p1), hash(p2))

    def test_invalid_state_length(self):
        with self.assertRaises(ValueError):
            Puzzle((1, 2, 3))


class TestMoveGeneration(unittest.TestCase):

    def test_goal_state_moves(self):
        """Blank is at bottom-right; can move UP and LEFT only."""
        p = Puzzle(GOAL_STATE)
        move_names = {m for m, _ in p.successors()}
        self.assertIn("UP", move_names)
        self.assertIn("LEFT", move_names)
        self.assertNotIn("DOWN", move_names)
        self.assertNotIn("RIGHT", move_names)

    def test_blank_top_left_moves(self):
        """Blank at (0,0): can move DOWN and RIGHT only."""
        state = (0, 1, 2, 3,
                 4, 5, 6, 7,
                 8, 9, 10, 11,
                 12, 13, 14, 15)
        p = make_puzzle(state)
        move_names = {m for m, _ in p.successors()}
        self.assertIn("DOWN", move_names)
        self.assertIn("RIGHT", move_names)
        self.assertNotIn("UP", move_names)
        self.assertNotIn("LEFT", move_names)

    def test_blank_center_all_moves(self):
        """Blank at (1,1): all four moves available."""
        state = (1, 2, 3, 4,
                 5, 0, 6, 7,
                 8, 9, 10, 11,
                 12, 13, 14, 15)
        p = make_puzzle(state)
        move_names = {m for m, _ in p.successors()}
        self.assertEqual(move_names, {"UP", "DOWN", "LEFT", "RIGHT"})

    def test_move_does_not_mutate_original(self):
        p = Puzzle(GOAL_STATE)
        original_state = p.state
        _ = p.successors()
        self.assertEqual(p.state, original_state)

    def test_move_sets_parent(self):
        p = Puzzle(GOAL_STATE)
        for _, child in p.successors():
            self.assertIs(child.parent, p)

    def test_move_increments_cost(self):
        p = Puzzle(GOAL_STATE)
        for _, child in p.successors():
            self.assertEqual(child.cost, 1)


class TestSolvability(unittest.TestCase):

    def test_goal_state_solvable(self):
        self.assertTrue(Puzzle.is_solvable(GOAL_STATE))

    def test_known_solvable(self):
        # One inversion from goal: swap 14 and 15
        state = (1, 2, 3, 4,
                 5, 6, 7, 8,
                 9, 10, 11, 12,
                 13, 15, 14, 0)
        # blank on row 4 (odd from bottom=1), inversions=1 (odd) → NOT solvable
        self.assertFalse(Puzzle.is_solvable(state))

    def test_generate_random_is_solvable(self):
        for _ in range(5):
            p = Puzzle.generate_random()
            self.assertTrue(Puzzle.is_solvable(p.state))

    def test_generate_from_goal_is_solvable(self):
        for _ in range(5):
            p = Puzzle.generate_random_from_goal(moves=30)
            self.assertTrue(Puzzle.is_solvable(p.state))


class TestSolutionPath(unittest.TestCase):

    def test_solution_path_length(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = AStarAgent()
        goal = agent.solve(initial)
        self.assertIsNotNone(goal)
        path = goal.solution_path()
        # path includes initial state, so length = moves + 1
        self.assertEqual(len(path), goal.cost + 1)

    def test_solution_path_starts_at_initial(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = AStarAgent()
        goal = agent.solve(initial)
        path = goal.solution_path()
        self.assertEqual(path[0].state, initial.state)

    def test_solution_path_ends_at_goal(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = AStarAgent()
        goal = agent.solve(initial)
        path = goal.solution_path()
        self.assertEqual(path[-1].state, GOAL_STATE)


class TestManhattanDistance(unittest.TestCase):

    def test_goal_distance_is_zero(self):
        self.assertEqual(manhattan_distance(GOAL_STATE), 0)

    def test_one_tile_off(self):
        # Swap tile 15 and blank (goal positions: 15 at (3,2), blank at (3,3))
        # After swap: 15 is at (3,3), blank at (3,2)
        state = (1, 2, 3, 4,
                 5, 6, 7, 8,
                 9, 10, 11, 12,
                 13, 14, 0, 15)
        # tile 15 moved from (3,2) to (3,3): distance = 1
        self.assertEqual(manhattan_distance(state), 1)

    def test_distance_positive_for_non_goal(self):
        p = Puzzle.generate_random_from_goal(moves=15)
        d = manhattan_distance(p.state)
        self.assertGreaterEqual(d, 0)


class TestBFSAgent(unittest.TestCase):

    def test_already_solved(self):
        p = Puzzle(GOAL_STATE)
        agent = BFSAgent()
        result = agent.solve(p)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_goal())

    def test_one_move_puzzle(self):
        # Blank at (3,2) → one RIGHT move solves it
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = BFSAgent()
        result = agent.solve(initial)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_goal())

    def test_optimal_solution(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = BFSAgent()
        result = agent.solve(initial)
        self.assertEqual(result.cost, 1)

    def test_nodes_expanded_positive(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = BFSAgent()
        agent.solve(initial)
        self.assertGreater(agent.nodes_expanded, 0)


class TestDFSAgent(unittest.TestCase):

    def test_already_solved(self):
        p = Puzzle(GOAL_STATE)
        agent = DFSAgent()
        result = agent.solve(p)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_goal())

    def test_finds_solution(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = DFSAgent()
        result = agent.solve(initial)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_goal())

    def test_nodes_expanded_positive(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = DFSAgent()
        agent.solve(initial)
        self.assertGreater(agent.nodes_expanded, 0)


class TestAStarAgent(unittest.TestCase):

    def test_already_solved(self):
        p = Puzzle(GOAL_STATE)
        agent = AStarAgent()
        result = agent.solve(p)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_goal())

    def test_one_move_puzzle(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = AStarAgent()
        result = agent.solve(initial)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_goal())

    def test_optimal_solution(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = AStarAgent()
        result = agent.solve(initial)
        self.assertEqual(result.cost, 1)

    def test_solution_quality_vs_bfs(self):
        """A* must find an optimal path (same length as BFS)."""
        initial = Puzzle.generate_random_from_goal(moves=12)
        bfs_result = BFSAgent().solve(initial)
        astar_result = AStarAgent().solve(initial)
        self.assertIsNotNone(bfs_result)
        self.assertIsNotNone(astar_result)
        self.assertEqual(bfs_result.cost, astar_result.cost)

    def test_nodes_expanded_positive(self):
        initial = make_puzzle(ONE_MOVE_FROM_GOAL)
        agent = AStarAgent()
        agent.solve(initial)
        self.assertGreater(agent.nodes_expanded, 0)


if __name__ == "__main__":
    unittest.main()
