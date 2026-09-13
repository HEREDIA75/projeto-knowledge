const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');

context.scale(20, 20);

// Definição das peças com cores Neon
const SHAPES = {
    'I': { blocks: [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], color: '#00ffff' },
    'O': { blocks: [[1,1],[1,1]], color: '#ffff00' },
    'T': { blocks: [[0,1,0],[1,1,1],[0,0,0]], color: '#ff00ff' },
    'S': { blocks: [[0,1,1],[1,1,0],[0,0,0]], color: '#00ff00' },
    'Z': { blocks: [[1,1,0],[0,1,1],[0,0,0]], color: '#ff0000' },
    'J': { blocks: [[1,0,0],[1,1,1],[0,0,0]], color: '#0044ff' },
    'L': { blocks: [[0,0,1],[1,1,1],[0,0,0]], color: '#ff8800' }
};

const PIECE_TYPES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];

// Estado do Jogo
const arena = createMatrix(12, 20);
const player = {
    pos: {x: 0, y: 0},
    matrix: null,
    color: '#fff',
    score: 0,
    lines: 0,
    level: 1
};

function createMatrix(w, h) {
    const matrix = [];
    while (h--) {
        matrix.push(new Array(w).fill(0));
    }
    return matrix;
}

function collide(arena, player) {
    const [m, o] = [player.matrix, player.pos];
    for (let y = 0; y < m.length; ++y) {
        for (let x = 0; x < m[y].length; ++x) {
            if (m[y][x] !== 0 &&
               (arena[y + o.y] && arena[y + o.y][x + o.x]) !== 0) {
                return true;
            }
        }
    }
    return false;
}

function merge(arena, player) {
    player.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                arena[y + player.pos.y][x + player.pos.x] = player.color;
            }
        });
    });
}

function rotate(matrix, dir) {
    for (let y = 0; y < matrix.length; ++y) {
        for (let x = 0; x < y; ++x) {
            [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
        }
    }
    if (dir > 0) {
        matrix.forEach(row => row.reverse());
    } else {
        matrix.reverse();
    }
}

function arenaSweep() {
    let rowCount = 1;
    outer: for (let y = arena.length - 1; y >= 0; --y) {
        for (let x = 0; x < arena[y].length; ++x) {
            if (arena[y][x] === 0) {
                continue outer;
            }
        }
        const row = arena.splice(y, 1)[0].fill(0);
        arena.unshift(row);
        ++y;

        player.score += rowCount * 10;
        player.lines += 1;
        rowCount *= 2;
    }
}

function drawMatrix(matrix, offset) {
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                // Efeito Neon (Glow)
                context.shadowBlur = 8;
                context.shadowColor = typeof value === 'string' ? value : player.color;
                context.fillStyle = typeof value === 'string' ? value : player.color;
                context.fillRect(x + offset.x, y + offset.y, 1, 1);
                
                // Borda interna brilhante
                context.lineWidth = 0.05;
                context.strokeStyle = '#ffffff';
                context.strokeRect(x + offset.x, y + offset.y, 1, 1);
            }
        });
    });
}

function draw() {
    context.fillStyle = '#0d0d1a';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    // Desenhar grade de fundo estilo Synthwave
    context.shadowBlur = 0;
    context.strokeStyle = 'rgba(0, 255, 255, 0.05)';
    context.lineWidth = 0.02;
    for(let x=0; x<12; x++) context.strokeRect(x, 0, 0, 20);
    for(let y=0; y<20; y++) context.strokeRect(0, y, 12, 0);

    drawMatrix(arena, {x: 0, y: 0});
    drawMatrix(player.matrix, player.pos);
}

function playerDrop() {
    player.pos.y++;
    if (collide(arena, player)) {
        player.pos.y--;
        merge(arena, player);
        playerReset();
        arenaSweep();
    }
    dropCounter = 0;
}

function playerMove(dir) {
    player.pos.x += dir;
    if (collide(arena, player)) {
        player.pos.x -= dir;
    }
}

function playerReset() {
    const type = PIECE_TYPES[Math.floor(Math.random() * PIECE_TYPES.length)];
    const piece = SHAPES[type];
    player.matrix = piece.blocks;
    player.color = piece.color;
    player.pos.y = 0;
    player.pos.x = Math.floor(arena[0].length / 2) - Math.floor(player.matrix[0].length / 2);

    if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
        player.score = 0;
        player.lines = 0;
    }
}

function playerRotate(dir) {
    const pos = player.pos.x;
    let offset = 1;
    rotate(player.matrix, dir);
    while (collide(arena, player)) {
        player.pos.x += offset;
        offset = -(offset + (offset > 0 ? 1 : -1));
        if (offset > player.matrix[0].length) {
            rotate(player.matrix, -dir);
            player.pos.x = pos;
            return;
        }
    }
}

let dropCounter = 0;
let dropInterval = 1000;
let lastTime = 0;

function update(time = 0) {
    const deltaTime = time - lastTime;
    lastTime = time;

    dropCounter += deltaTime;
    if (dropCounter > dropInterval) {
        playerDrop();
    }

    draw();
    requestAnimationFrame(update);
}

// Controles pelo Teclado
document.addEventListener('keydown', event => {
    if (event.keyCode === 37) { // Seta Esquerda
        playerMove(-1);
    } else if (event.keyCode === 39) { // Seta Direita
        playerMove(1);
    } else if (event.keyCode === 40) { // Seta Baixo
        playerDrop();
    } else if (event.keyCode === 81) { // Tecla Q (Girar Esq)
        playerRotate(-1);
    } else if (event.keyCode === 38 || event.keyCode === 87) { // Seta Cima ou W (Girar Dir)
        playerRotate(1);
    }
});

playerReset();
update();