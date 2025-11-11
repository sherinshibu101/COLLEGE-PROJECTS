/**
 * Main Application Controller
 * Coordinates between UI, Canvas, and WebSocket
 */

class DrawingApp {
    constructor() {
        this.remoteUsers = new Map();
        this.remoteCursors = new Map();
        this.initializeUI();
        this.setupWebSocketHandlers();
        this.setupKeyboardShortcuts();
    }

    /**
     * Initialize UI elements and event listeners
     */
    initializeUI() {
        // Tool buttons
        document.getElementById('tool-brush').addEventListener('click', () => this.selectTool('brush'));
        document.getElementById('tool-eraser').addEventListener('click', () => this.selectTool('eraser'));
        document.getElementById('tool-clear').addEventListener('click', () => this.clearCanvas());

        // Color picker
        const colorPicker = document.getElementById('color-picker');
        colorPicker.addEventListener('change', (e) => this.setColor(e.target.value));
        colorPicker.addEventListener('input', (e) => this.setColor(e.target.value));

        // Stroke width
        const strokeWidth = document.getElementById('stroke-width');
        strokeWidth.addEventListener('input', (e) => this.setStrokeWidth(e.target.value));

        // History buttons
        document.getElementById('btn-undo').addEventListener('click', () => this.undo());
        document.getElementById('btn-redo').addEventListener('click', () => this.redo());

        // Set initial color preview
        this.updateColorPreview(colorPicker.value);
    }

