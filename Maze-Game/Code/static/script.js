const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let gameState = null;
let cell_size = 34.66;

const visPos = { player: null, ai: null, monster: null };
const assets = { player: new Image(), ai: new Image(), monster: new Image(), coin: new Image(), exit: new Image() };

assets.player.src = '/static/assets/player.png';
assets.ai.src = '/static/assets/robot.jpg';
assets.monster.src = '/static/assets/monster.png';
assets.coin.src = '/static/assets/coin.jpg';
assets.exit.src = '/static/assets/exit.png';

async function fetchPost(url, data={}) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return await res.json();
}

document.getElementById('btn-generate').onclick = async () => {
    gameState = await fetchPost('/api/generate');
    cell_size = 520 / gameState.grid[0].length;
    document.getElementById('winner-overlay').classList.add('hidden');
};

document.getElementById('btn-start').onclick = async () => {
    gameState = await fetchPost('/api/start');
    if (gameState.error) return alert(gameState.error);
    visPos.player = [...gameState.player];
    visPos.ai = [...gameState.ai];
    visPos.monster = [...gameState.monster];
    updateUI();
};

window.addEventListener('keydown', async (e) => {
    if (!gameState || !gameState.player || gameState.game_over) return;
    const moves = {
        'ArrowUp': [-1, 0], 'w': [-1, 0],
        'ArrowDown': [1, 0], 's': [1, 0],
        'ArrowLeft': [0, -1], 'a': [0, -1],
        'ArrowRight': [0, 1], 'd': [0, 1]
    };
    if (moves[e.key]) {
        e.preventDefault();
        gameState = await fetchPost('/api/move', {dr: moves[e.key][0], dc: moves[e.key][1]});
        updateUI();
    }
});

function updateUI() {
    if (!gameState) return;
    if (gameState.player_score !== undefined) {
        document.getElementById('score-player').innerText = gameState.player_score;
        document.getElementById('score-ai').innerText = gameState.ai_score;
        document.getElementById('turn-count').innerText = gameState.turn;
        document.getElementById('turn-progress').style.width = Math.min(100, (gameState.turn / 15) * 100) + '%';
        
        const exitStatus = document.getElementById('exit-status');
        if (gameState.exits_unlocked) {
            exitStatus.innerText = 'EXITS OPEN!';
            exitStatus.className = 'status-msg text-purple';
        } else {
            exitStatus.innerText = 'Exits locked';
            exitStatus.className = 'status-msg text-dim';
        }
        
        document.getElementById('stat-nodes').innerText = gameState.analytics.nodes;
        document.getElementById('stat-prunes').innerText = gameState.analytics.prunes;
        document.getElementById('stat-coins').innerText = gameState.coins.length;
        
        const logsContainer = document.getElementById('log-container');
        logsContainer.innerHTML = '';
        gameState.logs.forEach(log => {
            const div = document.createElement('div');
            let colorClass = 'text-dim';
            if (log.includes('You') || log.includes('Player')) colorClass = 'text-cyan';
            else if (log.includes('AI')) colorClass = 'text-green';
            else if (log.includes('Monster')) colorClass = 'text-red';
            else if (log.includes('Exit') || log.includes('UNLOCKED')) colorClass = 'text-purple';
            
            div.className = `log-entry ${colorClass}`;
            div.innerText = log;
            logsContainer.prepend(div);
        });
        
        if (gameState.game_over) {
            const overlay = document.getElementById('winner-overlay');
            overlay.classList.remove('hidden');
            let winnerTitle = document.getElementById('winner-title');
            winnerTitle.innerText = gameState.winner === 'Player' ? 'YOU WIN!' : gameState.winner + ' WINS!';
            winnerTitle.className = gameState.winner === 'Player' ? 'text-cyan' : (gameState.winner === 'AI' ? 'text-green' : 'text-red');
        }
    }
}

function lerp(current, target, t=0.2) {
    return [current[0] + (target[0] - current[0]) * t, current[1] + (target[1] - current[1]) * t];
}

function renderLoop() {
    if (!gameState || !gameState.grid) {
        requestAnimationFrame(renderLoop);
        return;
    }
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const grid = gameState.grid;
    
    // Draw Grid
    for(let r=0; r<grid.length; r++) {
        for(let c=0; c<grid[0].length; c++) {
            if (grid[r][c] === 1) {
                ctx.fillStyle = '#1e293b';
                ctx.fillRect(c * cell_size, r * cell_size, cell_size + 0.5, cell_size + 0.5);
            } else {
                ctx.fillStyle = (r+c)%2===0 ? '#0f172a' : '#162032';
                ctx.fillRect(c * cell_size, r * cell_size, cell_size + 0.5, cell_size + 0.5);
            }
        }
    }
    
    if (gameState.player) {
        // Draw Exits
        gameState.exits.forEach(([er, ec]) => {
            ctx.drawImage(assets.exit, ec*cell_size+2, er*cell_size+2, cell_size-4, cell_size-4);
        });
        
        // Draw Coins
        gameState.coins.forEach(([cr, cc]) => {
            ctx.drawImage(assets.coin, cc*cell_size+4, cr*cell_size+4, cell_size-8, cell_size-8);
        });
        
        // Lerp characters
        visPos.player = lerp(visPos.player, gameState.player);
        visPos.ai = lerp(visPos.ai, gameState.ai);
        visPos.monster = lerp(visPos.monster, gameState.monster);
        
        // Draw Glows & Characters
        const drawChar = (pos, img, color) => {
            if (!pos) return;
            const x = pos[1] * cell_size;
            const y = pos[0] * cell_size;
            
            // Glow
            ctx.beginPath();
            ctx.arc(x + cell_size/2, y + cell_size/2, cell_size/2, 0, 2*Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            
            ctx.drawImage(img, x+2, y+2, cell_size-4, cell_size-4);
        };
        
        drawChar(visPos.player, assets.player, 'rgba(6, 182, 212, 0.4)');
        drawChar(visPos.ai, assets.ai, 'rgba(34, 197, 94, 0.4)');
        drawChar(visPos.monster, assets.monster, 'rgba(239, 68, 68, 0.4)');
    }
    
    requestAnimationFrame(renderLoop);
}

// Start render loop
requestAnimationFrame(renderLoop);
