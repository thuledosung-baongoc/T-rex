import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino T-Rex Deluxe", page_icon="🦖", layout="centered")

# Mã nguồn HTML, CSS và JavaScript của trò chơi
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dino Game Deluxe</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #222;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Courier New', Courier, monospace;
            overflow: hidden;
        }
        canvas {
            background: linear-gradient(to bottom, #b7d2ff, #ffffff);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-radius: 10px;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="800" height="400"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Trạng thái trò chơi
let gameState = "START"; // START, PLAYING, GAMEOVER
let score = 0;
let highScore = 0;
let gameSpeed = 5;
let gravity = 0.6;

// Khủng long
const dino = {
    x: 50,
    y: 290,
    width: 40,
    height: 50,
    dy: 0,
    jumpPower: -11,
    grounded: true,
    ducking: false,
    draw() {
        ctx.fillStyle = "#535353";
        if (this.ducking) {
            ctx.fillRect(this.x, this.y + 20, 60, 30); // Hình dạng cúi
        } else {
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }
    },
    update() {
        if (this.ducking && this.grounded) {
            this.height = 30;
            this.y = 310;
        } else {
            this.height = 50;
            this.y = 290;
        }

        this.dy += gravity;
        this.y += this.dy;

        // Giới hạn mặt đất
        if (this.y > 290) {
            this.y = 290;
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

// Mảng chướng ngại vật và cảnh vật
let obstacles = [];
let clouds = [];
let pyramids = [];

// Khởi tạo mây
for (let i = 0; i < 3; i++) {
    clouds.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 100 + 30,
        width: 60,
        height: 20,
        speed: 1
    });
}

// Khởi tạo tháp Ai Cập ở nền sau
for (let i = 0; i < 2; i++) {
    pyramids.push({
        x: i * 500 + 200,
        y: 240,
        width: 100,
        height: 100,
        speed: 1.5
    });
}

// Bộ đếm sinh chướng ngại vật
let obstacleTimer = 0;
let nextObstacleTime = 100;

function spawnObstacle() {
    const type = Math.random();
    if (type < 0.5) {
        // Xương rồng (Nhảy qua)
        obstacles.push({
            x: canvas.width,
            y: 300,
            width: 25,
            height: 40,
            type: "cactus",
            color: "#2e7d32"
        });
    } else {
        // Chim bay (Cúi xuống)
        obstacles.push({
            x: canvas.width,
            y: 220, // Bay ở trên cao
            width: 40,
            height: 25,
            type: "bird",
            color: "#d32f2f"
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
    gameSpeed = 5;
    obstacles = [];
    dino.y = 290;
    dino.dy = 0;
    dino.grounded = true;
    obstacleTimer = 0;
}

// Xử lý màu bầu trời chuyển dần khi đạt 1000 điểm
function getSkyColor(currentScore) {
    if (currentScore < 200) return "#b7d2ff"; // Sáng sớm
    if (currentScore < 500) return "#ffcc80"; // Hoàng hôn
    if (currentScore < 1000) return "#7986cb"; // Chập tối
    let t = Math.min(1, (currentScore - 1000) / 1000);
    return "#1a237e"; // Ban đêm (từ 1000đ trở đi)
}

// Vòng lặp game
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Vẽ bầu trời thay đổi màu
    let skyColor = getSkyColor(score);
    ctx.fillStyle = skyColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Vẽ Mặt Trời / Mặt Trăng
    ctx.fillStyle = score >= 1000 ? "#ffffff" : "#ffeb3b";
    ctx.beginPath();
    ctx.arc(700, 80, 30, 0, Math.PI * 2);
    ctx.fill();

    // 2. Vẽ Mây
    ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
    clouds.forEach(cloud => {
        if (gameState === "PLAYING") cloud.x -= cloud.speed;
        if (cloud.x + cloud.width < 0) {
            cloud.x = canvas.width;
            cloud.y = Math.random() * 100 + 30;
        }
        ctx.fillRect(cloud.x, cloud.y, cloud.width, cloud.height);
    });

    // 3. Vẽ Tháp Ai Cập (Pyramid) nền sau
    ctx.fillStyle = score >= 1000 ? "#37474f" : "#d7ccc8";
    pyramids.forEach(p => {
        if (gameState === "PLAYING") p.x -= p.speed;
        if (p.x + p.width < 0) {
            p.x = canvas.width + Math.random() * 100;
        }
        ctx.beginPath();
        ctx.moveTo(p.x + p.width / 2, p.y);
        ctx.lineTo(p.x, p.y + p.height);
        ctx.lineTo(p.x + p.width, p.y + p.height);
        ctx.closePath();
        ctx.fill();
    });

    // Vẽ mặt đất
    ctx.fillStyle = score >= 1000 ? "#263238" : "#8d6e63";
    ctx.fillRect(0, 340, canvas.width, 60);

    if (gameState === "PLAYING") {
        // Tăng tốc độ theo thời gian
        gameSpeed = 5 + Math.floor(score / 200);
        score += 0.05;

        // Sinh chướng ngại vật
        obstacleTimer++;
        if (obstacleTimer > nextObstacleTime) {
            spawnObstacle();
            obstacleTimer = 0;
            nextObstacleTime = Math.floor(Math.random() * 50) + 70 - Math.min(30, Math.floor(score / 100));
        }

        dino.update();
    }

    dino.draw();

    // 4. Xử lý Chướng ngại vật
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        if (gameState === "PLAYING") obs.x -= gameSpeed;

        ctx.fillStyle = obs.color;
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);

        // Kiểm tra va chạm chính xác (AABB Collision)
        if (
            dino.x < obs.x + obs.width &&
            dino.x + dino.width > obs.x &&
            dino.y < obs.y + obs.height &&
            dino.y + dino.height > obs.y
        ) {
            gameState = "GAMEOVER";
            if (Math.floor(score) > highScore) {
                highScore = Math.floor(score);
            }
        }

        // Xóa chướng ngại vật khi ra ngoài màn hình
        if (obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
        }
    }

    // Hiển thị Điểm số
    ctx.fillStyle = score >= 1000 ? "#ffffff" : "#333";
    ctx.font = "20px 'Courier New'";
    ctx.fillText("HI: " + String(highScore).padStart(5, '0'), canvas.width - 180, 30);
    ctx.fillText("SC: " + String(Math.floor(score)).padStart(5, '0'), canvas.width - 90, 30);

    // Màn hình Bắt đầu / Kết thúc
    if (gameState === "START") {
        ctx.fillStyle = "rgba(0,0,0,0.6)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ffffff";
        ctx.font = "24px 'Courier New'";
        ctx.textAlign = "center";
        ctx.fillText("NHẤN PHÍM CÁCH (SPACE) ĐỂ BẮT ĐẦU", canvas.width / 2, canvas.height / 2 - 10);
        ctx.font = "16px 'Courier New'";
        ctx.fillText("Mũi tên lên: Nhảy | Mũi tên xuống: Cúi người", canvas.width / 2, canvas.height / 2 + 30);
        ctx.textAlign = "left";
    } else if (gameState === "GAMEOVER") {
        ctx.fillStyle = "rgba(0,0,0,0.6)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ff5252";
        ctx.font = "30px 'Courier New'";
        ctx.textAlign = "center";
        ctx.fillText("TRÒ CHƠI KẾT THÚC", canvas.width / 2, canvas.height / 2 - 20);
        ctx.fillStyle = "#ffffff";
        ctx.font = "18px 'Courier New'";
        ctx.fillText("Nhấn PHÍM CÁCH để chơi lại", canvas.width / 2, canvas.height / 2 + 20);
        ctx.textAlign = "left";
    }

    requestAnimationFrame(animate);
}

// Chạy game
animate();
</script>

</body>
</html>
"""

components.html(game_html, height=450, width=850)
