"""
Fifteen Puzzle Game - Core Puzzle module.

Represents the 4x4 sliding puzzle with 15 numbered tiles and one empty space.
Provides state management, valid move generation, and solvability checking.
"""

import random
from typing import List, Optional, Tuple


# Goal state: tiles 1-15 followed by the empty space (0)
GOAL_STATE: Tuple[int, ...] = tuple(range(1, 16)) + (0,)
BOARD_SIZE = 4


class Puzzle:
    """
    Represents a state of the 15-puzzle on a 4x4 board.

    The board is stored as a flat tuple of 16 integers (0 = empty space).
    Position mapping:
        0  1  2  3
        4  5  6  7
        8  9  10 11
       12  13 14 15
    """

    def __init__(self, state: Tuple[int, ...], parent: Optional["Puzzle"] = None,
                 move: Optional[str] = None, cost: int = 0):
        if len(state) != BOARD_SIZE * BOARD_SIZE:
            raise ValueError(f"State must have {BOARD_SIZE * BOARD_SIZE} elements.")
        self.state = state
        self.parent = parent
        self.move = move        # The move that led to this state
        self.cost = cost        # g(n): cost to reach this state (depth)

    # ------------------------------------------------------------------
    # Board utilities
    # ------------------------------------------------------------------

    def blank_index(self) -> int:
        """Return the flat index of the empty space (0)."""
        return self.state.index(0)

    def blank_position(self) -> Tuple[int, int]:
        """Return the (row, col) position of the empty space."""
        idx = self.blank_index()
        return divmod(idx, BOARD_SIZE)

    def is_goal(self) -> bool:
        """Return True if this state is the goal state."""
        return self.state == GOAL_STATE

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Puzzle):
            return self.state == other.state
        return False

    def __hash__(self) -> int:
        return hash(self.state)

    def __repr__(self) -> str:
        lines = []
        for row in range(BOARD_SIZE):
            line = []
            for col in range(BOARD_SIZE):
                val = self.state[row * BOARD_SIZE + col]
                line.append(f"{val:2}" if val != 0 else " _")
            lines.append(" ".join(line))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Move generation
    # ------------------------------------------------------------------

    def successors(self) -> List[Tuple[str, "Puzzle"]]:
        """
        Generate all valid successor (move, state) pairs.

        Valid moves slide the empty space:
          - UP:    blank moves up    (tile above moves down)
          - DOWN:  blank moves down  (tile below moves up)
          - LEFT:  blank moves left  (tile to the left moves right)
          - RIGHT: blank moves right (tile to the right moves left)

        Returns a list of (move_name, new_puzzle) pairs.
        """
        row, col = self.blank_position()
        moves = []

        # UP: blank goes to row-1
        if row > 0:
            moves.append(("UP", self._swap(row * BOARD_SIZE + col,
                                           (row - 1) * BOARD_SIZE + col, "UP")))
        # DOWN: blank goes to row+1
        if row < BOARD_SIZE - 1:
            moves.append(("DOWN", self._swap(row * BOARD_SIZE + col,
                                             (row + 1) * BOARD_SIZE + col, "DOWN")))
        # LEFT: blank goes to col-1
        if col > 0:
            moves.append(("LEFT", self._swap(row * BOARD_SIZE + col,
                                             row * BOARD_SIZE + col - 1, "LEFT")))
        # RIGHT: blank goes to col+1
        if col < BOARD_SIZE - 1:
            moves.append(("RIGHT", self._swap(row * BOARD_SIZE + col,
                                              row * BOARD_SIZE + col + 1, "RIGHT")))
        return moves

    def _swap(self, i: int, j: int, move: str) -> "Puzzle":
        """Return a new Puzzle with positions i and j swapped, recording the move."""
        lst = list(self.state)
        lst[i], lst[j] = lst[j], lst[i]
        return Puzzle(tuple(lst), parent=self, move=move, cost=self.cost + 1)

    # ------------------------------------------------------------------
    # Solvability check
    # ------------------------------------------------------------------

    @staticmethod
    def is_solvable(state: Tuple[int, ...]) -> bool:
        """
        Determine if a given 4x4 15-puzzle state is solvable.

        A configuration is solvable when:
          - The blank is on an even row from the bottom AND the number of
            inversions is odd, OR
          - The blank is on an odd row from the bottom AND the number of
            inversions is even.

        Reference: https://www.cs.bham.ac.uk/~mdr/teaching/modules04/CS2150/search.pdf
        """
        inversions = Puzzle._count_inversions(state)
        blank_row_from_bottom = BOARD_SIZE - state.index(0) // BOARD_SIZE  # 1-indexed
        if blank_row_from_bottom % 2 == 0:
            return inversions % 2 == 1
        return inversions % 2 == 0

    @staticmethod
    def _count_inversions(state: Tuple[int, ...]) -> int:
        """Count the number of inversions (excluding the blank tile)."""
        tiles = [t for t in state if t != 0]
        count = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] > tiles[j]:
                    count += 1
        return count

    # ------------------------------------------------------------------
    # Solution path
    # ------------------------------------------------------------------

    def solution_path(self) -> List["Puzzle"]:
        """Return the list of states from the initial state to this state."""
        path = []
        node: Optional[Puzzle] = self
        while node is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    def solution_moves(self) -> List[str]:
        """Return the list of moves from the initial state to this state."""
        path = self.solution_path()
        moves = []
        for i in range(1, len(path)):
            node = path[i]
            if node.move:
                moves.append(node.move)
        return moves

    # ------------------------------------------------------------------
    # Random puzzle generation
    # ------------------------------------------------------------------

    @classmethod
    def generate_random(cls) -> "Puzzle":
        """
        Generate a random, solvable 15-puzzle state.
        Keeps shuffling until a solvable configuration is found.
        """
        tiles = list(range(16))
        while True:
            random.shuffle(tiles)
            state = tuple(tiles)
            if cls.is_solvable(state):
                return cls(state)

    @classmethod
    def generate_random_from_goal(cls, moves: int = 50) -> "Puzzle":
        """
        Generate a solvable puzzle by applying a given number of random
        moves starting from the goal state. This guarantees solvability.
        """
        puzzle = cls(GOAL_STATE)
        for _ in range(moves):
            successors = puzzle.successors()
            _, next_puzzle = random.choice(successors)
            # Reset parent so the generated puzzle has no solution chain
            puzzle = cls(next_puzzle.state)
        return puzzle
