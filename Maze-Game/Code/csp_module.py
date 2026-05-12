import random

class CSPCoinPlacer:
    def __init__(self, game_state, num_coins=15, min_dist=3):
        self.game_state = game_state
        self.num_coins = num_coins
        self.min_dist = min_dist
        self.empty_cells = self.get_empty_cells()

    def get_empty_cells(self):
        cells = []
        for r in range(self.game_state.rows):
            for c in range(self.game_state.cols):
                if self.game_state.grid[r][c] == 0:
                    pos = (r, c)
                    # dont place on players
                    if pos != self.game_state.player_pos and pos != self.game_state.ai_pos and pos != self.game_state.monster_pos:
                        cells.append(pos)
        return cells

    def check_constraints(self, pos, current_coins):
        # check if it is far enough from other coins
        for coin in current_coins:
            dist = abs(pos[0] - coin[0]) + abs(pos[1] - coin[1])
            if dist < self.min_dist:
                return False
        return True

    def place_coins(self):
        random.shuffle(self.empty_cells)
        coins = []
        
        def solve(index):
            if len(coins) == self.num_coins:
                return True
            
            for i in range(index, len(self.empty_cells)):
                pos = self.empty_cells[i]
                if self.check_constraints(pos, coins):
                    coins.append(pos)
                    # recursive call
                    if solve(i + 1):
                        return True
                    coins.pop() # backtrack
            return False

        if solve(0):
            self.game_state.coins = set(coins)
            return True
        return False
