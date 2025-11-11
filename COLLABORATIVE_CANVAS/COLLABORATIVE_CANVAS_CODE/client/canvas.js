/**
 * Canvas Drawing Engine
 * Handles all canvas operations, drawing, and state management
 */

class DrawingCanvas {
    constructor(canvasElement) {
        this.canvas = canvasElement;
        this.ctx = this.canvas.getContext('2d');
        this.isDrawing = false;
        this.currentTool = 'brush';
        this.currentColor = '#000000';
        this.currentStrokeWidth = 3;
        this.lastX = 0;
        this.lastY = 0;

        // Operation history for undo/redo
        this.operationHistory = [];
        this.historyIndex = -1;
        this.maxHistorySize = 100;

        // Drawing state snapshots for efficient redrawing
        this.stateSnapshots = [];

        this.setupCanvas();
        this.setupEventListeners();
    }

    /**
     * Setup canvas size and initial state
     */
    setupCanvas() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    /**
     * Resize canvas to fill container
     */
    resizeCanvas() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.redrawCanvas();
    }

    /**
     * Setup mouse event listeners
     */
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());

        // Touch support for mobile
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.canvas.addEventListener('touchend', () => this.handleMouseUp());
    }

    /**
     * Handle mouse down event
     */
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
        this.isDrawing = true;

        // Save state before drawing
        this.saveState();

        // Emit cursor position
        this.emitCursorPosition(this.lastX, this.lastY);
    }

    /**
     * Handle mouse move event
     */
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Emit cursor position for remote users
        this.emitCursorPosition(x, y);

        if (!this.isDrawing) return;

        // Draw locally
        this.drawLine(this.lastX, this.lastY, x, y);

        // Send drawing event to server
        this.emitDrawingEvent({
            x0: this.lastX,
            y0: this.lastY,
            x1: x,
            y1: y,
            tool: this.currentTool,
            color: this.currentColor,
            strokeWidth: this.currentStrokeWidth
        });

        this.lastX = x;
        this.lastY = y;
    }

    /**
     * Handle mouse up event
     */
    handleMouseUp() {
        if (this.isDrawing) {
            this.isDrawing = false;
            // Add operation to history
            this.addToHistory({
                type: 'draw',
                timestamp: Date.now()
            });
        }
    }

    /**
     * Handle touch start
     */
    handleTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        this.lastX = touch.clientX - rect.left;
        this.lastY = touch.clientY - rect.top;
        this.isDrawing = true;
        this.saveState();
    }

    /**
     * Handle touch move
     */
    handleTouchMove(e) {
        e.preventDefault();
        if (!this.isDrawing) return;

        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;

        this.drawLine(this.lastX, this.lastY, x, y);
        this.emitDrawingEvent({
            x0: this.lastX,
            y0: this.lastY,
            x1: x,
            y1: y,
            tool: this.currentTool,
            color: this.currentColor,
            strokeWidth: this.currentStrokeWidth
        });

        this.lastX = x;
        this.lastY = y;
    }

    /**
     * Draw a line from (x0, y0) to (x1, y1)
     */
    drawLine(x0, y0, x1, y1) {
        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.strokeStyle = this.currentTool === 'eraser' ? '#FFFFFF' : this.currentColor;
        this.ctx.lineWidth = this.currentStrokeWidth;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        if (this.currentTool === 'eraser') {
            this.ctx.globalCompositeOperation = 'destination-out';
            this.ctx.strokeStyle = 'rgba(0,0,0,1)';
        } else {
            this.ctx.globalCompositeOperation = 'source-over';
        }

        this.ctx.stroke();
    }

    /**
     * Draw a remote user's line
     */
    drawRemoteLine(x0, y0, x1, y1, color, strokeWidth, tool) {
        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.strokeStyle = tool === 'eraser' ? '#FFFFFF' : color;
        this.ctx.lineWidth = strokeWidth;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        if (tool === 'eraser') {
            this.ctx.globalCompositeOperation = 'destination-out';
            this.ctx.strokeStyle = 'rgba(0,0,0,1)';
        } else {
            this.ctx.globalCompositeOperation = 'source-over';
        }

        this.ctx.stroke();
    }

    /**
     * Clear the entire canvas
     */
    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.addToHistory({
            type: 'clear',
            timestamp: Date.now()
        });
    }

    /**
     * Save current canvas state
     */
    saveState() {
        this.stateSnapshots.push(this.canvas.toDataURL());
    }

    /**
     * Redraw canvas from history
     */
    redrawCanvas() {
        if (this.stateSnapshots.length > 0) {
            const img = new Image();
            img.src = this.stateSnapshots[this.stateSnapshots.length - 1];
            img.onload = () => {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                this.ctx.drawImage(img, 0, 0);
            };
        }
    }

    /**
     * Add operation to history
     */
    addToHistory(operation) {
        // Remove any redo history if we're adding a new operation
        this.operationHistory = this.operationHistory.slice(0, this.historyIndex + 1);
        this.operationHistory.push(operation);
        this.historyIndex++;

        // Limit history size
        if (this.operationHistory.length > this.maxHistorySize) {
            this.operationHistory.shift();
            this.historyIndex--;
        }
    }

    /**
     * Undo last operation
     */
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.emitUndoEvent();
        }
    }

    /**
     * Redo last undone operation
     */
    redo() {
        if (this.historyIndex < this.operationHistory.length - 1) {
            this.historyIndex++;
            this.emitRedoEvent();
        }
    }

    /**
     * Emit drawing event to server
     */
    emitDrawingEvent(data) {
        wsClient.send('draw', data);
    }

    /**
     * Emit cursor position to server
     */
    emitCursorPosition(x, y) {
        wsClient.send('cursor-move', { x, y });
    }

    /**
     * Emit undo event to server
     */
    emitUndoEvent() {
        wsClient.send('undo', {});
    }

    /**
     * Emit redo event to server
     */
    emitRedoEvent() {
        wsClient.send('redo', {});
    }

    /**
     * Handle remote drawing
     */
    handleRemoteDraw(data) {
        const { x0, y0, x1, y1, color, strokeWidth, tool } = data;
        this.drawRemoteLine(x0, y0, x1, y1, color, strokeWidth, tool);
    }

    /**
     * Handle remote clear
     */
    handleRemoteClear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * Set current tool
     */
    setTool(tool) {
        this.currentTool = tool;
    }

    /**
     * Set current color
     */
    setColor(color) {
        this.currentColor = color;
    }

    /**
     * Set current stroke width
     */
    setStrokeWidth(width) {
        this.currentStrokeWidth = width;
    }

    /**
     * Handle remote undo
     */
    handleRemoteUndo(data) {
        const { operations } = data;
        this.replayOperations(operations);
    }

    /**
     * Handle remote redo
     */
    handleRemoteRedo(data) {
        const { operations } = data;
        this.replayOperations(operations);
    }

    /**
     * Replay operations to reconstruct canvas state
     */
    replayOperations(operations) {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Replay all operations
        operations.forEach(op => {
            if (op.type === 'draw') {
                const { x0, y0, x1, y1, color, strokeWidth, tool } = op.data;
                this.drawRemoteLine(x0, y0, x1, y1, color, strokeWidth, tool);
            } else if (op.type === 'clear') {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            }
        });
    }
}

// Create global canvas instance
const drawingCanvas = new DrawingCanvas(document.getElementById('drawing-canvas'));

