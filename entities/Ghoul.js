/**
 * Ghoul.js
 * Basic Ground Unit (Fodder)
 */
import { Unit } from './Unit.js';

export class Ghoul extends Unit {
    constructor(x, y) {
        super(x, y, 'GROUND');
        this.width = 25;
        this.height = 25;
        
        this.speed = 2; // Fast
        this.hp = 15;
        this.maxHp = 15;
        this.cost = 10; // Soul Cost
        
        this.color = '#556b2f'; // Dark Olive Green
    }

    draw(ctx) {
        super.draw(ctx);
        
        // Eyes
        ctx.fillStyle = '#ff0000';
        ctx.fillRect(this.x + 15, this.y + 5, 5, 5);
    }
}
