"""
TP1 - Fundamentos de IA
Jogo do 15 em arquivo unico, simples e comentado.
"""

import argparse
import heapq
import random
import time
from collections import deque
from typing import Dict, List, Optional, Tuple

BOARD_SIZE = 4
GOAL_STATE: Tuple[int, ...] = tuple(range(1, 16)) + (0,)

# Limites fixos (o enunciado recomenda encerrar apos um limite alto de movimentos/nos).
MAX_NODES = 200000
DFS_MAX_DEPTH = 50

# Valores padrao para experimentos.
DEFAULT_SCRAMBLE_MOVES = 20
DEFAULT_TRIALS = 10

State = Tuple[int, ...]


def print_board(state: State) -> None:
    """Mostra o tabuleiro no formato 4x4."""
    for i in range(0, 16, 4):
        row = []
        for value in state[i:i + 4]:
            row.append(f"{value:2d}" if value != 0 else " _")
        print(" ".join(row))


def successors(state: State) -> List[Tuple[str, State]]:
    """Retorna os estados vizinhos validos."""
    idx = state.index(0)
    row, col = divmod(idx, BOARD_SIZE)
    result: List[Tuple[str, State]] = []

    def swap(i: int, j: int) -> State:
        values = list(state)
        values[i], values[j] = values[j], values[i]
        return tuple(values)

    if row > 0:
        result.append(("UP", swap(idx, idx - BOARD_SIZE)))
    if row < BOARD_SIZE - 1:
        result.append(("DOWN", swap(idx, idx + BOARD_SIZE)))
    if col > 0:
        result.append(("LEFT", swap(idx, idx - 1)))
    if col < BOARD_SIZE - 1:
        result.append(("RIGHT", swap(idx, idx + 1)))
    return result


# ------------------------------ Tarefa 1 ------------------------------

def count_inversions(state: State) -> int:
    """Conta inversoes ignorando o 0."""
    tiles = [x for x in state if x != 0]
    total = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                total += 1
    return total


