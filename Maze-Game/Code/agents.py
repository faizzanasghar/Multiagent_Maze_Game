import heapq

# helper for distance
def manhattan_distance(start, goal):
    # just calculate manhattan dist
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

class MonsterAgent:
    def __init__(self, game_state):
        self.game = game_state

    def get_next_move(self):
        # figure out who to chase
        if self.game.ai_score > self.game.player_score:
            target = self.game.ai_pos
        else:
            target = self.game.player_pos
            
        return self.run_a_star(self.game.monster_pos, target)

    def run_a_star(self, start, goal):
        frontier = [(0, start)]
        came_from = {}
        came_from[start] = None
        cost_so_far = {}
        cost_so_far[start] = 0

        while len(frontier) > 0:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_step in self.game.get_valid_moves(current):
                new_cost = cost_so_far[current] + 1
                if next_step not in cost_so_far or new_cost < cost_so_far[next_step]:
                    cost_so_far[next_step] = new_cost
                    # heuristic
                    priority = new_cost + manhattan_distance(next_step, goal)
                    heapq.heappush(frontier, (priority, next_step))
                    came_from[next_step] = current

        # track back the path to find the first step to take
        if goal not in came_from:
            return start
            
        curr = goal
        while came_from.get(curr) != None and came_from[curr] != start:
            curr = came_from[curr]
            
        if came_from.get(curr) == start:
            return curr
        return start


class AIPlayer:
    def __init__(self, game_state, depth=3):
        self.game = game_state
        self.max_depth = depth

    def evaluate(self):
        # if the game is over and someone escaped
        if self.game.exits_unlocked:
            if self.game.ai_pos in self.game.exits:
                return 999999
            if self.game.player_pos in self.game.exits:
                return -999999

        # Score = (AI coins - Human coins) - distance_to_exit - danger_from_monster
        total_score = (self.game.ai_score - self.game.player_score) * 20

        # distance to exit
        dist_to_exit = 0
        if len(self.game.exits) > 0:
            # find closest exit
            min_dist = 999
            for e in self.game.exits:
                d = manhattan_distance(self.game.ai_pos, e)
                if d < min_dist:
                    min_dist = d
            dist_to_exit = min_dist
            
            if self.game.exits_unlocked:
                total_score -= dist_to_exit * 2
            else:
                total_score -= dist_to_exit * 0.5

        # monster danger
        m_dist = manhattan_distance(self.game.ai_pos, self.game.monster_pos)
        danger = max(0, 10 - m_dist)
        total_score = total_score - (danger * 5)

        # go for coins
        if len(self.game.coins) > 0:
            c_dist = 999
            for c in self.game.coins:
                d = manhattan_distance(self.game.ai_pos, c)
                if d < c_dist:
                    c_dist = d
            total_score -= c_dist

        return total_score

    def get_best_move(self):
        best_score = -999999
        best_move = self.game.ai_pos
        possible_moves = self.game.get_valid_moves(self.game.ai_pos)
        
        if len(possible_moves) == 0:
            return best_move

        for m in possible_moves:
            # try the move
            old_pos = self.game.ai_pos
            self.game.ai_pos = m
            
            # call minimax
            score = self.minimax(self.max_depth - 1, -999999, 999999, False)
            
            # undo the move
            self.game.ai_pos = old_pos
            
            if score > best_score:
                best_score = score
                best_move = m
                
        return best_move

    def minimax(self, depth, alpha, beta, is_maximizing):
        # base case
        if depth == 0 or self.game.game_over:
            return self.evaluate()

        if is_maximizing:
            max_eval = -999999
            for m in self.game.get_valid_moves(self.game.ai_pos):
                old_pos = self.game.ai_pos
                self.game.ai_pos = m
                
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.game.ai_pos = old_pos
                
                if eval > max_eval:
                    max_eval = eval
                if eval > alpha:
                    alpha = eval
                    
                if beta <= alpha:
                    break # prune
            return max_eval
        else:
            min_eval = 999999
            for m in self.game.get_valid_moves(self.game.player_pos):
                old_pos = self.game.player_pos
                self.game.player_pos = m
                
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.game.player_pos = old_pos
                
                if eval < min_eval:
                    min_eval = eval
                if eval < beta:
                    beta = eval
                    
                if beta <= alpha:
                    break # prune
            return min_eval
