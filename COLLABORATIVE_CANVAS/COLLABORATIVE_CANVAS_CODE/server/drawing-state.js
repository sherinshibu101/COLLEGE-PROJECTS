/**
 * Drawing State Management
 * Manages canvas state, operation history, and undo/redo for a room
 */

export class DrawingState {
    constructor() {
        this.operations = [];
        this.operationIndex = -1;
        this.maxHistorySize = 200;
    }

    /**
     * Add a drawing operation to history
     */
    addOperation(operation) {
        // Remove any redo history if we're adding a new operation
        this.operations = this.operations.slice(0, this.operationIndex + 1);

        // Add the new operation
        this.operations.push({
            ...operation,
            timestamp: Date.now(),
            id: this.generateOperationId()
        });

        this.operationIndex++;

        // Limit history size
        if (this.operations.length > this.maxHistorySize) {
            this.operations.shift();
            this.operationIndex--;
        }

        return this.operations[this.operationIndex];
    }

    /**
     * Get the current operation index
     */
    getCurrentIndex() {
        return this.operationIndex;
    }

    /**
     * Get all operations
     */
    getOperations() {
        return this.operations;
    }

    /**
     * Get operations up to current index (for replay)
     */
    getActiveOperations() {
        return this.operations.slice(0, this.operationIndex + 1);
    }

    /**
     * Undo last operation
     */
    undo() {
        if (this.operationIndex > -1) {
            this.operationIndex--;
            return {
                success: true,
                newIndex: this.operationIndex,
                operations: this.getActiveOperations()
            };
        }
        return { success: false };
    }

    /**
     * Redo last undone operation
     */
    redo() {
        if (this.operationIndex < this.operations.length - 1) {
            this.operationIndex++;
            return {
                success: true,
                newIndex: this.operationIndex,
                operations: this.getActiveOperations()
            };
        }
        return { success: false };
    }

    /**
     * Clear all operations
     */
    clear() {
        this.operations = [];
        this.operationIndex = -1;
    }

    /**
     * Generate unique operation ID
     */
    generateOperationId() {
        return `op-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get operation by ID
     */
    getOperationById(id) {
        return this.operations.find(op => op.id === id);
    }

    /**
     * Get state info for debugging
     */
    getStateInfo() {
        return {
            totalOperations: this.operations.length,
            currentIndex: this.operationIndex,
            canUndo: this.operationIndex > -1,
            canRedo: this.operationIndex < this.operations.length - 1
        };
    }
}

/**
 * Room Drawing State Manager
 * Manages drawing state for a specific room
 */
export class RoomDrawingState {
    constructor(roomId) {
        this.roomId = roomId;
        this.drawingState = new DrawingState();
        this.userOperations = new Map(); // Track which user performed which operation
    }

    /**
     * Add a drawing operation
     */
    addDrawOperation(userId, drawData) {
        const operation = this.drawingState.addOperation({
            type: 'draw',
            userId,
            data: drawData
        });

        // Track user operation
        if (!this.userOperations.has(userId)) {
            this.userOperations.set(userId, []);
        }
        this.userOperations.get(userId).push(operation.id);

        return operation;
    }

    /**
     * Add a clear operation
     */
    addClearOperation(userId) {
        const operation = this.drawingState.addOperation({
            type: 'clear',
            userId,
            data: {}
        });

        if (!this.userOperations.has(userId)) {
            this.userOperations.set(userId, []);
        }
        this.userOperations.get(userId).push(operation.id);

        return operation;
    }

    /**
     * Undo last operation
     */
    undo() {
        return this.drawingState.undo();
    }

    /**
     * Redo last undone operation
     */
    redo() {
        return this.drawingState.redo();
    }

    /**
     * Get all active operations for replay
     */
    getActiveOperations() {
        return this.drawingState.getActiveOperations();
    }

    /**
     * Get operations by user
     */
    getUserOperations(userId) {
        const userOpIds = this.userOperations.get(userId) || [];
        return userOpIds
            .map(id => this.drawingState.getOperationById(id))
            .filter(op => op !== undefined);
    }

    /**
     * Get state info
     */
    getStateInfo() {
        return {
            roomId: this.roomId,
            ...this.drawingState.getStateInfo(),
            userCount: this.userOperations.size
        };
    }
}

