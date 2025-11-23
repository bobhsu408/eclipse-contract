/**
 * Player.js
 * The Summoner Character (2.5D)
 */
export class Player {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.z = 0; // Height
        
        this.width = 40;
        this.height = 60;
        
        this.vx = 0;
        this.vy = 0;
        this.vz = 0;
        
        this.speed = 1.5;
        this.maxSpeed = 5;
        this.jumpForce = 7; // Reduced for short hop
        
        this.isGrounded = true;
        
        // Stats
        this.hp = 100;
        this.maxHp = 100;
        this.soul = 50;
        this.maxSoul = 100;
        
        this.color = '#7b2cbf';
    }

    update(input) {
        // Movement (X/Y Plane)
        if (input.isKeyDown('KeyA') || input.isKeyDown('ArrowLeft')) {
            this.vx -= this.speed;
        }
        if (input.isKeyDown('KeyD') || input.isKeyDown('ArrowRight')) {
            this.vx += this.speed;
        }
        if (input.isKeyDown('KeyW') || input.isKeyDown('ArrowUp')) {
            this.vy -= this.speed;
        }
        if (input.isKeyDown('KeyS') || input.isKeyDown('ArrowDown')) {
            this.vy += this.speed;
        }
        
        // Jump (Z Axis)
        if (input.isKeyPressed('Space') && this.isGrounded) {
            this.vz = this.jumpForce;
            this.isGrounded = false;
        }
        
        // Fixed Short Jump (No variable height)
        
        // Clamp Speed
        if (this.vx > this.maxSpeed) this.vx = this.maxSpeed;
        if (this.vx < -this.maxSpeed) this.vx = -this.maxSpeed;
        if (this.vy > this.maxSpeed) this.vy = this.maxSpeed;
        if (this.vy < -this.maxSpeed) this.vy = -this.maxSpeed;
    }

    draw(ctx) {
        ctx.save();
        
        // Draw Shadow (at Ground Level Y)
        ctx.fillStyle = 'rgba(0,0,0,0.4)';
        ctx.beginPath();
        ctx.ellipse(this.x + this.width/2, this.y + this.height - 5, this.width/2, 10, 0, 0, Math.PI*2);
        ctx.fill();
        
        // Draw Character (Offset by Z)
        const drawY = this.y - this.z;
        
        // Glow effect
        ctx.shadowBlur = 20;
        ctx.shadowColor = this.color;
        
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, drawY, this.width, this.height);
        
        // Hood
        ctx.fillStyle = '#000';
        ctx.fillRect(this.x + 10, drawY + 5, 20, 20);
        
        // Eyes
        ctx.fillStyle = '#d4af37';
        ctx.shadowBlur = 5;
        ctx.shadowColor = '#d4af37';
        
        const eyeOffset = this.vx >= 0 ? 4 : -4;
        ctx.fillRect(this.x + 12 + eyeOffset, drawY + 12, 6, 4);
        ctx.fillRect(this.x + 22 + eyeOffset, drawY + 12, 6, 4);
        
        ctx.restore();
    }
}
