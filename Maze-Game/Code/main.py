import pygame
import sys
import copy
import os
import math

import maze_gen
import game_engine
import agents
import csp_module

# Pygame Setup Constants
TILE_SIZE = 24  # Reduced from 40 to ensure the board fits on standard laptop screens
FPS = 30

# Colors
COLOR_BG = (20, 20, 20)
COLOR_WALL = (50, 50, 150)
COLOR_OPEN = (200, 200, 200)
COLOR_PLAYER = (0, 255, 0)
COLOR_AI = (0, 255, 255)
COLOR_MONSTER = (255, 0, 0)
COLOR_COIN = (255, 215, 0)
COLOR_EXIT = (255, 0, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_HOVER = (100, 255, 100)

class GameApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 36, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)
        
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("AURA MAZE")
        self.clock = pygame.time.Clock()
        
        self.state = "MENU"
        self.maze_width = 15
        self.maze_height = 10  # Reduced height so that 2*10+1 = 21 tiles fit perfectly
        self.game = None
        self.ai_player = None
        self.monster = None
        self.menu_rects = []
        self.load_assets()
        
    def load_assets(self):
        self.assets = {}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "Assets")
        try:
            self.assets['player'] = pygame.transform.scale(pygame.image.load(os.path.join(assets_dir, "player.png")), (TILE_SIZE - 4, TILE_SIZE - 4))
            self.assets['ai'] = pygame.transform.scale(pygame.image.load(os.path.join(assets_dir, "robot.jpg")), (TILE_SIZE - 4, TILE_SIZE - 4))
            self.assets['monster'] = pygame.transform.scale(pygame.image.load(os.path.join(assets_dir, "monster.png")), (TILE_SIZE - 4, TILE_SIZE - 4))
            self.assets['exit'] = pygame.transform.scale(pygame.image.load(os.path.join(assets_dir, "exit.png")), (TILE_SIZE, TILE_SIZE))
            self.assets['coin'] = pygame.transform.scale(pygame.image.load(os.path.join(assets_dir, "coin.jpg")), (TILE_SIZE//2, TILE_SIZE//2))
        except Exception as e:
            print("Error loading assets:", e)

    def start_game(self):
        generator = maze_gen.MazeGenerator(self.maze_width, self.maze_height)
        generator.generate_dfs()
        
        self.game = game_engine.GameState(generator.grid)
        self.game.exits = [(1, 0), (self.game.rows - 2, self.game.cols - 1)]
        for r, c in self.game.exits:
            self.game.grid[r][c] = 0
            
        placer = csp_module.CSPCoinPlacer(self.game, num_coins=15, min_dist=3)
        placer.place_coins()
        
        self.ai_player = agents.AIPlayer(self.game, depth=3)
        self.monster = agents.MonsterAgent(self.game)
        self.game.log_event("System Initialized.")
        
        self.screen_width = self.game.cols * TILE_SIZE + 250
        self.screen_height = max(self.game.rows * TILE_SIZE, 400)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.state = "PLAYING"

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == "MENU":
                    self.handle_menu_events(event)
                elif self.state == "INSTRUCTIONS":
                    self.handle_instructions_events(event)
                elif self.state == "PLAYING":
                    self.handle_playing_events(event)
                elif self.state == "GAME_OVER":
                    self.handle_game_over_events(event)
                    
            self.screen.fill(COLOR_BG)
            
            if self.state == "MENU":
                self.draw_3d_background()
                self.draw_menu()
            elif self.state == "INSTRUCTIONS":
                self.draw_3d_background()
                self.draw_instructions()
            elif self.state == "PLAYING":
                self.draw_playing()
            elif self.state == "GAME_OVER":
                self.draw_playing() # Draw game behind overlay
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

    def handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.start_game()
            elif event.key == pygame.K_2:
                self.state = "INSTRUCTIONS"
            elif event.key == pygame.K_3 or event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    if i == 0:
                        self.start_game()
                    elif i == 1:
                        self.state = "INSTRUCTIONS"
                    elif i == 2:
                        pygame.quit()
                        sys.exit()

    def handle_instructions_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self.state = "MENU"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.state = "MENU" # click anywhere to return

    def handle_playing_events(self, event):
        if event.type == pygame.KEYDOWN and not self.game.game_over:
            moved = False
            dr, dc = 0, 0
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                dr, dc = -1, 0
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                dr, dc = 1, 0
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                dr, dc = 0, -1
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                dr, dc = 0, 1
                
            if dr != 0 or dc != 0:
                new_pos = (self.game.player_pos[0] + dr, self.game.player_pos[1] + dc)
                if self.game.move_player(new_pos):
                    moved = True
                    
            if moved and not self.game.game_over:
                self.game.move_ai(self.ai_player.get_best_move())
                self.game.move_monster(self.monster.get_next_move())
                self.game.advance_turn()
                
            if self.game.game_over:
                self.state = "GAME_OVER"

    def handle_game_over_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = "MENU"
                self.screen_width = 800
                self.screen_height = 600
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if hasattr(self, 'game_over_rects'):
                for i, rect in enumerate(self.game_over_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0:
                            self.start_game()
                        elif i == 1:
                            self.state = "MENU"
                            self.screen_width = 800
                            self.screen_height = 600
                            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def draw_3d_background(self):
        import random
        if not hasattr(self, 'stars'):
            self.stars = []
            for _ in range(150):
                # x, y, z
                self.stars.append([random.uniform(-self.screen_width, self.screen_width),
                                   random.uniform(-self.screen_height, self.screen_height),
                                   random.uniform(0.1, 2.0)])
                                   
        cx = self.screen_width / 2
        cy = self.screen_height / 2
        
        for star in self.stars:
            # Move star closer (decrease Z)
            star[2] -= 0.015
            if star[2] <= 0:
                star[0] = random.uniform(-self.screen_width, self.screen_width)
                star[1] = random.uniform(-self.screen_height, self.screen_height)
                star[2] = 2.0
                
            # 3D projection
            px = int(cx + (star[0] / star[2]))
            py = int(cy + (star[1] / star[2]))
            
            # Draw if on screen
            if 0 <= px < self.screen_width and 0 <= py < self.screen_height:
                size = max(1, int(3.0 / star[2]))
                shade = max(50, min(255, int(255 * (1.0 - (star[2] / 2.0)))))
                color = (0, shade, int(shade * 0.8)) # Cyan/blue tint matching AI Aura
                pygame.draw.circle(self.screen, color, (px, py), size)

    def draw_menu(self):
        time_ms = pygame.time.get_ticks()
        
        # 3D Smooth Title Transition (sine wave bouncing and shadow depth)
        title_text = "AURA MAZE"
        base_color = COLOR_AI
        # Create a pulsating depth effect
        depth = 5 + int(3 * math.sin(time_ms / 300.0))
        
        for i in range(depth, 0, -1):
            shadow = self.font_title.render(title_text, True, (20, 100, 150))
            self.screen.blit(shadow, (self.screen_width//2 - shadow.get_width()//2 + i, 100 + i))
            
        title = self.font_title.render(title_text, True, base_color)
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        
        opts = [
            "Play Game",
            "Instructions",
            "Exit"
        ]
        
        self.menu_rects = []
        mouse_pos = pygame.mouse.get_pos()
        y = 250
        for opt in opts:
            # First, compute standard rect for collision
            text_surf_temp = self.font_large.render(opt, True, COLOR_TEXT)
            rect = text_surf_temp.get_rect(center=(self.screen_width//2, y + text_surf_temp.get_height()//2))
            
            is_hovered = rect.collidepoint(mouse_pos)
            color = COLOR_HOVER if is_hovered else COLOR_TEXT
            
            # Smooth scaling effect on hover
            if is_hovered:
                scale_factor = 1.1 + 0.02 * math.sin(time_ms / 150.0)
                font_hover = pygame.font.SysFont("Arial", int(36 * scale_factor), bold=True)
                text = font_hover.render(opt, True, color)
            else:
                text = self.font_large.render(opt, True, color)
                
            draw_rect = text.get_rect(center=(self.screen_width//2, y + 20))
            self.screen.blit(text, draw_rect)
            self.menu_rects.append(rect)
            y += 70
            
        footer = self.font.render("Click an option or press 1, 2, 3", True, COLOR_OPEN)
        self.screen.blit(footer, (self.screen_width//2 - footer.get_width()//2, 480))

    def draw_instructions(self):
        title = self.font_title.render("INSTRUCTIONS", True, COLOR_AI)
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
        instructions = [
            "Use Arrow Keys or WASD to move.",
            "Collect coins to increase your score.",
            "Avoid the Monster (-3 coins if caught).",
            "Compete against the AI agent.",
            "Exits unlock after 15 turns.",
            "Reach the exit first to win!"
        ]
        
        y = 150
        for line in instructions:
            text = self.font_large.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, y))
            y += 50
            
        footer = self.font.render("Click anywhere or press ESC to return to Menu", True, COLOR_OPEN)
        self.screen.blit(footer, (self.screen_width//2 - footer.get_width()//2, 500))

    def draw_playing(self):
        # Draw Grid
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.game.grid[r][c] == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_OPEN, rect)
                    
        # Draw Coins
        for r, c in self.game.coins:
            if 'coin' in self.assets:
                self.screen.blit(self.assets['coin'], (c * TILE_SIZE + TILE_SIZE//4, r * TILE_SIZE + TILE_SIZE//4))
            else:
                pygame.draw.circle(self.screen, COLOR_COIN, (c * TILE_SIZE + TILE_SIZE//2, r * TILE_SIZE + TILE_SIZE//2), TILE_SIZE//4)
            
        # Draw Exits
        if self.game.exits_unlocked:
            for r, c in self.game.exits:
                if 'exit' in self.assets:
                    self.screen.blit(self.assets['exit'], (c * TILE_SIZE, r * TILE_SIZE))
                else:
                    pygame.draw.rect(self.screen, COLOR_EXIT, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
        # Draw Agents
        pr, pc = self.game.player_pos
        if 'player' in self.assets:
            self.screen.blit(self.assets['player'], (pc * TILE_SIZE + 2, pr * TILE_SIZE + 2))
        else:
            pygame.draw.rect(self.screen, COLOR_PLAYER, (pc * TILE_SIZE + 5, pr * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10))
        
        ar, ac = self.game.ai_pos
        if 'ai' in self.assets:
            self.screen.blit(self.assets['ai'], (ac * TILE_SIZE + 2, ar * TILE_SIZE + 2))
        else:
            pygame.draw.rect(self.screen, COLOR_AI, (ac * TILE_SIZE + 5, ar * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10))
        
        mr, mc = self.game.monster_pos
        if 'monster' in self.assets:
            self.screen.blit(self.assets['monster'], (mc * TILE_SIZE + 2, mr * TILE_SIZE + 2))
        else:
            pygame.draw.circle(self.screen, COLOR_MONSTER, (mc * TILE_SIZE + TILE_SIZE//2, mr * TILE_SIZE + TILE_SIZE//2), TILE_SIZE//2 - 5)
        
        # Draw Sidebar
        sidebar_x = self.game.cols * TILE_SIZE + 20
        
        texts = [
            f"Player Score: {self.game.player_score}",
            f"AI Score: {self.game.ai_score}",
            f"Turn: {self.game.turn} / 15",
            f"Exits Unlocked: {self.game.exits_unlocked}",
            "-" * 20,
            "Logs:"
        ]
        
        y_offset = 20
        for t in texts:
            surf = self.font.render(t, True, COLOR_TEXT)
            self.screen.blit(surf, (sidebar_x, y_offset))
            y_offset += 30
            
        for log in reversed(self.game.logs[-5:]):
            surf = self.font.render(log, True, (150, 150, 150))
            self.screen.blit(surf, (sidebar_x, y_offset))
            y_offset += 25

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.game.winner:
            msg = f"{self.game.winner} Won!"
            color = COLOR_PLAYER if self.game.winner == "Player" else COLOR_AI
        else:
            msg = "GAME OVER!"
            color = COLOR_MONSTER
            
        title = self.font_title.render(msg, True, color)
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, self.screen_height//2 - 120))
        
        info = self.font_large.render(f"Final Score - Player: {self.game.player_score} | AI: {self.game.ai_score}", True, COLOR_TEXT)
        self.screen.blit(info, (self.screen_width//2 - info.get_width()//2, self.screen_height//2 - 40))
        
        opts = ["Play Again", "Main Menu"]
        self.game_over_rects = []
        mouse_pos = pygame.mouse.get_pos()
        y = self.screen_height//2 + 40
        
        time_ms = pygame.time.get_ticks()
        
        for opt in opts:
            text_surf_temp = self.font_large.render(opt, True, COLOR_TEXT)
            rect = text_surf_temp.get_rect(center=(self.screen_width//2, y + text_surf_temp.get_height()//2))
            
            is_hovered = rect.collidepoint(mouse_pos)
            color = COLOR_HOVER if is_hovered else COLOR_TEXT
            
            if is_hovered:
                scale_factor = 1.1 + 0.02 * math.sin(time_ms / 150.0)
                font_hover = pygame.font.SysFont("Arial", int(36 * scale_factor), bold=True)
                text = font_hover.render(opt, True, color)
            else:
                text = self.font_large.render(opt, True, color)
                
            draw_rect = text.get_rect(center=(self.screen_width//2, y + 20))
            self.screen.blit(text, draw_rect)
            self.game_over_rects.append(rect)
            y += 60
            
        footer = self.font.render("Press ENTER to Play Again or ESC for Menu", True, COLOR_OPEN)
        self.screen.blit(footer, (self.screen_width//2 - footer.get_width()//2, y + 20))

if __name__ == "__main__":
    app = GameApp()
    app.run()
