import random

class MazeGenerator:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.grid_width = (2 * w) + 1
        self.grid_height = (2 * h) + 1
        self.grid = None
        self.visited = None
        self.steps = []

    def reset(self):
        self.grid = []
        for i in range(self.grid_height):
            row = []
            for j in range(self.grid_width):
                row.append(1) # 1 is wall
            self.grid.append(row)
        self.visited = set()
        self.steps = []

    def get_neighbors(self, r, c):
        n = []
        if r - 1 >= 0: n.append((r - 1, c))
        if r + 1 < self.height: n.append((r + 1, c))
        if c - 1 >= 0: n.append((r, c - 1))
        if c + 1 < self.width: n.append((r, c + 1))
        return n

    def remove_wall(self, r1, c1, r2, c2):
        # find the wall between them
        wall_r = r1 + r2 + 1
        wall_c = c1 + c2 + 1
        cell_r = (2 * r2) + 1
        cell_c = (2 * c2) + 1
        self.grid[wall_r][wall_c] = 0
        self.grid[cell_r][cell_c] = 0
        self.steps.append((cell_r, cell_c, wall_r, wall_c))

    def generate_dfs(self):
        self.reset()
        start_node = (0, 0)
        stack = [start_node]
        self.visited.add(start_node)
        self.grid[1][1] = 0
        self.steps.append((1, 1, None, None))

        while len(stack) > 0:
            curr_r, curr_c = stack[-1]
            unvisited = []
            for n in self.get_neighbors(curr_r, curr_c):
                if n not in self.visited:
                    unvisited.append(n)
                    
            if len(unvisited) > 0:
                next_r, next_c = random.choice(unvisited)
                self.remove_wall(curr_r, curr_c, next_r, next_c)
                self.visited.add((next_r, next_c))
                stack.append((next_r, next_c))
            else:
                stack.pop()
                
        return self.grid

    def generate_bfs(self):
        self.reset()
        start_node = (0, 0)
        queue = [start_node]
        self.visited.add(start_node)
        self.grid[1][1] = 0
        self.steps.append((1, 1, None, None))

        while len(queue) > 0:
            curr_r, curr_c = queue.pop(0) # pop from front
            neighbors = self.get_neighbors(curr_r, curr_c)
            random.shuffle(neighbors)
            for nr, nc in neighbors:
                if (nr, nc) not in self.visited:
                    self.remove_wall(curr_r, curr_c, nr, nc)
                    self.visited.add((nr, nc))
                    queue.append((nr, nc))
        return self.grid

    def generate_prim(self):
        self.reset()
        start = (0, 0)
        self.visited.add(start)
        self.grid[1][1] = 0
        self.steps.append((1, 1, None, None))
        
        frontier = []
        for n in self.get_neighbors(0, 0):
            frontier.append((n, start))

        while len(frontier) > 0:
            rand_idx = random.randint(0, len(frontier) - 1)
            current, parent = frontier.pop(rand_idx)
            
            curr_r, curr_c = current
            parent_r, parent_c = parent
            
            if current not in self.visited:
                self.remove_wall(parent_r, parent_c, curr_r, curr_c)
                self.visited.add(current)
                for nxt in self.get_neighbors(curr_r, curr_c):
                    if nxt not in self.visited:
                        frontier.append((nxt, current))
        return self.grid

    def analyze_maze(self):
        if self.grid == None:
            return {}
            
        dead_ends = 0
        open_spaces = 0
        for r in range(1, self.grid_height - 1, 2):
            for c in range(1, self.grid_width - 1, 2):
                if self.grid[r][c] == 0:
                    open_spaces += 1
                    
                    # count openings
                    openings = 0
                    if self.grid[r-1][c] == 0: openings += 1
                    if self.grid[r+1][c] == 0: openings += 1
                    if self.grid[r][c-1] == 0: openings += 1
                    if self.grid[r][c+1] == 0: openings += 1
                    
                    if openings == 1:
                        dead_ends += 1
                        
        return {"dead_ends": dead_ends, "total_open": open_spaces}
