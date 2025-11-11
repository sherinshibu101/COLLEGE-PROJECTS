/**
 * WebSocket Server for Real-time Drawing Synchronization
 * Handles client connections, message routing, and state management
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { RoomManager } from './rooms.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Configuration
const PORT = process.env.PORT || 8080;
const CLIENT_DIR = join(__dirname, '../client');

// Room management
const roomManager = new RoomManager();

// Serve static files
app.use(express.static(CLIENT_DIR));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API endpoint to get room info
app.get('/api/rooms', (req, res) => {
    const rooms = roomManager.getRoomsInfo();
    res.json(rooms);
});

/**
 * Handle WebSocket connections
 */
wss.on('connection', (ws) => {
    console.log('New WebSocket connection');
    let clientId = null;
    let roomId = 'default';

    /**
     * Handle incoming messages
     */
    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data);
            const { type, data: messageData } = message;

            switch (type) {
                case 'user-join':
                    handleUserJoin(ws, messageData, roomId);
                    clientId = messageData.userId;
                    break;

                case 'draw':
                    handleDraw(ws, messageData, roomId, clientId);
                    break;

                case 'cursor-move':
                    handleCursorMove(ws, messageData, roomId, clientId);
                    break;

                case 'clear':
                    handleClear(ws, roomId, clientId);
                    break;

                case 'undo':
                    handleUndo(ws, roomId, clientId);
                    break;

                case 'redo':
                    handleRedo(ws, roomId, clientId);
                    break;

                default:
                    console.warn('Unknown message type:', type);
            }
        } catch (error) {
            console.error('Error processing message:', error);
        }
    });

    /**
     * Handle client disconnect
     */
    ws.on('close', () => {
        if (clientId) {
            handleUserLeave(roomId, clientId);
        }
        console.log('Client disconnected');
    });

    /**
     * Handle errors
     */
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

/**
 * Handle user join
 */
function handleUserJoin(ws, data, roomId) {
    const { userId, userName, userColor } = data;
    const room = roomManager.getOrCreateRoom(roomId);
    room.addUser(userId, { ws, userName, userColor });

    // Send current users list to new user
    const usersList = room.getUsersList();
    ws.send(JSON.stringify({
        type: 'users-list',
        data: { users: usersList }
    }));



    // Broadcast user join to all clients in room
    room.broadcast({
        type: 'user-join',
        data: { userId, userName, userColor }
    }, null);

    console.log(`User ${userName} joined room ${roomId}`);
}

/**
 * Handle drawing event
 */
function handleDraw(ws, data, roomId, clientId) {
    const room = roomManager.getRoom(roomId);
    if (room) {
        // Add to drawing state
        room.addDrawOperation(clientId, data);

        // Broadcast to all other clients
        room.broadcast({
            type: 'draw',
            data
        }, ws);
    }
}

/**
 * Handle cursor movement
 */
function handleCursorMove(ws, data, roomId, clientId) {
    const room = roomManager.getRoom(roomId);
    if (room) {
        const user = room.getUser(clientId);
        if (user) {
            room.broadcast({
                type: 'cursor-move',
                data: {
                    userId: clientId,
                    x: data.x,
                    y: data.y,
                    userName: user.userName,
                    userColor: user.userColor
                }
            }, ws);
        }
    }
}

/**
 * Handle clear canvas
 */
function handleClear(ws, roomId, clientId) {
    const room = roomManager.getRoom(roomId);
    if (room) {
        // Add to drawing state
        room.addClearOperation(clientId);

        room.broadcast({
            type: 'remote-clear',
            data: {}
        }, ws);
    }
}

/**
 * Handle undo
 */
function handleUndo(ws, roomId, clientId) {
    const room = roomManager.getRoom(roomId);
    if (room) {
        const result = room.undo();
        if (result.success) {
            // Broadcast undo to all clients with updated operations
            room.broadcast({
                type: 'undo',
                data: {
                    userId: clientId,
                    newIndex: result.newIndex,
                    operations: result.operations
                }
            }, null);
        }
    }
}

/**
 * Handle redo
 */
function handleRedo(ws, roomId, clientId) {
    const room = roomManager.getRoom(roomId);
    if (room) {
        const result = room.redo();
        if (result.success) {
            // Broadcast redo to all clients with updated operations
            room.broadcast({
                type: 'redo',
                data: {
                    userId: clientId,
                    newIndex: result.newIndex,
                    operations: result.operations
                }
            }, null);
        }
    }
}

/**
 * Handle user leave
 */
function handleUserLeave(roomId, clientId) {
    const room = roomManager.getRoom(roomId);
    if (room) {
        room.removeUser(clientId);
        room.broadcast({
            type: 'user-leave',
            data: { userId: clientId }
        }, null);

        // Clean up empty rooms
        if (room.getUserCount() === 0) {
            roomManager.deleteRoom(roomId);
        }
    }
}

/**
 * Start server
 */
server.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`WebSocket server ready on ws://localhost:${PORT}`);
});

/**
 * Graceful shutdown
 */
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

