import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino Adventure Colorful", page_icon="🦖", layout="centered")

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Colorful Dino Adventure</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #74b9ff, #a29bfe);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
            touch-action: none;
        }
        .game-container {
            width: 100%;
            max-width: 850px;
            padding: 0 10px;
            box-sizing: border-box;
            text-align: center;
        }
        canvas {
            width: 100%;
            height: auto;
            background: #ffffff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border-radius: 12px;
            display: block;
        }
        .instructions {
            margin-top: 10px;
            font-size: 14px;
            color: #ffffff;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>

<div class="game-container">
    <canvas id="gameCanvas" width="850" height="350"></canvas>
    <div class="instructions">Máy tính: [Space/↑] Nhảy rất cao, [↓] Cúi đầu | Điện thoại: Chạm để Nhảy, Vuốt xuống để Cúi</div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let gameState = "START"; // START, PLAYING, GAMEOVER
let score = 0;
let highScore = 0;
let gameSpeed = 6;
let gravity = 0.55; // Giảm trọng lực một chút để khủng long bay lên cao và lơ lửng tốt hơn
let animFrame = 0;

// Khủng long màu sắc tươi sáng, lực nhảy cực khỏe
const dino = {
    x: 60,
    y: 225,
    width: 48,
    height: 55,
    dy: 0,
    jumpPower: -15.5, // Tăng mạnh lực nhảy giúp né mọi loại xương rồng
    grounded: true,
    ducking: false,
    draw() {
        const x = this.x;
        const y = this.y;

        if (this.ducking) {
            // Khủng long cúi người né chim bay chéo
            ctx.fillStyle = "#00b894"; 
            ctx.fillRect(x, y + 22, 62, 33); 
            ctx.fillRect(x + 40, y + 10, 24, 18); 
            
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x + 54, y + 13, 4, 4);
            ctx.fillStyle = "#fd79a8";
            ctx.fillRect(x + 56, y + 18, 5, 4);

            ctx.fillStyle = "#00a383";
            if (Math.floor(animFrame / 6) % 2 === 0) {
                ctx.fillRect(x + 15, y + 55, 8, 8);
                ctx.fillRect(x + 42, y + 55, 8, 8);
            } else {
                ctx.fillRect(x + 20, y + 55, 8, 8);
                ctx.fillRect(x + 38, y + 55, 8, 8);
            }
        } else {
            // Khủng long đứng / chạy màu xanh lá tươi
            ctx.fillStyle = "#00b894"; 
            
            ctx.fillRect(x + 18, y, 26, 16);
            ctx.fillRect(x + 36, y + 8, 12, 10);
            
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x + 36, y + 3, 4, 4);
            ctx.fillStyle = "#000000";
            ctx.fillRect(x + 38, y + 4, 2, 2);
            ctx.fillStyle = "#fd79a8";
            ctx.fillRect(x + 38, y + 10, 5, 4);

            ctx.fillStyle = "#00b894";
            ctx.fillRect(x + 10, y + 14, 26, 24);
            ctx.fillStyle = "#55efc4";
            ctx.fillRect(x + 4, y + 18, 10, 6);

            ctx.fillStyle = "#00b894";
            ctx.fillRect(x - 2, y + 12, 12, 8);
            ctx.fillRect(x - 8, y + 8, 8, 6);

            ctx.fillStyle = "#00a383";
            if (this.grounded) {
                if (Math.floor(animFrame / 6) % 2 === 0) {
                    ctx.fillRect(x + 14, y + 38, 7, 17);
                    ctx.fillRect(x + 26, y + 38, 7, 10);
                } else {
                    ctx.fillRect(x + 14, y + 38, 7, 10);
                    ctx.fillRect(x + 26, y + 38, 7, 17);
                }
            } else {
                ctx.fillRect(x + 14, y + 38, 7, 14);
                ctx.fillRect(x + 26, y + 38, 7, 14);
            }
        }
    },
    update() {
        if (this.ducking && this.grounded) {
            this.width = 62;
            this.height = 33;
            this.y = 247;
        } else {
            this.width = 48;
            this.height = 55;
            this.y = 225;
        }

        this.dy += gravity;
        this.y += this.dy;

        if (this.y > 225) {
            this.y = 225;
            this.dy = 0;
            this.grounded = true;
        }
    },
    jump() {
        if (this.grounded && !this.ducking) {
            this.dy = this.jumpPower;
            this.grounded = false;
        }
    }
};