    /**
     * Setup WebSocket event handlers
     */
    setupWebSocketHandlers() {
        // Connection events
        window.addEventListener('connected', () => this.handleConnected());
        window.addEventListener('disconnected', () => this.handleDisconnected());
        window.addEventListener('error', (e) => this.handleError(e.detail));

        // Drawing events
        window.addEventListener('draw', (e) => this.handleRemoteDraw(e.detail));
        window.addEventListener('remote-clear', (e) => this.handleRemoteClear());

        // User events
        window.addEventListener('user-join', (e) => this.handleUserJoin(e.detail));
        window.addEventListener('user-leave', (e) => this.handleUserLeave(e.detail));
        window.addEventListener('users-list', (e) => this.handleUsersList(e.detail));



        // Cursor events
        window.addEventListener('cursor-move', (e) => this.handleRemoteCursor(e.detail));

        // History events
        window.addEventListener('undo', (e) => this.handleRemoteUndo(e.detail));
        window.addEventListener('redo', (e) => this.handleRemoteRedo(e.detail));

        // Connect to server
        wsClient.connect();
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'z') {
                    e.preventDefault();
                    this.undo();
                } else if (e.key === 'y') {
                    e.preventDefault();
                    this.redo();
                }
            }

            // Tool shortcuts
            if (e.key === 'b' || e.key === 'B') {
                this.selectTool('brush');
            } else if (e.key === 'e' || e.key === 'E') {
                this.selectTool('eraser');
            }
        });
    }

    /**
     * Handle connection established
     */
    handleConnected() {
        console.log('Connected to server');
        this.updateConnectionStatus(true);
    }

    /**
     * Handle disconnection
     */
    handleDisconnected() {
        console.log('Disconnected from server');
        this.updateConnectionStatus(false);
    }

    /**
     * Handle connection error
     */
    handleError(error) {
        console.error('Connection error:', error);
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('status');
        const statusText = document.getElementById('status-text');

        if (connected) {
            statusIndicator.classList.remove('disconnected');
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.classList.remove('connected');
            statusIndicator.classList.add('disconnected');
            statusText.textContent = 'Disconnected';
        }
    }

    /**
     * Select a drawing tool
     */
    selectTool(tool) {
        // Update UI
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        if (tool === 'brush') {
            document.getElementById('tool-brush').classList.add('active');
        } else if (tool === 'eraser') {
            document.getElementById('tool-eraser').classList.add('active');
        }

        // Update canvas
        drawingCanvas.setTool(tool);
    }

    /**
     * Set drawing color
     */
    setColor(color) {
        drawingCanvas.setColor(color);
        this.updateColorPreview(color);
    }

    /**
     * Update color preview
     */
    updateColorPreview(color) {
        document.getElementById('color-preview').style.backgroundColor = color;
    }

    /**
     * Set stroke width
     */
    setStrokeWidth(width) {
        drawingCanvas.setStrokeWidth(parseInt(width));
        document.getElementById('stroke-width-value').textContent = width;
    }

    /**
     * Clear canvas
     */
    clearCanvas() {
        if (confirm('Are you sure you want to clear the canvas?')) {
            drawingCanvas.clearCanvas();
            wsClient.send('clear', {});
        }
    }

    /**
     * Undo operation
     */
    undo() {
        drawingCanvas.undo();
    }

    /**
     * Redo operation
     */
    redo() {
        drawingCanvas.redo();
    }

    /**
     * Handle remote drawing
     */
    handleRemoteDraw(data) {
        drawingCanvas.handleRemoteDraw(data);
    }

    /**
     * Handle remote clear
     */
    handleRemoteClear() {
        drawingCanvas.handleRemoteClear();
    }

    /**
     * Handle user join
     */
    handleUserJoin(data) {
        const { userId, userName, userColor } = data;
        this.remoteUsers.set(userId, { userName, userColor });
        this.updateUsersList();
        console.log(`${userName} joined`);
    }

    /**
     * Handle user leave
     */
    handleUserLeave(data) {
        const { userId } = data;
        this.remoteUsers.delete(userId);
        this.remoteCursors.delete(userId);
        this.removeRemoteCursor(userId);
        this.updateUsersList();
    }

    /**
     * Handle users list update
     */
    handleUsersList(data) {
        const { users } = data;
        this.remoteUsers.clear();
        users.forEach(user => {
            if (user.userId !== wsClient.userId) {
                this.remoteUsers.set(user.userId, {
                    userName: user.userName,
                    userColor: user.userColor
                });
            }
        });
        this.updateUsersList();
    }



    /**
     * Update users list display
     */
    updateUsersList() {
        const usersList = document.getElementById('users-list');
        usersList.innerHTML = '';

        // Add current user
        const currentUserItem = document.createElement('div');
        currentUserItem.className = 'user-item';
        currentUserItem.innerHTML = `
            <div class="user-color" style="background: ${wsClient.userColor}"></div>
            <span>${wsClient.userName} (You)</span>
        `;
        usersList.appendChild(currentUserItem);

        // Add remote users
        this.remoteUsers.forEach((user, userId) => {
            const userItem = document.createElement('div');
            userItem.className = 'user-item';
            userItem.innerHTML = `
                <div class="user-color" style="background: ${user.userColor}"></div>
                <span>${user.userName}</span>
            `;
            usersList.appendChild(userItem);
        });
    }

    /**
     * Handle remote cursor movement
     */
    handleRemoteCursor(data) {
        const { userId, x, y, userName, userColor } = data;
        this.remoteCursors.set(userId, { x, y, userName, userColor });
        this.updateRemoteCursor(userId, x, y, userName, userColor);
    }

    /**
     * Update remote cursor display
     */
    updateRemoteCursor(userId, x, y, userName, userColor) {
        let cursor = document.getElementById(`cursor-${userId}`);

        if (!cursor) {
            cursor = document.createElement('div');
            cursor.id = `cursor-${userId}`;
            cursor.className = 'remote-cursor';
            cursor.style.borderColor = userColor;
            cursor.style.color = userColor;
            document.getElementById('cursor-layer').appendChild(cursor);
        }

        cursor.style.left = x + 'px';
        cursor.style.top = y + 'px';

        // Update label
        let label = cursor.querySelector('.remote-cursor-label');
        if (!label) {
            label = document.createElement('div');
            label.className = 'remote-cursor-label';
            cursor.appendChild(label);
        }
        label.textContent = userName;
    }

    /**
     * Remove remote cursor
     */
    removeRemoteCursor(userId) {
        const cursor = document.getElementById(`cursor-${userId}`);
        if (cursor) {
            cursor.remove();
        }
    }

    /**
     * Handle remote undo
     */
    handleRemoteUndo(data) {
        drawingCanvas.handleRemoteUndo(data);
    }

    /**
     * Handle remote redo
     */
    handleRemoteRedo(data) {
        drawingCanvas.handleRemoteRedo(data);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DrawingApp();
});

