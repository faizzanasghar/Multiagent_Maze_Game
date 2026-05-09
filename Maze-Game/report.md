# Intelligent Multi-Agent Maze Game Report

## 1. Project Overview
This project implements a turn-based AI maze game featuring multiple search algorithms for maze generation, pathfinding, and decision making.

## 2. Maze Generation Algorithms
We implemented three primary algorithms:
- **DFS (Recursive Backtracking)**: Produces long, winding corridors with fewer branches. Ideal for "classic" maze feel.
- **BFS-Based**: Produces a more open structure. Due to its layer-by-layer expansion, it often results in more direct paths between distant points.
- **Prim's Algorithm**: Produces a balanced maze with a high number of short branches (dead ends), creating a complex, textured structure.

### Comparison Table
| Algorithm | Avg Path Length | Avg Dead Ends | Characteristic |
|-----------|-----------------|---------------|----------------|
| DFS       | ~180            | ~25           | Long corridors |
| BFS       | ~56             | ~24           | Open, direct   |
| Prim      | ~60             | ~71           | Highly branched|

**Recommendation**: DFS-based generation is recommended for the best gameplay experience as it provides challenging navigation and long corridors.

## 3. Game Design & AI Agents
### AI Player (Minimax + Alpha-Beta)
The AI player uses a depth-limited Minimax algorithm with Alpha-Beta pruning to decide its moves.
- **Evaluation Function**: `Score = (AI coins - Human coins) * 10 - distance_to_exit - (5 - distance_to_monster) * 20`
- **Depth**: 3-4 (adjustable).

### Monster Agent (A*)
The monster uses A* pathfinding with a Manhattan distance heuristic to target the player with the higher current score.
- **Behavior**: Moves every turn, terminating the game if it captures an agent.

## 4. Constraint Satisfaction Problem (CSP)
Coins are placed using a CSP approach to ensure:
- No coins on walls or agent start positions.
- Minimum distance of 4 units between any two coins.
- Optimal distribution across the available path cells.

## 5. Exit System
Two exits are placed at the boundaries of the maze. They remain locked for the first 15 turns to encourage coin collection and tactical movement.

## 6. Visualization
The game uses **Tkinter** and **PIL** for rendering. Features include:
- Real-time animation of maze carving.
- Color-coded agents and items.
- Turn and score tracking.

## 7. Analysis & Conclusion
The integration of adversarial search (Minimax) and pathfinding (A*) creates a dynamic environment where the player must balance risk (monster) and reward (coins/exit). The CSP-based placement ensures that every game is fair and requires exploration.
