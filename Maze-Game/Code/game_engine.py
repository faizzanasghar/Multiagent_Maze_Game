import copy

class GameState:
    def __init__(self, grid):
        # copy grid so we dont mess up original
        self.grid = copy.deepcopy(grid)
        self.rows = len(grid)
        self.cols = len(grid[0])

        # initial positions for everyone in corners
        self.player_pos = (1, 1)                          
        self.ai_pos = (self.rows - 2, self.cols - 2)      
        self.monster_pos = (self.rows - 2, 1)             

        self.player_score = 0
        self.ai_score = 0
        self.turn = 0
        self.coins = set()
        self.exits = []
        self.exits_unlocked = False

        # game status variables
        self.game_over = False
        self.winner = None
        self.message = ""
        self.logs = []

    def get_valid_moves(self, pos):
        r, c = pos
        moves = []
        # up down left right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            # check bounds
            if nr >= 0 and nr < self.rows and nc >= 0 and nc < self.cols:
                if self.grid[nr][nc] == 0:
                    moves.append((nr, nc))
        return moves

    def log_event(self, msg):
        self.logs.append(msg)
        # keep log short
        if len(self.logs) > 50:
            self.logs.pop(0)

    def move_player(self, new_pos):
        if new_pos in self.get_valid_moves(self.player_pos):
            self.player_pos = new_pos
            self.check_coin(new_pos, False)
            self.check_exit(new_pos, False)
            return True
        return False

    def move_ai(self, new_pos):
        if new_pos in self.get_valid_moves(self.ai_pos):
            self.ai_pos = new_pos
            self.check_coin(new_pos, True)
            self.check_exit(new_pos, True)
            return True
        return False

    def move_monster(self, new_pos):
        if new_pos in self.get_valid_moves(self.monster_pos):
            self.monster_pos = new_pos
            self.check_monster()
            return True
        return False

    def check_coin(self, pos, is_ai):
        # pick up coin if its there
        if pos in self.coins:
            self.coins.remove(pos)
            if is_ai == True:
                self.ai_score += 1
                self.log_event(f"AI got a coin! ({self.ai_score})")
            else:
                self.player_score += 1
                self.log_event(f"You got a coin! ({self.player_score})")

    def check_exit(self, pos, is_ai):
        # see if someone won
        if self.exits_unlocked and pos in self.exits:
            self.game_over = True
            if is_ai:
                self.winner = "AI"
                self.message = "AI escaped!"
            else:
                self.winner = "Player"
                self.message = "Player escaped!"

    def check_monster(self):
        # minus 3 coins if caught
        if self.monster_pos == self.player_pos:
            self.player_score -= 3
            if self.player_score < 0:
                self.player_score = 0
            self.log_event("Monster got you! Lost 3 coins.")
            
        elif self.monster_pos == self.ai_pos:
            self.ai_score -= 3
            if self.ai_score < 0:
                self.ai_score = 0
            self.log_event("Monster got the AI! Lost 3 coins.")

    def advance_turn(self):
        self.turn += 1
        # unlock exits at 15
        if self.turn >= 15 and self.exits_unlocked == False:
            self.exits_unlocked = True
            self.log_event("Exits are open now!")
