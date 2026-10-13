import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Dino Game Mobile & PC", page_icon="🦖", layout="centered")

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Google Dino Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #f7f7f7;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Courier New', Courier, monospace;
            overflow: hidden;
            touch-action: none;
        }
        .game-container {
            width: 100%;
            max-width: 800px;
            padding: 0 10px;
            box-sizing: border-box;
        }
        canvas {
            width: 100%;
            height: auto;
            background: #ffffff;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            border-radius: 6px;
            display: block;
        }
        .instructions {
            text-align: center;
            margin-top: 10px;
            font-size: 13px;
            color: #666;
        }
    </style>
</head>
<body>

<div class="game-container">
    <canvas id="gameCanvas" width="800" height="300"></canvas>
    <div class="instructions" id="hintText">Máy tính: [Space/↑] Nhảy, [↓] Cúi | Điện thoại: Chạm để Nhảy, Vuốt xuống để Cúi</div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let gameState = "START"; // START, PLAYING, GAMEOVER
let score = 0;
let highScore = 0;
let gameSpeed = 6;
let gravity = 0.65;
let animFrame = 0;

// Khủng long T-Rex chuẩn xác từng chi tiết hình dáng
const dino = {
    x: 50,
    y: 215,
    width: 44,
    height: 52,
    dy: 0,
    jumpPower: -12,
    grounded: true,
    ducking: false,
    draw() {
        ctx.fillStyle = "#535353";
        const x = this.x;
        const y = this.y;

        if (this.ducking) {
            // Khủng long cúi người né chim bay (Thân dài thấp)
            ctx.fillRect(x, y + 22, 58, 30); // Thân
            ctx.fillRect(x + 36, y + 10, 22, 16); // Đầu cúi
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x + 50, y + 13, 3, 3); // Mắt
            ctx.fillStyle = "#535353";
            
            // Chân cúi chạy
            if (Math.floor(animFrame / 6) % 2 === 0) {
                ctx.fillRect(x + 14, y + 52, 6, 8);
                ctx.fillRect(x + 38, y + 52, 6, 8);
            } else {
                ctx.fillRect(x + 18, y + 52, 6, 8);
                ctx.fillRect(x + 34, y + 52, 6, 8);
            }
        } else {
            // Khủng long đứng / chạy chuẩn dáng T-Rex
            // Đầu & Mõm
            ctx.fillRect(x + 16, y, 24, 15);
            ctx.fillRect(x + 32, y + 8, 10, 8);
            // Mắt khủng long
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x + 32, y + 3, 3, 3);
            ctx.fillStyle = "#535353";

            // Thân & Tay
            ctx.fillRect(x + 10, y + 14, 24, 20);
            ctx.fillRect(x + 4, y + 18, 10, 5); // Tay ngắn đặc trưng

            // Đuôi dài vểnh phía sau
            ctx.fillRect(x, y + 12, 10, 6);
            ctx.fillRect(x - 4, y + 10, 5, 4);

            // Chân chạy hoạt hoạ động lực học
            if (this.grounded) {
                if (Math.floor(animFrame / 6) % 2 === 0) {
                    // Bước chân 1
                    ctx.fillRect(x + 14, y + 34, 6, 14);
                    ctx.fillRect(x + 24, y + 34, 6, 8);
                } else {
                    // Bước chân 2
                    ctx.fillRect(x + 14, y + 34, 6, 8);
                    ctx.fillRect(x + 24, y + 34, 6, 14);
                }
            } else {
                // Nhảy lên (chụm chân)
                ctx.fillRect(x + 14, y + 34, 6, 12);
                ctx.fillRect(x + 24, y + 34, 6, 12);
            }
        }
    },
    update() {
        if (this.ducking && this.grounded) {
            this.width = 58;
            this.height = 30;
            this.y = 237;
        } else {
            this.width = 44;
            this.height = 52;
            this.y = 215;
        }

        this.dy += gravity;
        this.y += this.dy;

        if (this.y > 215) {
            this.y = 215;
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

// Khởi tạo mây trời
for (let i = 0; i < 4; i++) {
    clouds.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 90 + 20,
        width: 46,
        height: 14,
        speed: 1
    });
}

