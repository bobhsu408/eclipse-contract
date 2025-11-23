/**
 * Unit.js
 * Base class for all summoned units.
 */
export class Unit {
    constructor(x, y, type) {
        this.x = x;
        this.y = y;
        this.z = 0;
        
        this.width = 30;
        this.height = 30;
        
        this.type = type; // 'GROUND', 'FLYING', 'FIXED'
        
        this.vx = 0;
        this.vy = 0;
        this.vz = 0;
        this.speed = 1;
        
        this.hp = 10;
        this.maxHp = 10;
        this.damage = 1;
        
        this.state = 'IDLE'; // IDLE, MOVE, ATTACK
        this.target = null; // Enemy or Position
        
        this.isGrounded = true;
        this.color = '#fff';
    }

    update(physics, player) {
        // Basic AI: Follow Player (Guard Mode default)
        if (this.type !== 'FIXED') {
            const dx = player.x - this.x;
            const dy = player.y - this.y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            
            if (dist > 100) {
                this.vx = (dx / dist) * this.speed;
                this.vy = (dy / dist) * this.speed;
            } else {
                this.vx = 0;
                this.vy = 0;
            }
        }
        
        if (this.type === 'GROUND') {
            physics.applyGravity(this);
        } else if (this.type === 'FLYING') {
            this.z = 50; // Hover height
        }
    }

    draw(ctx) {
        // Shadow
        ctx.fillStyle = 'rgba(0,0,0,0.3)';
        ctx.beginPath();
        ctx.ellipse(this.x + this.width/2, this.y + this.height - 5, this.width/2, 8, 0, 0, Math.PI*2);
        ctx.fill();
        
        const drawY = this.y - this.z;
        
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, drawY, this.width, this.height);
        
        // Health Bar
        const hpPercent = this.hp / this.maxHp;
        ctx.fillStyle = 'red';
        ctx.fillRect(this.x, drawY - 10, this.width, 4);
        ctx.fillStyle = 'green';
        ctx.fillRect(this.x, drawY - 10, this.width * hpPercent, 4);
    }
}
