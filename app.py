import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(page_title="T-Rex Runner Advanced", page_icon="🦖", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #2ecc71; font-family: monospace;'>🦖 T-REX RUNNER: XƯƠNG RỒNG & CHIM BAY</h1>
    <p style='text-align: center; color: #b2bec3; font-family: monospace;'>Nhấn <b>Spacebar</b> hoặc nút <b>NHẢY</b> để né xương rồng | Nhấn <b>Mũi tên xuống</b> hoặc nút <b>CÚI</b> để né chim bay!</p>
""", unsafe_allow_html=True)

# Mã nguồn HTML, CSS và JavaScript hoàn chỉnh
game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>T-Rex Runner Advanced</title>
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

let score = 0;
let highScore = 0;
let gameSpeed = 5;
let isGameOver = false;

// Đối tượng Khủng Long T-Rex Pixel có trạng thái cúi
let dino = {
    x: 50,
    y: 165,
    width: 32,
    height: 36,
    normalHeight: 36,
    duckHeight: 22,
    vy: 0,
    gravity: 0.75,
    jumpPower: -13.5,
    isJumping: false,
    isDucking: false,
    animFrame: 0,
    draw() {
        ctx.fillStyle = "#535353";
if (this.isDucking && !this.isJumping) {
            // Tư thế cúi người
            ctx.fillRect(this.x, this.y + 14, 40, 22); // Thân dài ra, thấp xuống
            ctx.fillRect(this.x + 24, this.y + 6, 16, 12); // Đầu cúi thấp
            ctx.fillStyle = "#fff";
            ctx.fillRect(this.x + 34, this.y + 8, 3, 3); // Mắt
        } else {
            // Tư thế đứng chạy bình thường
            ctx.fillRect(this.x + 6, this.y + 12, 18, 16);
            ctx.fillRect(this.x + 14, this.y, 16, 14);
            ctx.fillStyle = "#fff";
            ctx.fillRect(this.x + 24, this.y + 3, 3, 3); // Mắt
            ctx.fillStyle = "#535353";
            ctx.fillRect(this.x + 20, this.y + 14, 4, 3);
            
            // Chân chạy/nhảy
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
            this.vy = this.jumpPower;
            this.isJumping = true;
            this.isDucking = false;
            this.height = this.normalHeight;
        }
    },
    duck(active) {
        if (!this.isJumping) {
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

// Xương rồng (chướng ngại vật dưới đất)
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

// Chim bay (chướng ngại vật trên không - khủng long phải cúi mới né được)
class Bird {
constructor() {
        this.width = 30;
        this.height = 20;
        this.x = canvas.width;
        // Đặt độ cao vừa phải để bắt buộc phải cúi đầu hoặc nhảy chuẩn
        this.y = 145; 
        this.type = 'bird';
        this.animFrame = 0;
    }
    draw() {
        ctx.fillStyle = "#8e44ad"; // Màu chim pixel
        ctx.fillRect(this.x, this.y + 6, 30, 10); // Thân chim
        ctx.fillRect(this.x + 8, this.y, 10, 8); // Đầu chim
        
        // Cánh chim vỗ lên xuống theo khung hình
        ctx.fillStyle = "#9b59b6";
        if (Math.floor(this.animFrame / 10) % 2 === 0) {
            ctx.fillRect(this.x + 12, this.y - 6, 8, 8); // Cánh giơ lên
        } else {
            ctx.fillRect(this.x + 12, this.y + 14, 8, 8); // Cánh cụp xuống
        }
        this.animFrame++;
    }
    update() {
        this.x -= gameSpeed;
    }
}

function resetGame() {
    score = 0;
    gameSpeed = 5;
    obstacles = [];
    isGameOver = false;
    dino.y = 165;
    dino.height = dino.normalHeight;
    dino.isDucking = false;
}

// Bắt sự kiện bàn phím
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

// Bắt sự kiện click các nút ảo trên màn hình
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
    ctx.fillStyle = "#f7f7f7";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Vẽ đường mặt đất
    ctx.strokeStyle = "#535353";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 200);
    ctx.lineTo(canvas.width, 200);
    ctx.stroke();

    if (!isGameOver) {
        dino.update();
        score += 0.08;
        gameSpeed = 5 + Math.floor(score / 100);

        // Sinh chướng ngại vật ngẫu nhiên (Xương rồng hoặc Chim bay)
        obstacleTimer++;
        if (obstacleTimer > 85 + Math.random() * 50) {
            if (score > 30 && Math.random() > 0.5) {
                obstacles.push(new Bird()); // Sau khi đạt 30 điểm có xuất hiện chim bay
            } else {
obstacles.push(new Cactus());
            }
            obstacleTimer = 0;
        }
    }

    // Cập nhật và vẽ chướng ngại vật
    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].update();
        obstacles[i].draw();

        // Kiểm tra va chạm chuẩn xác (AABB)
        if (
            dino.x + 4 < obstacles[i].x + obstacles[i].width - 4 &&
            dino.x + dino.width - 4 > obstacles[i].x + 4 &&
            dino.y + 4 < obstacles[i].y + obstacles[i].height &&
            dino.y + dino.height > obstacles[i].y
        ) {
            isGameOver = true;
            if (score > highScore) highScore = Math.floor(score);
        }

        if (obstacles[i].x < -40) {
            obstacles.splice(i, 1);
        }
    }

    dino.draw();

    // Hiển thị điểm số
    ctx.fillStyle = "#535353";
    ctx.font = "bold 16px 'Courier New'";
    ctx.fillText("HIỆN TẠI: " + Math.floor(score), 600, 30);
    ctx.fillText("KỶ LỤC: " + highScore, 600, 55);

    if (isGameOver) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#e74c3c";
        ctx.font = "bold 24px 'Courier New'";
        ctx.fillText("💀 GAME OVER - VẤP NGÃ RỒI", 220, 100);
        
        ctx.fillStyle = "#fff";
        ctx.font = "15px 'Courier New'";
        ctx.fillText("Bấm [SPACEBAR] hoặc nút [NHẢY] để chơi lại", 215, 145);
    }

    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>

</body>
</html>
"""

components.html(game_code, height=350)
