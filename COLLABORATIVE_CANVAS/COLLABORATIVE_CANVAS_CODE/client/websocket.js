/**
 * WebSocket Client for Real-time Drawing Synchronization
 * Handles connection, message sending/receiving, and event delegation
 */

class DrawingWebSocketClient {
    constructor() {
        this.ws = null;
        this.userId = this.generateUserId();
        this.userNumber = Math.floor(Math.random() * 10000);
        this.userName = `User-${this.userNumber}`;
        this.userColor = this.generateColor();
        this.isConnected = false;
        this.messageHandlers = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
    }

    /**
     * Generate a unique user ID
     */
    generateUserId() {
        return `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Generate a random color for the user
     */
    generateColor() {
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#52C9A8'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    /**
     * Connect to the WebSocket server
     */
    connect(url = 'ws://localhost:8080') {
        try {
            this.ws = new WebSocket(url);

            this.ws.onopen = () => this.handleOpen();
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onerror = (error) => this.handleError(error);
            this.ws.onclose = () => this.handleClose();
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket open event
     */
    handleOpen() {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;

        // Send initial handshake
        this.send('user-join', {
            userId: this.userId,
            userName: this.userName,
            userColor: this.userColor
        });

        this.emit('connected');
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            const { type, data } = message;

            if (this.messageHandlers[type]) {
                this.messageHandlers[type].forEach(handler => handler(data));
            }

            this.emit(type, data);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket error
     */
    handleError(error) {
        console.error('WebSocket error:', error);
        this.emit('error', error);
    }

    /**
     * Handle WebSocket close
     */
    handleClose() {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.emit('disconnected');
        this.scheduleReconnect();
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`);
            setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.emit('reconnect-failed');
        }
    }

    /**
     * Send a message to the server
     */
    send(type, data = {}) {
        if (!this.isConnected) {
            console.warn('WebSocket not connected, message queued:', type);
            return false;
        }

        try {
            const message = JSON.stringify({ type, data });
            this.ws.send(message);
            return true;
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            return false;
        }
    }

    /**
     * Register a handler for a specific message type
     */
    on(type, handler) {
        if (!this.messageHandlers[type]) {
            this.messageHandlers[type] = [];
        }
        this.messageHandlers[type].push(handler);
    }

    /**
     * Unregister a handler for a specific message type
     */
    off(type, handler) {
        if (this.messageHandlers[type]) {
            this.messageHandlers[type] = this.messageHandlers[type].filter(h => h !== handler);
        }
    }

    /**
     * Emit an event (for internal use)
     */
    emit(type, data) {
        const event = new CustomEvent(type, { detail: data });
        window.dispatchEvent(event);
    }

    /**
     * Close the WebSocket connection
     */
    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Create global WebSocket client instance
const wsClient = new DrawingWebSocketClient();

