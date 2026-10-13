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
    for (let i = obstacles
