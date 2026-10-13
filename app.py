import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Dino Game Deluxe", page_icon="🦖", layout="centered")

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Dino Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #f7f7f7;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Courier New', Courier, monospace;
            overflow: hidden;
        }
        canvas {
            background: #ffffff;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 4px;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="800" height="300"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let gameState = "START"; // START, PLAYING, GAMEOVER
let score = 0;
let highScore = 0;
let gameSpeed = 6;
let gravity = 0.6;
let animFrame = 0;

// Khủng long chuẩn Google T-Rex
const dino = {
    x: 50,
    y: 220,
    width: 44,
    height: 47,
    dy: 0,
    jumpPower: -11.5,
    grounded: true,
    ducking: false,
    draw() {
        ctx.fillStyle = "#535353";
        const x = this.x;
        const y = this.y;

        if (this.ducking) {
            // Hình dáng khi cúi đầu
            ctx.fillRect(x, y + 20, 59, 27); // Thân cúi
            ctx.fillRect(x + 35, y + 10, 20, 15); // Đầu cúi
            // Chân cúi
            if (Math.floor(animFrame / 6) % 2 === 0) {
                ctx.fillRect(x + 15, y + 47, 6, 8);
                ctx.fillRect(x + 35, y + 47, 6, 8);
            } else {
                ctx.fillRect(x + 18, y + 47, 6, 8);
                ctx.fillRect(x + 32, y + 47, 6, 8);
            }
        } else {
            // Hình dáng chuẩn T-Rex đứng/chạy
            ctx.fillRect(x + 14, y + 2, 22, 14); // Đầu
            ctx.fillRect(x + 30, y + 10, 8, 8);   // Mõm
            ctx.fillRect(x + 8, y + 16, 26, 18);  // Thân
            ctx.fillRect(x + 2, y + 18, 10, 6);   // Tay ngắn
            ctx.fillRect(x + 4, y + 34, 8, 10);   // Đuôi dài
            
            // Chân chạy hoạt hoạ
            if (this.grounded) {
                if (Math.floor(animFrame / 6) % 2 === 0) {
                    ctx.fillRect(x + 14, y + 34, 5, 13); // Chân trái duỗi
                    ctx.fillRect(x + 24, y + 34, 5, 8);  // Chân phải co
                } else {
                    ctx.fillRect(x + 14, y + 34, 5, 8);  // Chân trái co
                    ctx.fillRect(x + 24, y + 34, 5, 13); // Chân phải duỗi
                }
            } else {
                // Khi nhảy chụm chân
                ctx.fillRect(x + 14, y + 34, 5, 11);
                ctx.fillRect(x + 24, y + 34, 5, 11);
            }
        }
    },
    update() {
        if (this.ducking && this.grounded) {
            this.width = 59;
            this.height = 27;
            this.y = 240;
        } else {
            this.width = 44;
            this.height = 47;
            this.y = 220;
        }

        this.dy += gravity;
        this.y += this.dy;

        if (this.y > 220) {
            this.y = 220;
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

// Khởi tạo mây
for (let i = 0; i < 3; i++) {
    clouds.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 80 + 20,
        width: 46,
        height: 14,
        speed: 1
    });
}

// Khởi tạo Tháp Ai Cập ở nền sau
for (let i = 0; i < 2; i++) {
    pyramids.push({
        x: i * 450 + 300,
        y: 170,
        width: 70,
        height: 97,
        speed: 1.5
    });
}

let obstacleTimer = 0;
let nextObstacleTime = 120;

function spawnObstacle() {
    const type = Math.random();
    if (type < 0.5) {
        // Xương rồng chuẩn Google
        obstacles.push({
            x: canvas.width,
            y: 215,
            width: 20,
            height: 50,
            type: "cactus"
        });
    } else {
        // Chim bay (vị trí ngang tầm đầu hoặc tầm cao)
        obstacles.push({
            x: canvas.width,
            y: 155, // Ngang tầm khủng long cúi đầu
            width: 42,
            height: 30,
            type: "bird"
        });
    }
}

// Điều khiển bàn phím
window.addEventListener("keydown", (e) => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        if (gameState === "START" || gameState === "GAMEOVER") {
            resetGame();
        } else {
            dino.jump();
        }
    }
    if (e.code === "ArrowDown") {
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

function resetGame() {
    gameState = "PLAYING";
    score = 0;
    gameSpeed = 6;
    obstacles = [];
    dino.y = 220;
    dino.dy = 0;
    dino.grounded = true;
    dino.ducking = false;
    obstacleTimer = 0;
}

function animate() {
    animFrame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Đổi màu bầu trời khi đạt 1000 điểm (Night mode chuẩn Google Dino)
    let isNight = score >= 1000;
    ctx.fillStyle = isNight ? "#202124" : "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    let textColor = isNight ? "#f1f3f4" : "#535353";
    let objectColor = isNight ? "#9aa0a6" : "#535353";

    // Vẽ Mặt Trời / Mặt Trăng chuẩn pixel
    ctx.fillStyle = objectColor;
    ctx.beginPath();
    ctx.arc(700, 60, 20, 0, Math.PI * 2);
    ctx.fill();

    // Vẽ Mây
    clouds.forEach(cloud => {
        if (gameState === "PLAYING") cloud.x -= cloud.speed;
        if (cloud.x + cloud.width < 0) {
            cloud.x = canvas.width;
            cloud.y = Math.random() * 80 + 20;
        }
        ctx.fillStyle = isNight ? "#3c4043" : "#d7d7d7";
        ctx.fillRect(cloud.x, cloud.y, cloud.width, cloud.height);
    });

    // Vẽ Tháp Ai Cập ở hậu cảnh
    pyramids.push();
    pyramids.forEach(p => {
        if (gameState === "PLAYING") p.x -= p.speed;
        if (p.x + p.width < 0) {
            p.x = canvas.width + Math.random() * 150;
        }
        ctx.fillStyle = isNight ? "#303134" : "#e0e0e0";
        ctx.beginPath();
        ctx.moveTo(p.x + p.width / 2, p.y);
        ctx.lineTo(p.x, p.y + p.height);
        ctx.lineTo(p.x + p.width, p.y + p.height);
        ctx.closePath();
        ctx.fill();
    });

    // Vẽ mặt đất (đường kẻ ngang chuẩn Google Dino)
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
            nextObstacleTime = Math.floor(Math.random() * 40) + 70 - Math.min(25, Math.floor(score / 100));
        }

        dino.update();
    }

    dino.draw();

    // Xử lý chướng ngại vật
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        if (gameState === "PLAYING") obs.x -= gameSpeed;

        ctx.fillStyle = objectColor;
        if (obs.type === "cactus") {
            // Vẽ xương rồng
            ctx.fillRect(obs.x + 6, obs.y, 8, 50);
            ctx.fillRect(obs.x, obs.y + 12, 6, 16);
            ctx.fillRect(obs.x + 14, obs.y + 20, 6, 16);
        } else {
            // Vẽ chim bay đập cánh hoạt hoạ
            let wingUp = Math.floor(animFrame / 10) % 2 === 0;
            ctx.fillRect(obs.x, obs.y + (wingUp ? 5 : 15), 12, 10); // Thân chim
            ctx.fillRect(obs.x + 12, obs.y + 10, 18, 8);
            if (wingUp) {
                ctx.fillRect(obs.x + 14, obs.y, 10, 8); // Cánh lên
            } else {
                ctx.fillRect(obs.x + 14, obs.y + 18, 10, 8); // Cánh xuống
            }
        }

        // Kiểm tra va chạm chính xác
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

    // Hiển thị điểm số chuẩn kiểu số điện tử Google
    ctx.fillStyle = textColor;
    ctx.font = "16px 'Courier New'";
    let hiStr = String(highScore).padStart(5, '0');
    let scStr = String(Math.floor(score)).padStart(5, '0');
    ctx.fillText("HI " + hiStr + "  " + scStr, canvas.width - 190, 30);

    // Màn hình bắt đầu / Game Over
    if (gameState === "START") {
        ctx.fillStyle = textColor;
        ctx.font = "14px 'Courier New'";
        ctx.textAlign = "center";
        ctx.fillText("NHẤN PHÍM CÁCH (SPACE) ĐỂ BẮT ĐẦU", canvas.width / 2, canvas.height / 2);
        ctx.textAlign = "left";
    } else if (gameState === "GAMEOVER") {
        // Biểu tượng Game Over chuẩn Google (dấu x và chữ restart icon)
        ctx.fillStyle = textColor;
        ctx.font = "18px 'Courier New'";
        ctx.textAlign = "center";
        ctx.fillText("G A M E   O V E R", canvas.width / 2, canvas.height / 2 - 10);
        ctx.font = "12px 'Courier New'";
        ctx.fillText("Nhấn PHÍM CÁCH để chơi lại", canvas.width / 2, canvas.height / 2 + 20);
        ctx.textAlign = "left";
    }

    requestAnimationFrame(animate);
}

animate();
</script>

</body>
</html>
"""

components.html(game_html, height=350, width=850)
