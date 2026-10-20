<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Khủng Long Chạy</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #222; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: Arial, sans-serif; }
#gameContainer {
    position: relative;
    width: 800px;
    height: 300px;
    overflow: hidden;
    border: 2px solid #555;
    background: linear-gradient(to bottom, #87CEEB 0%, #87CEEB 70%, #d2b48c 70%, #d2b48c 100%);
    transition: background 1s;
}
#sky { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
#player {
    position: absolute;
    bottom: 55px;
    left: 50px;
    width: 40px;
    height: 50px;
    z-index: 2;
    font-size: 40px;
    line-height: 50px;
    text-align: center;
    user-select: none;
}
#player.duck { height: 25px; font-size: 25px; line-height: 25px; bottom: 30px; }
.obstacle {
    position: absolute;
    bottom: 55px;
    z-index: 2;
    font-size: 40px;
    line-height: 50px;
    user-select: none;
}
.bird {
    position: absolute;
    z-index: 2;
    font-size: 30px;
    user-select: none;
}
#score { position: absolute; top: 10px; right: 10px; color: #333; font-size: 20px; font-weight: bold; z-index: 3; }
#gameOver {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 20px 30px;
    text-align: center;
    border-radius: 10px;
    display: none;
    z-index: 5;
}
#gameOver button {
    margin-top: 10px;
    padding: 8px 20px;
    font-size: 16px;
    cursor: pointer;
    border: none;
    border-radius: 5px;
    background: #4CAF50;
    color: white;
}
#gameOver button:hover { background: #45a049; }
#instruction { position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); color: #333; font-size: 12px; z-index: 3; }
</style>
</head>
<body>

<div id="gameContainer">
    <div id="sky"></div>
    <div id="score">0</div>
    <div id="player">🦖</div>
    <div id="instruction">Nhấn SPACE để nhảy | Nhấn ↓ để cúi | Tránh 🦖 🌵 🦅</div>
    <div id="gameOver">
        <h2>Game Over!</h2>
        <p id="finalScore"></p>
        <button onclick="restartGame()">Chơi lại</button>
    </div>
</div>

<script>
const container = document.getElementById('gameContainer');
const player = document.getElementById('player');
const scoreEl = document.getElementById('score');
const gameOverEl = document.getElementById('gameOver');
const finalScoreEl = document.getElementById('finalScore');

let score = 0;
let gameRunning = false;
let gameSpeed = 6;
let obstacles = [];
let birds = [];
let jumpVelocity = 0;
let isJumping = false;
let isDucking = false;
let playerY = 0;
let gravity = 0.8;
let groundLevel = 55;
let phase = 0; // 0: ngày, 1: đêm
let zone = 0; // 0: đồng cỏ, 1: sa mạc, 2: rừng, 3: biển
let zoneNames = ['Đồng cỏ', 'Sa mạc', 'Rừng Amazon', 'Biển'];
let lastZoneChange = 0;

// Tạo âm thanh bằng Web Audio API
let audioCtx;
try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
} catch(e) {
    audioCtx = null;
}

function playSound(type) {
    if (!audioCtx) return;
    const ctx = audioCtx;
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    if (type === 'jump') {
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(300, ctx.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.2, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.2);
    } else if (type === 'duck') {
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(200, ctx.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.15, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.15);
    } else if (type === 'score') {
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(800, ctx.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.1, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.1);
    } else if (type === 'gameOver') {
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(400, ctx.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(50, ctx.currentTime + 0.5);
        gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.8);
    }
}

