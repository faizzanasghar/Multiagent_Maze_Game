from flask import Flask, render_template, jsonify, request
import maze_gen
import game_engine
import agents
import csp_module

app = Flask(__name__)

class GameManager:
    def __init__(self):
        self.game = None
        self.generator = None
        self.ai_player = None
        self.monster = None

gm = GameManager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json or {}
    w = data.get("width", 7)
    h = data.get("height", 7)
    gm.generator = maze_gen.MazeGenerator(w, h)
    gm.generator.generate_dfs()
    return jsonify({"status": "success", "grid": gm.generator.grid})

@app.route("/api/start", methods=["POST"])
def start():
    if not gm.generator:
        return jsonify({"error": "Generate first"})
    gm.game = game_engine.GameState(gm.generator.grid)
    gm.game.exits = [(1, 0), (gm.game.rows - 2, gm.game.cols - 1)]
    for r, c in gm.game.exits:
        gm.game.grid[r][c] = 0
        
    placer = csp_module.CSPCoinPlacer(gm.game, num_coins=15, min_dist=3)
    placer.place_coins()
    
    gm.ai_player = agents.AIPlayer(gm.game, depth=3)
    gm.monster = agents.MonsterAgent(gm.game)
    gm.game.log_event("System Initialized. AURA MAZE Web Edition.")
    return get_state()

def get_state():
    if not gm.game:
        return jsonify({"status": "error", "message": "Game not started"})
    
    return jsonify({
        "status": "success",
        "grid": gm.game.grid,
        "player": gm.game.player_pos,
        "ai": gm.game.ai_pos,
        "monster": gm.game.monster_pos,
        "coins": list(gm.game.coins),
        "exits": gm.game.exits,
        "player_score": gm.game.player_score,
        "ai_score": gm.game.ai_score,
        "turn": gm.game.turn,
        "exits_unlocked": gm.game.exits_unlocked,
        "game_over": gm.game.game_over,
        "winner": gm.game.winner,
        "logs": gm.game.logs,
        "analytics": {
            "nodes": getattr(gm.ai_player, 'nodes', 0) if gm.ai_player else 0,
            "prunes": getattr(gm.ai_player, 'prunes', 0) if gm.ai_player else 0
        }
    })

@app.route("/api/move", methods=["POST"])
def move():
    if not gm.game or gm.game.game_over:
        return get_state()
    
    data = request.json
    dr = data.get("dr", 0)
    dc = data.get("dc", 0)
    
    if dr != 0 or dc != 0:
        new_pos = (gm.game.player_pos[0] + dr, gm.game.player_pos[1] + dc)
        if gm.game.move_player(new_pos):
            if not gm.game.game_over:
                gm.game.move_ai(gm.ai_player.get_best_move())
                gm.game.move_monster(gm.monster.get_next_move())
                gm.game.advance_turn()
                
    return get_state()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
