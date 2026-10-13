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
    <div class="instructions">Máy tính: [Space/↑] Nhảy cao, [↓] Cúi đầu | Điện thoại: Chạm để Nhảy, Vuốt xuống để Cúi</div>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let gameState = "START"; // START, PLAYING, GAMEOVER
let score = 0;
let highScore = 0;
let gameSpeed = 6;
let gravity = 0.6; // Trọng lực cân đối để nhảy cao và mượt
let animFrame = 0;

// Khủng long màu sắc tươi sáng, sinh động
const dino = {
    x: 60,
    y: 230,
    width: 48,
    height: 55,
    dy: 0,
    jumpPower: -13.5, // Tăng lực nhảy cao hơn đáng kể
    grounded: true,
    ducking: false,
    draw() {
        const x = this.x;
        const y = this.y;

        if (this.ducking) {
            // Khủng long cúi người né chim bay chéo
            ctx.fillStyle = "#00b894"; // Xanh ngọc tươi sáng
            ctx.fillRect(x, y + 22, 62, 33); // Thân dài
            ctx.fillRect(x + 40, y + 10, 24, 18); // Đầu cúi
            
            // Mắt và má hồng
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x + 54, y + 13, 4, 4);
            ctx.fillStyle = "#fd79a8";
            ctx.fillRect(x + 56, y + 18, 5, 4);

            // Chân cúi hoạt hoạ
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
            
            // Đầu & Miệng
            ctx.fillRect(x + 18, y, 26, 16);
            ctx.fillRect(x + 36, y + 8, 12, 10);
            
            // Mắt & Má
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(x + 36, y + 3, 4, 4);
            ctx.fillStyle = "#000000";
            ctx.fillRect(x + 38, y + 4, 2, 2);
            ctx.fillStyle = "#fd79a8";
            ctx.fillRect(x + 38, y + 10, 5, 4);

            // Thân & Tay nhỏ đáng yêu
            ctx.fillStyle = "#00b894";
            ctx.fillRect(x + 10, y + 14, 26, 24);
            ctx.fillStyle = "#55efc4";
            ctx.fillRect(x + 4, y + 18, 10, 6); // Tay

            // Đuôi dài nhông vểnh
            ctx.fillStyle = "#00b894";
            ctx.fillRect(x - 2, y + 12, 12, 8);
            ctx.fillRect(x - 8, y + 8, 8, 6);

            // Chân chạy hoạt hoạ năng động
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
                // Nhảy lên chụm chân
                ctx.fillRect(x + 14, y + 38, 7, 14);
                ctx.fillRect(x + 26, y + 38, 7, 14);
            }
        }
    },
    update() {
        if (this.ducking && this.grounded) {
            this.width = 62;
            this.height = 33;
            this.y = 252;
        } else {
            this.width = 48;
            this.height = 55;
            this.y = 230;
        }

        this.dy += gravity;
        this.y += this.dy;

        if (this.y > 230) {
            this.y = 230;
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

// Khởi tạo mây bay màu trắng sáng
for (let i = 0; i < 4; i++) {
    clouds.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 100 + 20,
        width: 60,
        height: 20,
        speed: 1
    });
}

// Khởi tạo tháp Ai Cập nền sau màu cam đất/hồng pastel
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
let nextObstacleTime = 100;

function spawnObstacle() {
    const type = Math.random();
    if (type < 0.5) {
        // Xương rồng đa dạng (Xương rồng đơn cao hoặc chùm xương rồng sinh động)
        let variant = Math.floor(Math.random() * 3);
        obstacles.push({
            x: canvas.width,
            y: 225,
            width: variant === 2 ? 38 : 22,
            height: 60,
            type: "cactus",
            variant: variant
        });
    } else {
        // Chim bay chéo từ trên cao lao xuống để ép khủng long phải cúi đầu
        obstacles.push({
            x: canvas.width,
            y: 130, // Bắt đầu ở trên cao
            targetY: 200, // Lao dần xuống tầm trung
            width: 48,
            height: 32,
            type: "bird",
            dy: 0.2
        });
    }
}

// Điều khiển bàn phím PC
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

// Điều khiển cảm ứng điện thoại
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
    dino.y = 230;
    dino.dy = 0;
    dino.grounded = true;
    dino.ducking = false;
    obstacleTimer = 0;
}

