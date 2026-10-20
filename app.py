import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="T-Rex Runner Pro", page_icon="🦖", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #2ecc71; font-family: monospace;'>🦖 T-REX RUNNER PRO</h1>
    <p style='text-align: center; color: #b2bec3; font-family: monospace;'>
    - Nhấn <b>Spacebar / Mũi tên lên</b> hoặc nút <b>NHẢY</b> để né xương rồng<br>
    - Nhấn <b>Mũi tên xuống</b> hoặc giữ nút <b>CÚI</b> để né chim bay chéo xuống<br>
    - Bầu trời chuyển Ngày / Đêm mỗi <b>500 điểm</b>!
    </p>
""", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>T-Rex Runner Pro</title>
    <style>
        body {
            margin: 0;
            background-color: #0f0f0f;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            font-family: 'Courier New', Courier, monospace;
        }
        canvas {
            border: 4px solid #fff;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            box-shadow: 0 0 25px rgba(46, 204, 113, 0.4);
            background: #f7f7f7;
            transition: background 1s ease;
        }
        .btn-container {
            margin-top: 15px;
            display: flex;
            gap: 15px;
        }
        .game-btn {
            background-color: #2ecc71;
            color: white;
            border: 3px solid #fff;
            padding: 10px 25px;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            cursor: pointer;
            box-shadow: 0 4px 0 #27ae60;
            border-radius: 6px;
        }
        .game-btn:active {
            transform: translateY(4px);
            box-shadow: 0 0 0 #27ae60;
        }
        .duck-btn {
            background-color: #e67e22;
            box-shadow: 0 4px 0 #ca6f1e;
        }
        .duck-btn:active {
            box-shadow: 0 0 0 #ca6f1e;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="800" height="250"></canvas>

<div class="btn-container">
    <button class="game-btn" id="jumpBtn">🚀 NHẢY (JUMP)</button>
    <button class="game-btn duck-btn" id="duckBtn">⬇️ CÚI (DUCK)</button>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// System Âm thanh Web Audio API (Retro Sound Effects)
const AudioContext = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new AudioContext();
    }
}

function playSound(type) {
    if (!audioCtx) return;
    try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
osc.connect(gain);
        gain.connect(audioCtx.destination);

        if (type === 'jump') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(150, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.1);
            gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.1);
        } else if (type === 'duck') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(300, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.08);
        } else if (type === 'gameover') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(200, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.4);
            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.4);
        }
    } catch(e){}
}

let score = 0;
let highScore = 0;
let gameSpeed = 5;
let isGameOver = false;

// Trạng thái ngày/đêm
let isNightMode = false;

// Khủng Long T-Rex
let dino = {
    x: 50,
    y: 165,
    width: 32,
    height: 36,
    normalHeight: 36,
    duckHeight: 20,
    vy: 0,
    gravity: 0.75,
    jumpPower: -13.5,
    isJumping: false,
    isDucking: false,
    animFrame: 0,
    draw() {
        ctx.fillStyle = isNightMode ? "#ecf0f1" : "#535353";
        if (this.isDucking && !this.isJumping) {
            // Tư thế cúi sát người né chim
            ctx.fillRect(this.x, this.y + 16, 42, 20);
            ctx.fillRect(this.x + 26, this.y + 8, 16, 12);
            ctx.fillStyle = isNightMode ? "#2c3e50" : "#fff";
            ctx.fillRect(this.x + 36, this.y + 10, 3, 3);
        } else {
            // Đứng chạy
            ctx.fillRect(this.x + 6, this.y + 12, 18, 16);
            ctx.fillRect(this.x + 14, this.y, 16, 14);
            ctx.fillStyle = isNightMode ? "#2c3e50" : "#fff";
            ctx.fillRect(this.x + 24, this.y + 3, 3, 3);
            ctx.fillStyle = isNightMode ? "#ecf0f1" : "#535353";
            ctx.fillRect(this.x + 20, this.y + 14, 4, 3);
            
            if (this.isJumping) {
                ctx.fillRect(this.x + 8, this.y + 28, 4, 8);
                ctx.fillRect(this.x + 16, this.y + 28, 4, 8);
            } else {
                if (Math.floor(this.animFrame / 8) % 2 === 0) {
                    ctx.fillRect(this.x + 8, this.y + 28, 4, 8);
ctx.fillRect(this.x + 16, this.y + 28, 3, 6);
                } else {
                    ctx.fillRect(this.x + 8, this.y + 28, 3, 6);
                    ctx.fillRect(this.x + 16, this.y + 28, 4, 8);
                }
            }
        }
        this.animFrame++;
    },
    jump() {
        if (!this.isJumping) {
            initAudio();
            playSound('jump');
            this.vy = this.jumpPower;
            this.isJumping = true;
            this.isDucking = false;
            this.height = this.normalHeight;
        }
    },
    duck(active) {
        if (!this.isJumping) {
            if (active && !this.isDucking) {
                initAudio();
                playSound('duck');
            }
            this.isDucking = active;
            if (active) {
                this.height = this.duckHeight;
                this.y = 165 + (this.normalHeight - this.duckHeight);
            } else {
                this.height = this.normalHeight;
                this.y = 165;
            }
        }
    },
    update() {
        this.vy += this.gravity;
        this.y += this.vy;
        let groundLevel = this.isDucking ? 165 + (this.normalHeight - this.duckHeight) : 165;
        if (this.y > groundLevel) {
            this.y = groundLevel;
            this.vy = 0;
            this.isJumping = false;
        }
    }
};

let obstacles = [];

// Xương rồng
class Cactus {
    constructor() {
        this.width = 20;
        this.height = 35;
        this.x = canvas.width;
        this.y = 200 - this.height;
        this.type = 'cactus';
    }
    draw() {
        ctx.fillStyle = "#27ae60";
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.fillStyle = "#1e8449";
        ctx.fillRect(this.x - 4, this.y + 8, 4, 6);
        ctx.fillRect(this.x + this.width, this.y + 16, 4, 6);
    }
    update() {
        this.x -= gameSpeed;
    }
}

// Chim bay CHÉO XUỐNG (Di chuyển đường chéo từ cao xuống tầm đầu)
class DiagonalBird {
    constructor() {
        this.width = 30;
        this.height = 20;
        this.x = canvas.width;
        this.y = 100; // Khởi điểm bay cao trên trời
        this.targetY = 158; // Bay chéo xuống ngay tầm đầu khủng long!
        this.vy = 0.6; // Tốc độ sà xuống
        this.type = 'bird';
        this.animFrame = 0;
    }
    draw() {
        ctx.fillStyle = isNightMode ? "#e74c3c" : "#8e44ad";
        ctx.fillRect(this.x, this.y + 6, 30, 10);
        ctx.fillRect(this.x + 8, this.y, 10, 8);
        
        ctx.fillStyle = isNightMode ? "#ff7675" : "#9b59b6";
        if (Math.floor(this.animFrame / 8) % 2 === 0) {
            ctx.fillRect(this.x + 12, this.y - 6, 8, 8);
        } else {
            ctx.fillRect(this.x + 12, this.y + 14, 8, 8);
        }
        this.animFrame++;
    }
    update() {
        this.x -= gameSpeed;
        // Quỹ đạo sà chéo xuống
        if (this.y < this.targetY) {
this.y += this.vy;
        }
    }
}

function resetGame() {
    score = 0;
    gameSpeed = 5;
    obstacles = [];
    isGameOver = false;
    isNightMode = false;
    dino.y = 165;
    dino.height = dino.normalHeight;
    dino.isDucking = false;
}

// Bắt sự kiện phím
window.addEventListener("keydown", e => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        if (isGameOver) resetGame();
        else dino.jump();
        e.preventDefault();
    }
    if (e.code === "ArrowDown") {
        if (!isGameOver) dino.duck(true);
        e.preventDefault();
    }
});

window.addEventListener("keyup", e => {
    if (e.code === "ArrowDown") {
        if (!isGameOver) dino.duck(false);
    }
});

// Nút bấm ảo
document.getElementById("jumpBtn").addEventListener("click", () => {
    if (isGameOver) resetGame();
    else dino.jump();
});

const duckBtn = document.getElementById("duckBtn");
duckBtn.addEventListener("mousedown", () => { if(!isGameOver) dino.duck(true); });
duckBtn.addEventListener("mouseup", () => { if(!isGameOver) dino.duck(false); });
duckBtn.addEventListener("touchstart", (e) => { if(!isGameOver) dino.duck(true); e.preventDefault(); });
duckBtn.addEventListener("touchend", (e) => { if(!isGameOver) dino.duck(false); e.preventDefault(); });

let obstacleTimer = 0;

function gameLoop() {
    // 500 điểm ĐỔI MÀU BẦU TRỜI (NGÀY / ĐÊM)
    let currentScore = Math.floor(score);
    isNightMode = Math.floor(currentScore / 500) % 2 === 1;

    // Nền bầu trời
    ctx.fillStyle = isNightMode ? "#1a252f" : "#f7f7f7";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Mặt trời / Mặt trăng
    ctx.fillStyle = isNightMode ? "#f1c40f" : "#f39c12";
    ctx.fillRect(700, 30, 24, 24);

    // Đường mặt đất
    ctx.strokeStyle = isNightMode ? "#bdc3c7" : "#535353";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 200);
    ctx.lineTo(canvas.width, 200);
    ctx.stroke();

    if (!isGameOver) {
        dino.update();
        score += 0.15;
        // Tốc độ TĂNG NHANH DẦN theo thời gian
        gameSpeed = 5.5 + (score / 150);

        obstacleTimer++;
        if (obstacleTimer > Math.max(50, 90 - (gameSpeed * 2)) + Math.random() * 40) {
            // Sinh chim bay chéo xuống hoặc xương rồng
            if (score > 100 && Math.random() > 0.45) {
                obstacles.push(new DiagonalBird());
            } else {
                obstacles.push(new Cactus());
            }
            obstacleTimer = 0;
        }
    }

    // Xử lý chướng ngại vật
    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].update();
        obstacles[i].draw();

        // Kiểm tra va chạm AABB
        if (
            dino.x + 4 < obstacles[i].x + obstacles[i].width - 4 &&
            dino.x + dino.width - 4 > obstacles[i].x + 4 &&
            dino.y + 4 < obstacles[i].y + obstacles[i].height &&
dino.y + dino.height > obstacles[i].y
        ) {
            if (!isGameOver) {
                playSound('gameover');
            }
            isGameOver = true;
            if (score > highScore) highScore = Math.floor(score);
        }

        if (obstacles[i].x < -40) {
            obstacles.splice(i, 1);
        }
    }

    dino.draw();

    // Hiển thị điểm & chế độ
    ctx.fillStyle = isNightMode ? "#ecf0f1" : "#535353";
    ctx.font = "bold 15px 'Courier New'";
    ctx.fillText("ĐIỂM: " + currentScore, 630, 30);
    ctx.fillText("KỶ LỤC: " + highScore, 630, 52);

    // Màn hình Game Over
    if (isGameOver) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#e74c3c";
        ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("💀 GAME OVER - BỊ VA CHẠM!", 210, 100);
        
        ctx.fillStyle = "#fff";
        ctx.font = "15px 'Courier New'";
        ctx.fillText("Bấm [SPACEBAR] hoặc nút [NHẢY] để chơi lại", 205, 145);
    }

    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>

</body>
</html>
"""

components.html(game_code, height=360)