// Cập nhật bầu trời (sáng/tối)
function updateSky() {
    const sky = document.getElementById('sky');
    if (phase === 0) {
        // Ngày
        if (zone === 0) sky.style.background = 'linear-gradient(to bottom, #87CEEB, #87CEEB)';
        else if (zone === 1) sky.style.background = 'linear-gradient(to bottom, #FFD700, #FFA500)';
        else if (zone === 2) sky.style.background = 'linear-gradient(to bottom, #228B22, #006400)';
        else if (zone === 3) sky.style.background = 'linear-gradient(to bottom, #00BFFF, #1E90FF)';
    } else {
        // Đêm
        if (zone === 0) sky.style.background = 'linear-gradient(to bottom, #1a1a2e, #0f3460)';
        else if (zone === 1) sky.style.background = 'linear-gradient(to bottom, #2d1b69, #1a1a2e)';
        else if (zone === 2) sky.style.background = 'linear-gradient(to bottom, #0b3d0b, #001a00)';
        else if (zone === 3) sky.style.background = 'linear-gradient(to bottom, #001f3f, #000033)';
    }
    // Đổi màu nền đất
    const ground = container.style;
    if (zone === 0) ground.background = (phase === 0) ? 'linear-gradient(to bottom, #87CEEB 0%, #87CEEB 70%, #d2b48c 70%, #d2b48c 100%)' : 'linear-gradient(to bottom, #1a1a2e 0%, #1a1a2e 70%, #4a4a2e 70%, #4a4a2e 100%)';
    else if (zone === 1) ground.background = (phase === 0) ? 'linear-gradient(to bottom, #FFD700 0%, #FFD700 70%, #DAA520 70%, #DAA520 100%)' : 'linear-gradient(to bottom, #2d1b69 0%, #2d1b69 70%, #5c4033 70%, #5c4033 100%)';
    else if (zone === 2) ground.background = (phase === 0) ? 'linear-gradient(to bottom, #228B22 0%, #228B22 70%, #8B4513 70%, #8B4513 100%)' : 'linear-gradient(to bottom, #0b3d0b 0%, #0b3d0b 70%, #3d2b1f 70%, #3d2b1f 100%)';
    else if (zone === 3) ground.background = (phase === 0) ? 'linear-gradient(to bottom, #00BFFF 0%, #00BFFF 70%, #FFD700 70%, #FFD700 100%)' : 'linear-gradient(to bottom, #001f3f 0%, #001f3f 70%, #1a1a5e 70%, #1a1a5e 100%)';
}

// Tạo vật cản
function spawnObstacle() {
    const type = Math.random();
    if (type < 0.4) {
        // Khủng long chạy ngang (hình ảnh khủng long)
        const dino = document.createElement('div');
        dino.className = 'obstacle';
        dino.textContent = '🦖';
        dino.style.left = '800px';
        container.appendChild(dino);
        obstacles.push(dino);
    } else if (type < 0.7) {
        // Cây xương rồng
        const cactus = document.createElement('div');
        cactus.className = 'obstacle';
        cactus.textContent = '🌵';
        cactus.style.left = '800px';
        container.appendChild(cactus);
        obstacles.push(cactus);
    } else {
        // Chim bay chéo
        const bird = document.createElement('div');
        bird.className = 'bird';
        bird.textContent = '🦅';
        bird.style.left = '800px';
        bird.style.bottom = (Math.random() * 60 + 80) + 'px';
        const vy = (Math.random() * 0.5 - 0.25);
        bird.dataset.vy = vy;
        container.appendChild(bird);
        birds.push(bird);
    }
}

// Game loop
function gameLoop() {
    if (!gameRunning) return;
    
    // Cập nhật score
    score += 1;
    scoreEl.textContent = score;
    
    // Kiểm tra đổi bầu trời (500 điểm)
    const newPhase = Math.floor(score / 500) % 2;
    if (newPhase !== phase) {
        phase = newPhase;
        updateSky();
        playSound('score');
    }
    
    // Kiểm tra đổi khu vực (2000 điểm)
    const newZone = Math.floor(score / 2000) % 4;
    if (newZone !== zone) {
        zone = newZone;
        updateSky();
        playSound('score');
        // Hiển thị tên khu vực
        showZoneName();
    }
    
    // Tăng tốc độ dần
    gameSpeed = 6 + Math.floor(score / 300) * 0.5;
    
    // Xử lý nhảy
    if (isJumping) {
        playerY += jumpVelocity;
        jumpVelocity -= gravity;
        player.style.bottom = (groundLevel + playerY) + 'px';
        if (playerY <= 0) {
            playerY = 0;
            isJumping = false;
            jumpVelocity = 0;
            player.style.bottom = groundLevel + 'px';
        }
    }
    
    // Di chuyển vật cản
    for (let i = obstacles.length - 1; i >= 0; i--) {
        const obs = obstacles[i];
        let x = parseFloat(obs.style.left);
        x -= gameSpeed;
        obs.style.left = x + 'px';
        if (x < -50) {
            obs.remove();
            obstacles.splice(i, 1);
        }
    }
    
    // Di chuyển chim
    for (let i = birds.length - 1; i >= 0; i--) {
        const bird = birds[i];
        let x = parseFloat(bird.style.left);
        x -= gameSpeed;
        let y = parseFloat(bird.style.bottom) + parseFloat(bird.dataset.vy);
        bird.style.left = x + 'px';
        bird.style.bottom = y + 'px';
        if (x < -50) {
            bird.remove();
            birds.splice(i, 1);
        }
    }
    
    // Kiểm tra va chạm
    if (checkCollision()) {
        endGame();
        return;
    }
    
    // Random spawn vật cản
    if (Math.random() < 0.02) {
        spawnObstacle();
    }
    
    requestAnimationFrame(gameLoop);
}

