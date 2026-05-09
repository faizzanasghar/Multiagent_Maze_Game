import random

class CSPCoinPlacer:
    def __init__(self, game_state, num_coins=15, min_dist=3):
        self.game_state = game_state
        self.num_coins = num_coins
        self.min_dist = min_dist
        self.empty_cells = self._get_empty_cells()

    def _get_empty_cells(self):
        cells = []
        for r in range(self.game_state.rows):
            for c in range(self.game_state.cols):
                if self.game_state.grid[r][c] == 0:
                    # Exclude start/end positions of agents
                    pos = (r, c)
                    if pos != self.game_state.player_pos and \
                       pos != self.game_state.ai_pos and \
                       pos != self.game_state.monster_pos:
                        cells.append(pos)
        return cells

    def is_consistent(self, pos, current_coins):
        # Distance constraint
        for coin in current_coins:
            dist = abs(pos[0] - coin[0]) + abs(pos[1] - coin[1])
            if dist < self.min_dist:
                return False
        
        # Quadrant constraint (optional but helps "spread")
        # Let's just stick to distance for now as it's easier to satisfy
        return True

    def place_coins(self):
        random.shuffle(self.empty_cells)
        coins = []
        
        def backtrack(index):
            if len(coins) == self.num_coins:
                return True
            
            for i in range(index, len(self.empty_cells)):
                pos = self.empty_cells[i]
                if self.is_consistent(pos, coins):
                    coins.append(pos)
                    if backtrack(i + 1):
                        return True
                    coins.pop()
            return False

        if backtrack(0):
            self.game_state.coins = set(coins)
            return True
        return False