def is_solvable(state: State) -> bool:
    """Verifica se o estado do 15-puzzle e solucionavel."""
    inversions = count_inversions(state)
    blank_row_from_bottom = BOARD_SIZE - (state.index(0) // BOARD_SIZE)
    # Regra para grade 4x4.
    return (inversions + blank_row_from_bottom) % 2 == 1


# ------------------------------ Tarefa 2 ------------------------------

def generate_initial_state(scramble_moves: int) -> State:
    """
    Gera estado aleatorio aplicando movimentos validos a partir do objetivo.
    Assim, o estado inicial sempre sera solucionavel.
    """
    state = GOAL_STATE
    opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
    last_move: Optional[str] = None

    for _ in range(scramble_moves):
        options = successors(state)
        if last_move is not None:
            filtered = [(m, s) for m, s in options if m != opposite[last_move]]
            if filtered:
                options = filtered
        move, state = random.choice(options)
        last_move = move
    return state


def reconstruct_moves(
    parent: Dict[State, Tuple[Optional[State], Optional[str]]],
    goal: State,
) -> List[str]:
    """Reconstrucao do caminho do estado inicial ate o objetivo."""
    moves: List[str] = []
    current = goal
    while parent[current][0] is not None:
        prev, move = parent[current]
        moves.append(move or "")
        current = prev  # type: ignore[assignment]
    moves.reverse()
    return moves


def result_dict(solved: bool, moves: List[str], expanded: int, started_at: float) -> Dict[str, object]:
    return {
        "solved": solved,
        "moves": moves,
        "nodes": expanded,
        "time": time.perf_counter() - started_at,
    }


# ------------------------------ Tarefa 3: BFS ------------------------------

def solve_bfs(initial: State) -> Dict[str, object]:
    start = time.perf_counter()
    expanded = 0
    queue = deque([initial])
    visited = {initial}
    parent: Dict[State, Tuple[Optional[State], Optional[str]]] = {initial: (None, None)}

    while queue:
        current = queue.popleft()
        expanded += 1

        if current == GOAL_STATE:
            return result_dict(True, reconstruct_moves(parent, current), expanded, start)
        if expanded >= MAX_NODES:
            break

        for move, nxt in successors(current):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = (current, move)
            queue.append(nxt)

    return result_dict(False, [], expanded, start)


# ------------------------------ Tarefa 3: DFS ------------------------------

def solve_dfs(initial: State) -> Dict[str, object]:
    start = time.perf_counter()
    expanded = 0
    stack: List[Tuple[State, int]] = [(initial, 0)]

    # Guarda menor profundidade onde cada estado foi visto (evita ciclos).
    best_depth: Dict[State, int] = {initial: 0}
    parent: Dict[State, Tuple[Optional[State], Optional[str]]] = {initial: (None, None)}

    while stack:
        current, depth = stack.pop()
        expanded += 1

        if current == GOAL_STATE:
            return result_dict(True, reconstruct_moves(parent, current), expanded, start)
        if expanded >= MAX_NODES:
            break
        if depth >= DFS_MAX_DEPTH:
            continue

        for move, nxt in reversed(successors(current)):
            next_depth = depth + 1
            seen_depth = best_depth.get(nxt)
            if seen_depth is not None and seen_depth <= next_depth:
                continue
            best_depth[nxt] = next_depth
            parent[nxt] = (current, move)
            stack.append((nxt, next_depth))

    return result_dict(False, [], expanded, start)


# ------------------------------ Tarefa 4: A* ------------------------------

def manhattan_distance(state: State) -> int:
    """h(n): soma das distancias de Manhattan de cada peca ate a meta."""
    total = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        row, col = divmod(idx, BOARD_SIZE)
        goal_idx = tile - 1
        goal_row, goal_col = divmod(goal_idx, BOARD_SIZE)
        total += abs(row - goal_row) + abs(col - goal_col)
    return total


def solve_astar(initial: State) -> Dict[str, object]:
    start = time.perf_counter()
    expanded = 0

    # Heap guarda: (f(n), g(n), estado)
    heap: List[Tuple[int, int, State]] = [(manhattan_distance(initial), 0, initial)]
    g_cost: Dict[State, int] = {initial: 0}
    parent: Dict[State, Tuple[Optional[State], Optional[str]]] = {initial: (None, None)}

    while heap:
        _, g, current = heapq.heappop(heap)
        if g != g_cost.get(current):
            continue

        expanded += 1

        if current == GOAL_STATE:
            return result_dict(True, reconstruct_moves(parent, current), expanded, start)
        if expanded >= MAX_NODES:
            break

        for move, nxt in successors(current):
            new_g = g + 1
            old_g = g_cost.get(nxt, 10**9)
            if new_g >= old_g:
                continue
            g_cost[nxt] = new_g
            parent[nxt] = (current, move)
            heapq.heappush(heap, (new_g + manhattan_distance(nxt), new_g, nxt))

    return result_dict(False, [], expanded, start)


# ------------------------------ Tarefa 5 ------------------------------

def run_all_methods(initial: State) -> Dict[str, Dict[str, object]]:
    return {
        "BFS": solve_bfs(initial),
        "DFS": solve_dfs(initial),
        "A*": solve_astar(initial),
    }


def compare_methods(trials: int, scramble_moves: int) -> Dict[str, Dict[str, float]]:
    totals = {
        "BFS": {"solved": 0, "nodes": 0.0, "moves": 0.0, "time": 0.0},
        "DFS": {"solved": 0, "nodes": 0.0, "moves": 0.0, "time": 0.0},
        "A*": {"solved": 0, "nodes": 0.0, "moves": 0.0, "time": 0.0},
    }

    for _ in range(trials):
        initial = generate_initial_state(scramble_moves)
        results = run_all_methods(initial)
        for method in ("BFS", "DFS", "A*"):
            result = results[method]
            totals[method]["nodes"] += float(result["nodes"])
            totals[method]["time"] += float(result["time"])
            if bool(result["solved"]):
                totals[method]["solved"] += 1
                totals[method]["moves"] += float(len(result["moves"]))  # type: ignore[arg-type]

    summary: Dict[str, Dict[str, float]] = {}
    for method in ("BFS", "DFS", "A*"):
        solved = totals[method]["solved"]
        avg_moves = -1.0
        if solved > 0:
            avg_moves = totals[method]["moves"] / solved
        summary[method] = {
            "solved": float(solved),
            "avg_nodes": totals[method]["nodes"] / trials,
            "avg_moves": avg_moves,
            "avg_time": totals[method]["time"] / trials,
        }
    return summary


def print_single_execution(initial: State, results: Dict[str, Dict[str, object]]) -> None:
    print("=" * 60)
    print("JOGO DO 15 - EXECUCAO UNICA")
    print("=" * 60)
    print("Estado inicial:")
    print_board(initial)
    print(f"\nSolucionavel? {is_solvable(initial)}")
    print(f"Limites: MAX_NODES={MAX_NODES}, DFS_MAX_DEPTH={DFS_MAX_DEPTH}\n")

    for method in ("BFS", "DFS", "A*"):
        result = results[method]
        solved = bool(result["solved"])
        moves = result["moves"]  # type: ignore[assignment]
        print(f"{method}:")
        print(f"  Resolvido: {'sim' if solved else 'nao'}")
        print(f"  Nos expandidos: {result['nodes']}")
        print(f"  Movimentos: {len(moves) if solved else 'N/A'}")
        print(f"  Tempo (s): {float(result['time']):.6f}")
        if solved:
            print(f"  Caminho: {' -> '.join(moves) if moves else 'ja estava resolvido'}")
        print()


def print_comparison(summary: Dict[str, Dict[str, float]], trials: int, scramble_moves: int) -> None:
    print("=" * 60)
    print("JOGO DO 15 - COMPARACAO")
    print("=" * 60)
    print(
        f"trials={trials} | scramble_moves={scramble_moves} | "
        f"MAX_NODES={MAX_NODES} | DFS_MAX_DEPTH={DFS_MAX_DEPTH}\n"
    )

    for method in ("BFS", "DFS", "A*"):
        data = summary[method]
        solved = int(data["solved"])
        avg_moves = "N/A" if data["avg_moves"] < 0 else f"{data['avg_moves']:.2f}"
        print(f"{method}:")
        print(f"  Resolvidos: {solved}/{trials}")
        print(f"  Media de nos expandidos: {data['avg_nodes']:.2f}")
        print(f"  Media de movimentos: {avg_moves}")
        print(f"  Media de tempo (s): {data['avg_time']:.6f}")
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TP1 - Jogo do 15 (arquivo unico)")
    parser.add_argument("--compare", action="store_true", help="Ativa comparacao dos metodos.")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help="Numero de experimentos no modo compare.")
    parser.add_argument("--moves", type=int, default=DEFAULT_SCRAMBLE_MOVES, help="Movimentos aleatorios para gerar estado inicial.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.compare:
        summary = compare_methods(trials=args.trials, scramble_moves=args.moves)
        print_comparison(summary, trials=args.trials, scramble_moves=args.moves)
        return

    initial = generate_initial_state(scramble_moves=args.moves)
    results = run_all_methods(initial)
    print_single_execution(initial, results)


if __name__ == "__main__":
    main()
