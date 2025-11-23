/**
 * InputHandler.js
 * Manages keyboard and mouse input.
 */
export class InputHandler {
    constructor() {
        this.keys = {};
        this.keysPrev = {}; // For "just pressed" detection
        
        this.mouse = {
            x: 0,
            y: 0,
            isDown: false,
            isDownPrev: false
        };

        window.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });
        
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
        
        window.addEventListener('mousedown', () => {
            this.mouse.isDown = true;
        });
        
        window.addEventListener('mouseup', () => {
            this.mouse.isDown = false;
        });
    }

    update() {
        // Copy current state to prev state at the end of frame
        // But here we need to call this manually or have a way to reset "just pressed"
        // A better way for "just pressed" is to check (current && !prev)
    }
    
    postUpdate() {
        this.keysPrev = { ...this.keys };
        this.mouse.isDownPrev = this.mouse.isDown;
    }

    isKeyDown(code) {
        return !!this.keys[code];
    }

    isKeyPressed(code) {
        return !!this.keys[code] && !this.keysPrev[code];
    }
    
    isMouseDown() {
        return this.mouse.isDown;
    }
    
    isMouseClicked() {
        return this.mouse.isDown && !this.mouse.isDownPrev;
    }
}
