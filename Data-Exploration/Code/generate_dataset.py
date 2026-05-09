"""
Generate maze metrics dataset for algorithm comparison.
"""
import csv
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../Maze-Game/Code"))
from maze_gen import MazeGenerator


def bfs_path_length(grid, start=(1, 1), end=None):
    if end is None:
        end = (len(grid) - 2, len(grid[0]) - 2)
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        (r, c), dist = queue.popleft()
        if (r, c) == end:
            return dist
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), dist + 1))
    return -1


def calc_metrics(grid):
    dead_ends = 0
    total_branching = 0
    path_cells = 0
    for r in range(1, len(grid) - 1):
        for c in range(1, len(grid[0]) - 1):
            if grid[r][c] == 0:
                path_cells += 1
                nbrs = sum(1 for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                           if grid[r + dr][c + dc] == 0)
                if nbrs == 1:
                    dead_ends += 1
                total_branching += nbrs
    return {
        "dead_ends": dead_ends,
        "avg_branching": round(total_branching / path_cells, 4) if path_cells else 0,
        "path_length": bfs_path_length(grid),
    }


def main():
    iterations = 50
    size = 15
    out_dir = os.path.join(os.path.dirname(__file__), "Dataset")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "maze_metrics.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Algorithm", "Iteration", "Dead Ends", "Avg Branching", "Path Length"])
        gen = MazeGenerator(size, size)
        for alg_name, method in [("DFS", gen.generate_dfs),
                                  ("BFS", gen.generate_bfs),
                                  ("Prim", gen.generate_prim)]:
            print(f"Generating {alg_name}…")
            for i in range(iterations):
                grid = method()
                m = calc_metrics(grid)
                writer.writerow([alg_name, i, m["dead_ends"], m["avg_branching"], m["path_length"]])
    print("Done — Dataset/maze_metrics.csv written.")


if __name__ == "__main__":
    main()