function animate() {
    animFrame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Đổi màu bầu trời khi đạt 1000 điểm (Chuyển từ ban ngày sáng rực sang Hoàng hôn/Ban đêm rực rỡ)
    let isNight = score >= 1000;
    let skyGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    if (!isNight) {
        skyGrad.addColorStop(0, "#74b9ff"); // Xanh trời sáng
        skyGrad.addColorStop(1, "#dfe6e9");
    } else {
        skyGrad.addColorStop(0, "#2d3436"); // Hoàng hôn/Đêm huyền ảo
        skyGrad.addColorStop(1, "#636e72");
    }
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Vẽ Mặt Trời tươi sáng / Mặt trăng vàng
    ctx.fillStyle = isNight ? "#ffeaa7" : "#fdcb6e";
    ctx.beginPath();
    ctx.arc(730, 60, 25, 0, Math.PI * 2);
    ctx.fill();

    // Vẽ mây trời bồng bềnh
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

    // Vẽ Tháp Ai Cập hậu cảnh màu sắc nghệ thuật
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
        // Cửa tháp
        ctx.fillStyle = isNight ? "#636e72" : "#e17055";
        ctx.fillRect(p.x + p.width/2 - 7, p.y + p.height - 30, 14, 30);
    });

    // Vẽ mặt đất màu xanh cỏ tươi / nâu ấm
    ctx.fillStyle = isNight ? "#2d3436" : "#00b894";
    ctx.fillRect(0, 285, canvas.width, 65);
    ctx.fillStyle = isNight ? "#636e72" : "#55efc4";
    ctx.fillRect(0, 285, canvas.width, 8); // Viền cỏ nổi bật

    if (gameState === "PLAYING") {
        // Tốc độ tăng dần mượt mà theo thời gian và điểm số
        gameSpeed = 6 + Math.floor(score / 120);
        score += 0.05;

        obstacleTimer++;
        if (obstacleTimer > nextObstacleTime) {
            spawnObstacle();
            obstacleTimer = 0;
            nextObstacleTime = Math.floor(Math.random() * 40) + 65 - Math.min(25, Math.floor(score / 100));
        }

        dino.update();
    }

    dino.draw();

    // Xử lý chướng ngại vật
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        if (gameState === "PLAYING") {
            obs.x -= gameSpeed;
            if (obs.type === "bird") {
                obs.y += obs.dy; // Chim bay chéo xuống dưới dần
                if (obs.y > 215 || obs.y < 120) obs.dy *= -1; // Dao động chéo lên xuống linh hoạt
            }
        }

        if (obs.type === "cactus") {
            // Xương rồng màu xanh lá cây đậm tươi tắn, đa dạng kiểu dáng
            ctx.fillStyle = "#00b894";
            if (obs.variant === 0) {
                // Xương rồng đơn cao
                ctx.fillRect(obs.x + 6, obs.y, 10, 60);
                ctx.fillRect(obs.x, obs.y + 18, 6, 16);
                ctx.fillRect(obs.x + 16, obs.y + 28, 6, 16);
            } else if (obs.variant === 1) {
                // Xương rồng đôi
                ctx.fillRect(obs.x + 2, obs.y + 10, 8, 50);
                ctx.fillRect(obs.x + 12, obs.y, 9, 60);
                ctx.fillRect(obs.x + 21, obs.y + 20, 6, 18);
            } else {
                // Chùm xương rồng lớn đa nhánh
                ctx.fillRect(obs.x + 4, obs.y + 5, 9, 55);
                ctx.fillRect(obs.x, obs.y + 22, 6, 18);
                ctx.fillRect(obs.x + 16, obs.y + 12, 8, 48);
                ctx.fillRect(obs.x + 26, obs.y + 25, 7, 20);
            }
        } else {
            // Chim bay màu hồng/đỏ cam cực đẹp, bay chéo né bằng cách cúi đầu
            ctx.fillStyle = "#e17055";
            let wingUp = Math.floor(animFrame / 8) % 2 === 0;
            
            // Thân chim & mỏ nhọn
            ctx.fillRect(obs.x + 8, obs.y + 10, 26, 12);
            ctx.fillRect(obs.x, obs.y + 13, 10, 6); 
            // Mắt chim
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(obs.x + 24, obs.y + 12, 3, 3);
            
            // Cánh chim vẫy
            ctx.fillStyle = "#fab1a0";
            if (wingUp) {
                ctx.fillRect(obs.x + 14, obs.y - 2, 12, 12); // Cánh vươn lên
            } else {
                ctx.fillRect(obs.x + 14, obs.y + 16, 12, 12); // Cánh cụp xuống
            }
        }

        // Kiểm tra va chạm chính xác chuẩn xác
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

    // Hiển thị điểm số màu sắc bắt mắt
    ctx.fillStyle = isNight ? "#dfe6e9" : "#2d3436";
    ctx.font = "bold 18px 'Segoe UI'";
    let hiStr = String(highScore).padStart(5, '0');
    let scStr = String(Math.floor(score)).padStart(5, '0');
    ctx.fillText("HI: " + hiStr + "   SCORE: " + scStr, canvas.width - 240, 35);

    // Màn hình bắt đầu & Game Over
    if (gameState === "START") {
        ctx.fillStyle = "rgba(0,0,0,0.4)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 22px 'Segoe UI'";
        ctx.textAlign = "center";
        ctx.fillText("NHẤN PHÍM CÁCH HOẶC CHẠM ĐỂ BẮT ĐẦU", canvas.width / 2, canvas.height / 2);
        ctx.textAlign = "left";
    } else if (gameState === "GAMEOVER") {
        ctx.fillStyle = "rgba(0,0,0,0.5)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ff7675";
        ctx.font = "bold 26px 'Segoe UI'";
        ctx.textAlign = "center";
        ctx.fillText("TRÒ CHƠI KẾT THÚC", canvas.width / 2, canvas.height / 2 - 15);
        ctx.fillStyle = "#ffffff";
        ctx.font = "16px 'Segoe UI'";
        ctx.fillText("Chạm hoặc nhấn phím để chơi lại", canvas.width / 2, canvas.height / 2 + 25);
        ctx.textAlign = "left";
    }

    requestAnimationFrame(animate);
}

animate();
</script>

</body>
</html>
"""

components.html(game_html, height=380, width=870)