let obstacles = [];
let clouds = [];
let pyramids = [];

for (let i = 0; i < 4; i++) {
    clouds.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 100 + 20,
        width: 60,
        height: 20,
        speed: 1
    });
}

for (let i = 0; i < 2; i++) {
    pyramids.push({
        x: i * 500 + 300,
        y: 170,
        width: 80,
        height: 115,
        speed: 1.5
    });
}

let obstacleTimer = 0;
let nextObstacleTime = 110;

function spawnObstacle() {
    const type = Math.random();
    if (type < 0.5) {
        let variant = Math.floor(Math.random() * 3);
        obstacles.push({
            x: canvas.width,
            y: 220,
            width: variant === 2 ? 38 : 22,
            height: 60,
            type: "cactus",
            variant: variant
        });
    } else {
        obstacles.push({
            x: canvas.width,
            y: 130,
            targetY: 200,
            width: 48,
            height: 32,
            type: "bird",
            dy: 0.2
        });
    }
}

window.addEventListener("keydown", (e) => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        if (gameState === "START" || gameState === "GAMEOVER") {
            resetGame();
        } else {
            dino.jump();
        }
    }
    if (e.code === "ArrowDown") {
        e.preventDefault();
        if (gameState === "PLAYING") {
            dino.ducking = true;
        }
    }
});

window.addEventListener("keyup", (e) => {
    if (e.code === "ArrowDown") {
        dino.ducking = false;
    }
});

let touchStartY = 0;
window.addEventListener("touchstart", (e) => {
    touchStartY = e.touches[0].clientY;
    if (gameState === "START" || gameState === "GAMEOVER") {
        resetGame();
    } else {
        dino.jump();
    }
}, {passive: false});

window.addEventListener("touchmove", (e) => {
    let touchY = e.touches[0].clientY;
    if (touchY - touchStartY > 35) {
        dino.ducking = true;
    }
    e.preventDefault();
}, {passive: false});

window.addEventListener("touchend", () => {
    dino.ducking = false;
});

function resetGame() {
    gameState = "PLAYING";
    score = 0;
    gameSpeed = 6;
    obstacles = [];
    dino.y = 225;
    dino.dy = 0;
    dino.grounded = true;
    dino.ducking = false;
    obstacleTimer = 0;
}

