import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(page_title="Dino Pixel Adventure", page_icon="🦖", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #2ecc71; font-family: monospace;'>🦖 DINO WORLD PIXEL ADVENTURE</h1>
    <p style='text-align: center; color: #b2bec3; font-family: monospace;'>Hành trình xuyên lục địa: Sa mạc Ai Cập ➔ Rừng Amazon ➔ Nước Úc.<br>Nhấn <b>Spacebar</b> hoặc <b>Mũi tên lên</b> / <b>Click chuột</b> để nhảy!</p>
""", unsafe_allow_html=True)

# Mã nguồn HTML, CSS và JavaScript hoàn chỉnh phong cách Pixel Art 2D
game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Dino Pixel Adventure</title>
    <style>
        body {
            margin: 0;
            background-color: #0f0f0f;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        canvas {
            border: 4px solid #fff;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            box-shadow: 0 0 25px rgba(46, 204, 113, 0.4);
            background: #222;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="800" height="300"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Biến trạng thái trò chơi
let score = 0;
let highScore = 0;
let gameSpeed = 5;
let isGameOver = false;
let isDay = true;
let worldTimer = 0;
let currentWorld = 0; // 0: Sa mạc Ai Cập, 1: Rừng Amazon, 2: Nước Úc

// Cấu hình các Thế giới Pixel
const worlds = [
    { name: "Sa mạc Ai Cập", skyDay: "#70c5ce", skyNight: "#0a1128", ground: "#d1a153", groundLine: "#8c6239", obstacle: "#5c4033" },
    { name: "Rừng Amazon", skyDay: "#3498db", skyNight: "#112233", ground: "#27ae60", groundLine: "#145a32", obstacle: "#196f3d" },
    { name: "Nước Úc", skyDay: "#e67e22", skyNight: "#1b2631", ground: "#ba4a00", groundLine: "#6e2c00", obstacle: "#512e5f" }
];

// Đối tượng Khủng Long Pixel 2D (có hiệu ứng chạy động)
let dino = {
    x: 60,
    y: 195,
    width: 32,
    height: 40,
    vy: 0,
    gravity: 0.75,
    jumpPower: -13.5, // Lực nhảy tối ưu để vượt qua mọi chướng ngại vật
    isJumping: false,
    animFrame: 0,
    draw() {
        ctx.fillStyle = "#2ecc71"; // Màu xanh khủng long
        
        // Thân khủng long
        ctx.fillRect(this.x + 6, this.y + 14, 20, 20);
        // Đầu khủng long
        ctx.fillRect(this.x + 16, this.y + 2, 16, 14);
        // Mắt pixel đen
        ctx.fillStyle = "#000";
        ctx.fillRect(this.x + 26, this.y + 5, 3, 3);
        // Miệng
        ctx.fillStyle = "#27ae60";
        ctx.fillRect(this.x + 28, this.y + 9, 4, 3);
        // Tay nhỏ pixel
ctx.fillRect(this.x + 22, this.y + 16, 4, 3);
        
        // Hoạt ảnh chân chạy pixel thay đổi luân phiên
        ctx.fillStyle = "#27ae60";
        if (this.isJumping) {
            // Chân khi nhảy co lên
            ctx.fillRect(this.x + 8, this.y + 34, 4, 6);
            ctx.fillRect(this.x + 18, this.y + 34, 4, 6);
        } else {
            // Chân khi chạy bộ
            if (Math.floor(this.animFrame / 8) % 2 === 0) {
                ctx.fillRect(this.x + 8, this.y + 34, 5, 8);
                ctx.fillRect(this.x + 18, this.y + 34, 3, 6);
            } else {
                ctx.fillRect(this.x + 8, this.y + 34, 3, 6);
                ctx.fillRect(this.x + 18, this.y + 34, 5, 8);
            }
        }
        this.animFrame++;
    },
    jump() {
        if (!this.isJumping) {
            this.vy = this.jumpPower;
            this.isJumping = true;
        }
    },
    update() {
        this.vy += this.gravity;
        this.y += this.vy;
        if (this.y > 195) {
            this.y = 195;
            this.vy = 0;
            this.isJumping = false;
        }
    }
};

let obstacles = [];
let clouds = [];

// Khởi tạo mây trời pixel
for(let i=0; i<4; i++) {
    clouds.push({
        x: Math.random() * canvas.width,
        y: 30 + Math.random() * 60,
        speed: 0.5 + Math.random() * 0.8,
        width: 40 + Math.random() * 30
    });
}

class Obstacle {
    constructor() {
        this.width = 22 + Math.random() * 14;
        this.height = 32 + Math.random() * 22;
        this.x = canvas.width;
        this.y = 235 - this.height;
    }
    draw() {
        ctx.fillStyle = worlds[currentWorld].obstacle;
        // Vẽ chướng ngại vật khối pixel bén nhọn
        ctx.fillRect(this.x, this.y, this.width, this.height);
        // Chi tiết điểm nhấn pixel trắng tạo độ nổi 3D cổ điển
        ctx.fillStyle = "#fff";
        ctx.fillRect(this.x + 3, this.y + 4, 3, 3);
        ctx.fillRect(this.x + this.width - 6, this.y + 12, 3, 3);
    }
    update() {
        this.x -= gameSpeed;
    }
}

// Bắt sự kiện bàn phím
window.addEventListener("keydown", e => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        if (isGameOver) {
            resetGame();
        } else {
            dino.jump();
        }
        e.preventDefault(); // Ngăn cuộn trang
    }
});

// Bắt sự kiện click chuột/chạm màn hình
window.addEventListener("click", () => {
    if (isGameOver) {
        resetGame();
    } else {
        dino.jump();
    }
});

function resetGame() {
    score = 0;
    gameSpeed = 5;
    obstacles = [];
    isGameOver = false;
    currentWorld = 0;
    dino.y = 195;
}

let obstacleTimer = 0;

function gameLoop() {
    // Chu kỳ ngày đêm & thay đổi thế giới pixel theo điểm số
    worldTimer++;
    if (worldTimer % 700 === 0) {
        isDay = !isDay;
    }
    if (worldTimer % 1400 === 0) {
currentWorld = (currentWorld + 1) % worlds.length;
    }

    // 1. Vẽ Bầu trời
    ctx.fillStyle = isDay ? worlds[currentWorld].skyDay : worlds[currentWorld].skyNight;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Vẽ Mặt trời / Mặt trăng pixel
    ctx.fillStyle = isDay ? "#f1c40f" : "#ecf0f1";
    ctx.fillRect(700, 35, 32, 32);
    // Tạo hiệu ứng ô lưới pixel cho mặt trăng/mặt trời
    ctx.fillStyle = isDay ? "#d4ac0d" : "#bdc3c7";
    ctx.fillRect(708, 43, 8, 8);

    // 2. Vẽ Mây pixel trôi
    ctx.fillStyle = isDay ? "rgba(255, 255, 255, 0.7)" : "rgba(255, 255, 255, 0.15)";
    clouds.forEach(cloud => {
        cloud.x -= cloud.speed;
        if (cloud.x < -60) cloud.x = canvas.width + 50;
        ctx.fillRect(cloud.x, cloud.y, cloud.width, 12);
        ctx.fillRect(cloud.x + 10, cloud.y - 8, cloud.width - 20, 8);
    });

    // 3. Vẽ Mặt đất Pixel 2D
    ctx.fillStyle = worlds[currentWorld].ground;
    ctx.fillRect(0, 235, canvas.width, 65);
    
    // Đường viền pixel mặt đất cắt lớp phong cách retro
    ctx.fillStyle = worlds[currentWorld].groundLine;
    ctx.fillRect(0, 235, canvas.width, 5);
    // Họa tiết chấm sỏi pixel trên mặt đất
    ctx.fillStyle = "rgba(0,0,0,0.15)";
    for(let i = 0; i < canvas.width; i += 40) {
        ctx.fillRect((i - (score * 10) % 40), 250, 8, 4);
        ctx.fillRect((i + 20 - (score * 10) % 40), 270, 6, 4);
    }

    if (!isGameOver) {
        dino.update();
        score += 0.08;
        gameSpeed = 5 + Math.floor(score / 120); // Tăng dần độ khó

        // Sinh chướng ngại vật
        obstacleTimer++;
        if (obstacleTimer > 85 + Math.random() * 45) {
            obstacles.push(new Obstacle());
            obstacleTimer = 0;
        }
    }

    // Cập nhật và vẽ chướng ngại vật
    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].update();
        obstacles[i].draw();

        // Kiểm tra va chạm chính xác chuẩn pixel (AABB)
        if (
            dino.x + 4 < obstacles[i].x + obstacles[i].width - 4 &&
            dino.x + dino.width - 4 > obstacles[i].x + 4 &&
            dino.y + 4 < obstacles[i].y + obstacles[i].height &&
            dino.y + dino.height > obstacles[i].y
        ) {
            isGameOver = true;
            if (score > highScore) highScore = Math.floor(score);
        }

        // Xóa vật cản khi ra ngoài màn hình
        if (obstacles[i].x < -50) {
            obstacles.splice(i, 1);
        }
    }

    dino.draw();

    // Hiển thị giao diện điểm số phong cách Retro Pixel UI
    ctx.fillStyle = isDay ? "#2c3e50" : "#ecf0f1";
    ctx.font = "bold 15px 'Courier New'";
    ctx.fillText("ĐIỂM: " + Math.floor(score), 25, 30);
    ctx.fillText("KỶ LỤC: " + highScore, 25, 55);
    ctx.fillText("VÙNG ĐẤT: " + worlds[currentWorld].name, 25, 80);

    // Màn hình Game Over
    if (isGameOver) {
ctx.fillStyle = "rgba(15, 15, 15, 0.85)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#e74c3c";
        ctx.font = "bold 26px 'Courier New'";
        ctx.fillText("💀 KHỦNG LONG VẤP NGÃ! GAME OVER", 135, 125);
        
        ctx.fillStyle = "#fff";
        ctx.font = "16px 'Courier New'";
        ctx.fillText("Bấm [SPACEBAR] hoặc [CLICK CHUỘT] để chơi lại", 175, 175);
    }

    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>

</body>
</html>
"""

components.html(game_code, height=350)