// Khởi tạo tháp Ai Cập ở hậu cảnh
for (let i = 0; i < 2; i++) {
    pyramids.push({
        x: i * 450 + 300,
        y: 160,
        width: 75,
        height: 107,
        speed: 1.5
    });
}

let obstacleTimer = 0;
let nextObstacleTime = 110;

function spawnObstacle() {
    const type = Math.random();
    if (type < 0.55) {
        // Cây xương rồng (nhiều kiểu kích cỡ)
        let isGroup = Math.random() < 0.4;
        obstacles.push({
            x: canvas.width,
            y: 212,
            width: isGroup ? 34 : 20,
            height: 55,
            type: "cactus",
            isGroup: isGroup
        });
    } else {
        // Con chim bay ngang tầm phải cúi đầu
        obstacles.push({
            x: canvas.width,
            y: 150, // Vị trí bay ngang tầm đầu khủng long cúi
            width: 46,
            height: 32,
            type: "bird"
        });
    }
}

// Điều khiển bàn phím (Laptop/PC)
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

// Điều khiển Cảm ứng (Điện thoại / Máy tính bảng)
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
    if (touchY - touchStartY > 40) {
        // Vuốt xuống -> Cúi đầu
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
    dino.y = 215;
    dino.dy = 0;
    dino.grounded = true;
    dino.ducking = false;
    obstacleTimer = 0;
}