// Kiểm tra va chạm
function checkCollision() {
    const playerRect = {
        left: 50,
        right: 50 + 40,
        bottom: isDucking ? 30 : (groundLevel + playerY),
        top: isDucking ? 30 + 25 : (groundLevel + playerY + 50)
    };
    
    for (const obs of obstacles) {
        const obsX = parseFloat(obs.style.left);
        const obsRect = {
            left: obsX,
            right: obsX + 40,
            bottom: groundLevel,
            top: groundLevel + 50
        };
        if (rectsOverlap(playerRect, obsRect)) return true;
    }
    
    for (const bird of birds) {
        const birdX = parseFloat(bird.style.left);
        const birdY = parseFloat(bird.style.bottom);
        const birdRect = {
            left: birdX,
            right: birdX + 30,
            bottom: birdY,
            top: birdY + 30
        };
        if (rectsOverlap(playerRect, birdRect)) return true;
    }
    
    return false;
}

function rectsOverlap(r1, r2) {
    return !(r1.right < r2.left || r1.left > r2.right || r1.top < r2.bottom || r1.bottom > r2.top);
}

// Hiển thị tên khu vực
function showZoneName() {
    const div = document.createElement('div');
    div.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:white;font-size:30px;font-weight:bold;z-index:4;text-shadow:2px 2px 4px rgba(0,0,0,0.5);';
    div.textContent = zoneNames[zone];
    container.appendChild(div);
    setTimeout(() => div.remove(), 2000);
}

// Điều khiển
document.addEventListener('keydown', (e) => {
    if (!gameRunning) return;
    if (e.code === 'Space') {
        e.preventDefault();
        if (!isJumping && !isDucking) {
            isJumping = true;
            jumpVelocity = 15;
            playSound('jump');
        }
    }
    if (e.code === 'ArrowDown') {
        e.preventDefault();
        if (!isJumping && !isDucking) {
            isDucking = true;
            player.classList.add('duck');
            playSound('duck');
        }
    }
});

document.addEventListener('keyup', (e) => {
    if (e.code === 'ArrowDown') {
        isDucking = false;
        player.classList.remove('duck');
        playSound('duck');
    }
});

// Kết thúc game
function endGame() {
    gameRunning = false;
    playSound('gameOver');
    finalScoreEl.textContent = 'Điểm: ' + score;
    gameOverEl.style.display = 'block';
}

// Bắt đầu lại
function restartGame() {
    // Xóa vật cản
    obstacles.forEach(o => o.remove());
    birds.forEach(b => b.remove());
    obstacles = [];
    birds = [];
    
    // Reset trạng thái
    score = 0;
    scoreEl.textContent = '0';
    gameSpeed = 6;
    isJumping = false;
    isDucking = false;
    playerY = 0;
    jumpVelocity = 0;
    player.style.bottom = groundLevel + 'px';
    player.classList.remove('duck');
    phase = 0;
    zone = 0;
    updateSky();
    
    gameOverEl.style.display = 'none';
    gameRunning = true;
    gameLoop();
}

// Khởi động
updateSky();
restartGame();
</script>
</body>
</html>
