/**
 * Physics.js
 * Top-Down 2.5D Physics
 * X, Y: Ground Plane
 * Z: Height (Jumping)
 */
export class Physics {
    constructor() {
        this.gravity = 0.9; // Higher gravity for snappy hops
        this.friction = 0.85;
        // Boundaries
        this.minY = 200; // Horizon line
        this.maxY = window.innerHeight - 50;
    }

    applyGravity(entity) {
        // Gravity affects Z axis now
        if (entity.z > 0 || entity.vz > 0) {
            entity.vz -= this.gravity;
            entity.isGrounded = false;
        }
    }

    applyPhysics(entity) {
        // Ground Movement (X/Y)
        entity.x += entity.vx;
        entity.y += entity.vy;
        
        // Height Movement (Z)
        entity.z += entity.vz;

        // Friction
        entity.vx *= this.friction;
        entity.vy *= this.friction;
        
        // Floor Collision (Z-axis)
        if (entity.z < 0) {
            entity.z = 0;
            entity.vz = 0;
            entity.isGrounded = true;
        }
        
        // Screen Boundaries (X/Y)
        if (entity.x < 0) entity.x = 0;
        if (entity.y < this.minY) entity.y = this.minY;
        if (entity.y > this.maxY) entity.y = this.maxY;
    }
    
    checkCollision(rect1, rect2) {
        // 2.5D Collision: Check Footprint (X/Y) AND Height (Z) overlap?
        // For now, we mainly care about ground footprint overlap
        return (
            rect1.x < rect2.x + rect2.width &&
            rect1.x + rect1.width > rect2.x &&
            rect1.y < rect2.y + rect2.height &&
            rect1.y + rect1.height > rect2.y
        );
    }
}
