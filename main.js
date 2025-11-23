/**
 * Eclipse Contract - Main Entry Point
 */

import { InputHandler } from './engine/InputHandler.js';
import { Physics } from './engine/Physics.js';
import { Player } from './entities/Player.js';
import { Ghoul } from './entities/Ghoul.js';

class Game {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        
        // Systems
        this.input = new InputHandler();
        this.physics = new Physics();
        
        // Entities
        this.player = new Player(100, 300);
        this.units = []; // Array to hold all friendly units
        
        this.isRunning = false;
        this.lastTime = 0;
        
        // Resize handling
        window.addEventListener('resize', () => this.resize());
        this.resize();
        
        // UI Elements
        this.startBtn = document.getElementById('start-btn');
        this.mainMenu = document.getElementById('main-menu');
        this.gameHud = document.getElementById('game-hud');
        this.soulDisplay = document.getElementById('soul-count');
        
        this.initListeners();
        
        // Start the render loop
        this.loop(0);
    }
    
    initListeners() {
        this.startBtn.addEventListener('click', () => {
            this.startGame();
        });
    }
    
    resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        
        if (this.physics) {
            this.physics.maxY = this.height - 50;
        }
    }
    
    startGame() {
        console.log("Contract Signed. Game Starting...");
        this.mainMenu.classList.add('hidden');
        this.gameHud.classList.remove('hidden');
        this.isRunning = true;
        
        this.player.y = 300;
        this.player.vx = 0;
        this.player.vy = 0;
        this.units = []; // Clear units
    }
    
    update(deltaTime) {
        if (!this.isRunning) return;
        
        this.input.update();
        
        // Summoning Test (Press 1)
        if (this.input.isKeyPressed('Digit1')) {
            if (this.player.soul >= 10) {
                this.player.soul -= 10;
                // Spawn Ghoul at Player position
                const ghoul = new Ghoul(this.player.x + 50, this.player.y);
                this.units.push(ghoul);
                console.log("Summoned Ghoul!");
            } else {
                console.log("Not enough Soul!");
            }
        }
        
        // Player Logic
        this.player.update(this.input);
        this.physics.applyGravity(this.player);
        this.physics.applyPhysics(this.player);
        
        // Unit Logic
        this.units.forEach(unit => {
            unit.update(this.physics, this.player);
            this.physics.applyPhysics(unit);
        });
        
        // Update UI
        if (this.soulDisplay) {
            this.soulDisplay.textContent = Math.floor(this.player.soul);
        }
        
        this.input.postUpdate();
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        if (!this.isRunning) {
            this.drawMenuBackground();
        } else {
            this.drawGameWorld();
        }
    }
    
    drawMenuBackground() {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.02)';
        for(let i=0; i<50; i++) {
            const x = Math.random() * this.width;
            const y = Math.random() * this.height;
            const size = Math.random() * 2;
            this.ctx.fillRect(x, y, size, size);
        }
    }
    
    drawGameWorld() {
        // Draw Floor (Grid)
        this.ctx.fillStyle = '#1a1a1a';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Grid Lines
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        this.ctx.lineWidth = 1;
        const gridSize = 50;
        
        // Vertical
        for(let x=0; x<this.width; x+=gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
            this.ctx.stroke();
        }
        // Horizontal
        for(let y=0; y<this.height; y+=gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.width, y);
            this.ctx.stroke();
        }
        
        // Horizon Line (Limit of movement)
        this.ctx.strokeStyle = '#7b2cbf';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.physics.minY);
        this.ctx.lineTo(this.width, this.physics.minY);
        this.ctx.stroke();
        
        // Collect all entities for sorting
        const renderList = [this.player, ...this.units];
        
        // Sort by Y (Depth)
        renderList.sort((a, b) => a.y - b.y);
        
        // Draw Sorted Entities
        renderList.forEach(entity => {
            entity.draw(this.ctx);
            
            // Draw Connection Line if it's a unit
            if (entity !== this.player) {
                this.ctx.strokeStyle = 'rgba(212, 175, 55, 0.2)';
                this.ctx.lineWidth = 1;
                this.ctx.beginPath();
                // Connect bases (feet)
                this.ctx.moveTo(this.player.x + this.player.width/2, this.player.y + this.player.height);
                this.ctx.lineTo(entity.x + entity.width/2, entity.y + entity.height);
                this.ctx.stroke();
            }
        });
        
        // Draw Instructions
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '14px Inter';
        this.ctx.fillText('WASD to Move (2.5D) | Space to Jump | Press 1 to Summon Ghoul', 20, 80);
    }
    
    loop(timestamp) {
        const deltaTime = timestamp - this.lastTime;
        this.lastTime = timestamp;
        
        this.update(deltaTime);
        this.draw();
        
        requestAnimationFrame((t) => this.loop(t));
    }
}
