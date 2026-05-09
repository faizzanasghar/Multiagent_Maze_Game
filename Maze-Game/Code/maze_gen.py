"""
Maze Generation Module
Implements DFS, BFS, and Prim's algorithms for maze generation.
No UI dependencies - pure algorithmic logic.
"""
import random
from collections import deque


class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid_width = 2 * width + 1
        self.grid_height = 2 * height + 1
        self.grid = None
        self.visited = None
        self.steps = []  # Stores generation steps for animated replay

    def reset_grid(self):
        self.grid = [[1] * self.grid_width for _ in range(self.grid_height)]
        self.visited = set()
        self.steps = []

    def get_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbors.append((nr, nc))
        return neighbors

    def _carve(self, curr_r, curr_c, next_r, next_c):
        """Remove wall between two logical cells and record the step."""
        wall_r = curr_r + next_r + 1
        wall_c = curr_c + next_c + 1
        cell_r = 2 * next_r + 1
        cell_c = 2 * next_c + 1
        self.grid[wall_r][wall_c] = 0
        self.grid[cell_r][cell_c] = 0
        self.steps.append((cell_r, cell_c, wall_r, wall_c))

    def generate_dfs(self):
        """DFS / Recursive Backtracking - instant, stores steps for replay."""
        self.reset_grid()
        start = (0, 0)
        stack = [start]
        self.visited.add(start)
        self.grid[1][1] = 0
        self.steps.append((1, 1, None, None))

        while stack:
            curr_r, curr_c = stack[-1]
            neighbors = [n for n in self.get_neighbors(curr_r, curr_c)
                         if n not in self.visited]
            if neighbors:
                next_r, next_c = random.choice(neighbors)
                self._carve(curr_r, curr_c, next_r, next_c)
                self.visited.add((next_r, next_c))
                stack.append((next_r, next_c))
            else:
                stack.pop()
        return self.grid

    def generate_bfs(self):
        """BFS-based generation - instant, stores steps for replay."""
        self.reset_grid()
        start = (0, 0)
        queue = deque([start])
        self.visited.add(start)
        self.grid[1][1] = 0
        self.steps.append((1, 1, None, None))

        while queue:
            curr_r, curr_c = queue.popleft()
            neighbors = self.get_neighbors(curr_r, curr_c)
            random.shuffle(neighbors)
            for next_r, next_c in neighbors:
                if (next_r, next_c) not in self.visited:
                    self._carve(curr_r, curr_c, next_r, next_c)
                    self.visited.add((next_r, next_c))
                    queue.append((next_r, next_c))
        return self.grid

    def generate_prim(self):
        """Prim's algorithm - instant, stores steps for replay."""
        self.reset_grid()
        start = (0, 0)
        self.visited.add(start)
        self.grid[1][1] = 0
        self.steps.append((1, 1, None, None))
        frontier = [(n, start) for n in self.get_neighbors(0, 0)]

        while frontier:
            idx = random.randrange(len(frontier))
            (curr_r, curr_c), (parent_r, parent_c) = frontier.pop(idx)
            if (curr_r, curr_c) not in self.visited:
                self._carve(parent_r, parent_c, curr_r, curr_c)
                self.visited.add((curr_r, curr_c))
                for next_node in self.get_neighbors(curr_r, curr_c):
                    if next_node not in self.visited:
                        frontier.append((next_node, (curr_r, curr_c)))
        return self.grid

    def analyze_maze(self):
        """Calculate maze metrics for analysis."""
        if not self.grid:
            return {}
        dead_ends = 0
        total_open = 0
        for r in range(1, self.grid_height - 1, 2):
            for c in range(1, self.grid_width - 1, 2):
                if self.grid[r][c] == 0:
                    total_open += 1
                    open_n = sum(1 for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]
                                if self.grid[r+dr][c+dc] == 0)
                    if open_n == 1:
                        dead_ends += 1
        return {"dead_ends": dead_ends, "total_open": total_open}
