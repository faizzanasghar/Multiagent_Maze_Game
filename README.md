# AURA MAZE: Elite Multi-Agent System 🌌

Welcome to **Aura Maze**, a stunning, web-based artificial intelligence project developed for the National University of Computer & Emerging Sciences (NUCES), Faisalabad-Chiniot Campus.

This project demonstrates complex multi-agent pathfinding, adversarial decision-making, constraint satisfaction, and procedural generation—all wrapped in a highly polished, responsive **Glassmorphism Web Application**.

---

## ✨ Features

- **Procedural Generation:** The maze layout is uniquely generated every game using a randomized Depth-First Search (DFS) algorithm.
- **Minimax AI Agent (Alpha-Beta Pruning):** The main opponent intelligently calculates its moves several turns ahead to collect coins and block the player, optimizing its decision tree with Alpha-Beta pruning to save processing time.
- **A* Pathfinding (Monster):** A relentless secondary AI uses the A* Search Algorithm combined with True-Distance BFS heuristics to hunt down whichever entity (Player or AI) is currently winning.
- **Constraint Satisfaction Problem (CSP):** The environment utilizes CSP logic to intelligently spawn high-value gold coins dynamically, ensuring they are out of immediate reach of all agents upon spawn.
- **Elite Web Interface:** Powered by Python/Flask on the backend and HTML5 Canvas/CSS Glassmorphism on the frontend, featuring live analytics, smooth entity interpolation (lerp), and real-time event logging.

---

## 🛠️ Technology Stack

- **Backend Logic:** Pure Python 3
- **Web Server:** Flask (REST API)
- **Frontend Engine:** HTML5 Canvas & Vanilla JavaScript (60 FPS Render Loop)
- **Styling:** Vanilla CSS (Glassmorphism, CSS Grid/Flexbox)

---

## 🚀 How to Run the Project

### 1. Prerequisites
Ensure you have Python 3 installed on your machine. You will also need the `Flask` library to run the web server.

```bash
pip install flask
```

### 2. Start the Server
Navigate to the `Code` directory containing `app.py` and run the application:

```bash
cd Maze-Game/Code
python app.py
```

### 3. Play the Game
Once the terminal indicates the server is running, open your favorite web browser (Chrome, Edge, Firefox) and go to:

👉 **http://localhost:5000**

- Click **GENERATE** to build the maze geometry.
- Click **START** to drop the AI, Player, Monster, and Coins into the arena.
- Use **WASD** or **Arrow Keys** to move.
- Collect coins to increase your score, avoid the Monster, and reach the glowing purple exit before the Minimax AI does!

---

## 📊 Analytics & Live Data

The web dashboard provides a real-time glimpse into the "brain" of the AI. On the right-side panel, you can monitor:
- **Nodes Evaluated:** How many future possibilities the Minimax algorithm calculated this turn.
- **Alpha-Beta Prunes:** How many bad branches of the decision tree the AI successfully ignored to save processing power.
- **Live Event Logs:** A scrolling feed tracking every coin grab, monster attack, and door unlock.

---

## 👥 Authors / University Context

**Course:** Final Project 4A1  
**Institution:** NUCES Faisalabad-Chiniot Campus  
This project was designed to showcase the practical implementation of core Artificial Intelligence search algorithms (Minimax, A*, BFS, DFS, CSP) in an interactive, highly competitive environment.