function animate() {
    animFrame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Chuyển màu bầu trời Night Mode khi đạt >= 1000 điểm
    let isNight = score >= 1000;
    ctx.fillStyle = isNight ? "#202124" : "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    let textColor = isNight ? "#f1f3f4" : "#535353";
    let objectColor = isNight ? "#9aa0a6" : "#535353";

    // Vẽ Mặt Trời / Mặt Trăng
    ctx.fillStyle = objectColor;
    ctx.beginPath();
    ctx.arc(700, 55, 18, 0, Math.PI * 2);
    ctx.fill();

    // Vẽ Mây bay
    clouds.forEach(cloud => {
        if (gameState === "PLAYING") cloud.x -= cloud.speed;
        if (cloud.x + cloud.width < 0) {
            cloud.x = canvas.width;
            cloud.y = Math.random() * 90 + 20;
        }
        ctx.fillStyle = isNight ? "#3c4043" : "#e0e0e0";
        ctx.fillRect(cloud.x, cloud.y, cloud.width, cloud.height);
        ctx.fillRect(cloud.x + 10, cloud.y - 4, 20, 6);
    });

    // Vẽ Tháp Ai Cập nền sau
    pyramids.forEach(p => {
        if (gameState === "PLAYING") p.x -= p.speed;
        if (p.x + p.width < 0) {
            p.x = canvas.width + Math.random() * 200;
        }
        ctx.fillStyle = isNight ? "#303134" : "#e8e8e8";
        ctx.beginPath();
        ctx.moveTo(p.x + p.width / 2, p.y);
        ctx.lineTo(p.x, p.y + p.height);
        ctx.lineTo(p.x + p.width, p.y + p.height);
        ctx.closePath();
        ctx.fill();
        // Chi tiết cửa tháp
        ctx.fillStyle = isNight ? "#202124" : "#d0d0d0";
        ctx.fillRect(p.x + p.width/2 - 6, p.y + p.height - 25, 12, 25);
    });

    // Vẽ mặt đất
    ctx.strokeStyle = objectColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 267);
    ctx.lineTo(canvas.width, 267);
    ctx.stroke();

    if (gameState === "PLAYING") {
        gameSpeed = 6 + Math.floor(score / 150);
        score += 0.05;

        obstacleTimer++;
        if (obstacleTimer > nextObstacleTime) {
            spawnObstacle();
            obstacleTimer = 0;
            nextObstacleTime = Math.floor(Math.random() * 45) + 70 - Math.min(25, Math.floor(score / 100));
        }

        dino.update();
    }

    dino.draw();

    // Xử lý chướng ngại vật (Xương rồng & Chim)
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        if (gameState === "PLAYING") obs.x -= gameSpeed;

        ctx.fillStyle = objectColor;
        if (obs.type === "cactus") {
            if (obs.isGroup) {
                // Chùm xương rồng lớn
                ctx.fillRect(obs.x + 4, obs.y + 10, 8, 45);
                ctx.fillRect(obs.x, obs.y + 20, 6, 20);
                ctx.fillRect(obs.x + 16, obs.y + 5, 8, 50);
                ctx.fillRect(obs.x + 26, obs.y + 18, 6, 22);
            } else {
                // Xương rồng đơn chuẩn
                ctx.fillRect(obs.x + 6, obs.y + 5, 8, 50);
                ctx.fillRect(obs.x, obs.y + 15, 6, 18);
                ctx.fillRect(obs.x + 14, obs.y + 22, 6, 16);
            }
        } else {
            // Con chim bay (hiệu ứng đập cánh vẫy lên vẫy xuống rõ nét)
            let wingUp = Math.floor(animFrame / 10) % 2 === 0;
            // Thân chim & Mỏ
            ctx.fillRect(obs.x + 8, obs.y + 10, 24, 10);
            ctx.fillRect(obs.x, obs.y + 12, 10, 6); // Mỏ nhọn
            // Mắt chim
            ctx.fillStyle = isNight ? "#202124" : "#ffffff";
            ctx.fillRect(obs.x + 22, obs.y + 12, 2, 2);
            ctx.fillStyle = objectColor;
            
            // Cánh chim đập
            if (wingUp) {
                ctx.fillRect(obs.x + 12, obs.y, 12, 10); // Cánh vươn lên
            } else {
                ctx.fillRect(obs.x + 12, obs.y + 18, 12, 10); // Cánh cụp xuống
            }
        }

        // Kiểm tra va chạm cực kỳ chính xác
        if (
            dino.x < obs.x + obs.width - 4 &&
            dino.x + dino.width - 4 > obs.x &&
            dino.y < obs.y + obs.height - 4 &&
            dino.y + dino.height - 4 > obs.y
        ) {
            gameState = "GAMEOVER";
            if (Math.floor(score) > highScore) {
                highScore = Math.floor(score);
            }
        }

        if (obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
        }
    }

    // Hiển thị điểm số dạng số điện tử Google
    ctx.fillStyle = textColor;
    ctx.font = "16px 'Courier New'";
    let hiStr = String(highScore).padStart(5, '0');
    let scStr = String(Math.floor(score)).padStart(5, '0');
    ctx.fillText("HI " + hiStr + "  " + scStr, canvas.width - 190, 30);

    // Màn hình Start / Game Over
    if (gameState === "START") {
        ctx.fillStyle = textColor;
        ctx.font = "14px 'Courier New'";
        ctx.textAlign = "center";
        ctx.fillText("NHẤN PHÍM CÁCH HOẶC CHẠM MÀN HÌNH ĐỂ CHƠI", canvas.width / 2, canvas.height / 2);
        ctx.textAlign = "left";
    } else if (gameState === "GAMEOVER") {
        ctx.fillStyle = textColor;
        ctx.font = "20px 'Courier New'";
        ctx.textAlign = "center";
        ctx.fillText("G A M E   O V E R", canvas.width / 2, canvas.height / 2 - 10);
        ctx.font = "12px 'Courier New'";
        ctx.fillText("Chạm hoặc nhấn phím để chơi lại", canvas.width / 2, canvas.height / 2 + 20);
        ctx.textAlign = "left";
    }

    requestAnimationFrame(animate);
}

animate();
</script>

</body>
</html>
"""

components.html(game_html, height=360, width=820)