function animate() {
    animFrame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let isNight = score >= 1000;
    let skyGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    if (!isNight) {
        skyGrad.addColorStop(0, "#74b9ff");
        skyGrad.addColorStop(1, "#dfe6e9");
    } else {
        skyGrad.addColorStop(0, "#2d3436");
        skyGrad.addColorStop(1, "#636e72");
    }
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = isNight ? "#ffeaa7" : "#fdcb6e";
    ctx.beginPath();
    ctx.arc(730, 60, 25, 0, Math.PI * 2);
    ctx.fill();

    clouds.forEach(cloud => {
        if (gameState === "PLAYING") cloud.x -= cloud.speed;
        if (cloud.x + cloud.width < 0) {
            cloud.x = canvas.width;
            cloud.y = Math.random() * 100 + 20;
        }
        ctx.fillStyle = isNight ? "rgba(255,255,255,0.15)" : "rgba(255,255,255,0.7)";
        ctx.beginPath();
        ctx.arc(cloud.x + 15, cloud.y + 10, 15, 0, Math.PI * 2);
        ctx.arc(cloud.x + 35, cloud.y + 5, 20, 0, Math.PI * 2);
        ctx.arc(cloud.x + 50, cloud.y + 12, 12, 0, Math.PI * 2);
        ctx.fill();
    });

    pyramids.forEach(p => {
        if (gameState === "PLAYING") p.x -= p.speed;
        if (p.x + p.width < 0) {
            p.x = canvas.width + Math.random() * 200;
        }
        ctx.fillStyle = isNight ? "#b2bec3" : "#fab1a0";
        ctx.beginPath();
        ctx.moveTo(p.x + p.width / 2, p.y);
        ctx.lineTo(p.x, p.y + p.height);
        ctx.lineTo(p.x + p.width, p.y + p.height);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = isNight ? "#636e72" : "#e17055";
        ctx.fillRect(p.x + p.width/2 - 7, p.y + p.height - 30, 14, 30);
    });

    ctx.fillStyle = isNight ? "#2d3436" : "#00b894";
    ctx.fillRect(0, 280, canvas.width, 70);
    ctx.fillStyle = isNight ? "#636e72" : "#55efc4";
    ctx.fillRect(0, 280, canvas.width, 8);

    if (gameState === "PLAYING") {
        gameSpeed = 6 + Math.floor(score / 120);
        score += 0.05;

        obstacleTimer++;
        if (obstacleTimer > nextObstacleTime) {
            spawnObstacle();
            obstacleTimer = 0;
            nextObstacleTime = Math.floor(Math.random() * 45) + 65 - Math.min(25, Math.floor(score / 100));
        }

        dino.update();
    }

    dino.draw();

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        if (gameState === "PLAYING") {
            obs.x -= gameSpeed;
            if (obs.type === "bird") {
                obs.y += obs.dy;
                if (obs.y > 210 || obs.y < 120) obs.dy *= -1;
            }
        }

        if (obs.type === "cactus") {
            ctx.fillStyle = "#00b894";
            if (obs.variant === 0) {
                ctx.fillRect(obs.x + 6, obs.y, 10, 60);
                ctx.fillRect(obs.x, obs.y + 18, 6, 16);
                ctx.fillRect(obs.x + 16, obs.y + 28, 6, 16);
            } else if (obs.variant === 1) {
                ctx.fillRect(obs.x + 2, obs.y + 10, 8, 50);
                ctx.fillRect(obs.x + 12, obs.y, 9, 60);
                ctx.fillRect(obs.x + 21, obs.y + 20, 6, 18);
            } else {
                ctx.fillRect(obs.x + 4, obs.y + 5, 9, 55);
                ctx.fillRect(obs.x, obs.y + 22, 6, 18);
                ctx.fillRect(obs.x + 16, obs.y + 12, 8, 48);
                ctx.fillRect(obs.x + 26, obs.y + 25, 7, 20);
            }
        } else {
            ctx.fillStyle = "#e17055";
            let wingUp = Math.floor(animFrame / 8) % 2 === 0;
            
            ctx.fillRect(obs.x + 8, obs.y + 10, 26, 12);
            ctx.fillRect(obs.x, obs.y + 13, 10, 6); 
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(obs.x + 24, obs.y + 12, 3, 3);
            
            ctx.fillStyle = "#fab1a0";
            if (wingUp) {
                ctx.fillRect(obs.x + 14, obs.y - 2, 12, 12);
            } else {
                ctx.fillRect(obs.x + 14, obs.y + 16, 12, 12);
            }
        }

        if (
            dino.x < obs.x + obs.width - 4 &&
            dino.x + dino.width - 4 > obs.x &&
            dino.y < obs.y + obs.height - 4 &&
            dino.y + dino.height - 4 > obs.y
        ) {
            gameState = "GAMEOVER";
            if (Math.floor(score) > highScore) {
                highScore = Math.floor(score);
