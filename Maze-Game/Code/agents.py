"""
AI Agents Module
- AIPlayer: Minimax with Alpha-Beta pruning & True-Distance Heuristic
- MonsterAgent: A* pathfinding using True Distance
"""
import math
import heapq
from collections import deque

def true_distance(gs, start, goal):
    """Calculates the actual shortest path length using BFS. Much smarter than Manhattan in mazes."""
    if start == goal: return 0
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        curr, dist = queue.popleft()
        if curr == goal:
            return dist
        for nxt in gs.get_valid_moves(curr):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, dist + 1))
    return 999 # Unreachable

class MonsterAgent:
    """Monster that chases the player with the higher score."""

    def __init__(self, game_state):
        self.gs = game_state

    def get_next_move(self):
        # Target whoever has a higher score
        if self.gs.ai_score > self.gs.player_score:
            target = self.gs.ai_pos
        else:
            target = self.gs.player_pos
        return self._a_star(self.gs.monster_pos, target)

    def _a_star(self, start, goal):
        frontier = [(0, start)]
        came_from = {start: None}
        cost = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal:
                break
            for nxt in self.gs.get_valid_moves(current):
                new_cost = cost[current] + 1
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    # Using true distance is expensive for A*, but grid is small. For performance, we can stick to manhattan for the heuristic, but true distance for actual behavior. Let's use manhattan for the A* heuristic to keep it fast.
                    h = abs(nxt[0] - goal[0]) + abs(nxt[1] - goal[1])
                    heapq.heappush(frontier, (new_cost + h, nxt))
                    came_from[nxt] = current

        # Reconstruct first step
        if goal not in came_from:
            return start
        curr = goal
        while came_from.get(curr) is not None and came_from[curr] != start:
            curr = came_from[curr]
        return curr if came_from.get(curr) == start else start


class AIPlayer:
    """AI player using Minimax with Alpha-Beta pruning."""

    def __init__(self, game_state, depth=3):
        self.gs = game_state
        self.depth = depth

    def evaluate(self):
        score = (self.gs.ai_score - self.gs.player_score) * 20

        # Coin proximity bonus (True Distance)
        for coin in self.gs.coins:
            d = true_distance(self.gs, self.gs.ai_pos, coin)
            if d < 10:
                score += max(0, 15 - d)

        # Exit proximity (only when unlocked)
        if self.gs.exits:
            d_exit = min(true_distance(self.gs, self.gs.ai_pos, e) for e in self.gs.exits)
            if self.gs.exits_unlocked:
                score -= d_exit * 5
            else:
                score -= d_exit * 0.5

        # Monster danger (True Distance)
        d_monster = true_distance(self.gs, self.gs.ai_pos, self.gs.monster_pos)
        if d_monster < 5:
            score -= (8 - d_monster) * 25

        return score

    def get_best_move(self):
        self.nodes = 0
        self.prunes = 0
        best_val = -math.inf
        best_move = self.gs.ai_pos
        moves = self.gs.get_valid_moves(self.gs.ai_pos)
        if not moves:
            return best_move

        for move in moves:
            saved = self.gs.ai_pos
            self.gs.ai_pos = move
            val = self._minimax(self.depth - 1, -math.inf, math.inf, False)
            self.gs.ai_pos = saved
            if val > best_val:
                best_val = val
                best_move = move
        return best_move

    def _minimax(self, depth, alpha, beta, is_max):
        self.nodes += 1
        if depth == 0 or self.gs.game_over:
            return self.evaluate()

        if is_max:
            max_eval = -math.inf
            for move in self.gs.get_valid_moves(self.gs.ai_pos):
                saved = self.gs.ai_pos
                self.gs.ai_pos = move
                val = self._minimax(depth - 1, alpha, beta, False)
                self.gs.ai_pos = saved
                max_eval = max(max_eval, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    self.prunes += 1
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in self.gs.get_valid_moves(self.gs.player_pos):
                saved = self.gs.player_pos
                self.gs.player_pos = move
                val = self._minimax(depth - 1, alpha, beta, True)
                self.gs.player_pos = saved
                min_eval = min(min_eval, val)
                beta = min(beta, val)
                if beta <= alpha:
                    self.prunes += 1
                    break
            return min_eval

