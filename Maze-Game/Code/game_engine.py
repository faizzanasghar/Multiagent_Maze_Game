"""
Game Engine Module
Manages game state, turn logic, scoring, and win/loss conditions.
"""
import copy


class GameState:
    def __init__(self, grid):
        self.grid = copy.deepcopy(grid)
        self.rows = len(grid)
        self.cols = len(grid[0])

        # Place agents at distinct corners
        self.player_pos = (1, 1)                          # Top-left
        self.ai_pos = (self.rows - 2, self.cols - 2)      # Bottom-right
        self.monster_pos = (self.rows - 2, 1)             # Bottom-left

        self.player_score = 0
        self.ai_score = 0
        self.turn = 0
        self.coins = set()
        self.exits = []
        self.exits_unlocked = False

        self.game_over = False
        self.winner = None
        self.message = ""
        self.logs = []

    def get_valid_moves(self, pos):
        r, c = pos
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] == 0:
                moves.append((nr, nc))
        return moves

    def log_event(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 50:
            self.logs.pop(0)

    def move_player(self, new_pos):
        if new_pos in self.get_valid_moves(self.player_pos):
            self.player_pos = new_pos
            self._check_coin(new_pos, is_ai=False)
            self._check_exit(new_pos, is_ai=False)
            return True
        return False

    def move_ai(self, new_pos):
        if new_pos in self.get_valid_moves(self.ai_pos):
            self.ai_pos = new_pos
            self._check_coin(new_pos, is_ai=True)
            self._check_exit(new_pos, is_ai=True)
            return True
        return False

    def move_monster(self, new_pos):
        if new_pos in self.get_valid_moves(self.monster_pos):
            self.monster_pos = new_pos
            self._check_monster_capture()
            return True
        return False

    def _check_coin(self, pos, is_ai):
        if pos in self.coins:
            self.coins.discard(pos)
            if is_ai:
                self.ai_score += 1
                self.log_event(f"AI collected a coin! ({self.ai_score})")
            else:
                self.player_score += 1
                self.log_event(f"You collected a coin! ({self.player_score})")

    def _check_exit(self, pos, is_ai):
        if self.exits_unlocked and pos in self.exits:
            self.game_over = True
            self.winner = "AI" if is_ai else "Player"
            self.message = f"{'AI' if is_ai else 'Player'} escaped through the exit!"

    def _check_monster_capture(self):
        if self.monster_pos == self.player_pos:
            self.player_score = max(0, self.player_score - 3)
            self.log_event("Monster caught you! -3 coins.")
        elif self.monster_pos == self.ai_pos:
            self.ai_score = max(0, self.ai_score - 3)
            self.log_event("Monster caught the AI! -3 coins.")

    def advance_turn(self):
        self.turn += 1
        if self.turn >= 15 and not self.exits_unlocked:
            self.exits_unlocked = True
            self.log_event("Exits have been UNLOCKED!")
