/**
 * Room Management System
 * Handles multiple isolated drawing rooms/canvases
 */

import { RoomDrawingState } from './drawing-state.js';

export class Room {
    constructor(roomId) {
        this.roomId = roomId;
        this.users = new Map();
        this.drawingState = new RoomDrawingState(roomId);
        this.createdAt = new Date();
    }

    /**
     * Add a user to the room
     */
    addUser(userId, userData) {
        this.users.set(userId, userData);
    }

    /**
     * Remove a user from the room
     */
    removeUser(userId) {
        this.users.delete(userId);
    }

    /**
     * Get a user by ID
     */
    getUser(userId) {
        return this.users.get(userId);
    }

    /**
     * Get all users in the room
     */
    getUsers() {
        return Array.from(this.users.values());
    }

    /**
     * Get users list for broadcasting
     */
    getUsersList() {
        return Array.from(this.users.entries()).map(([userId, user]) => ({
            userId,
            userName: user.userName,
            userColor: user.userColor
        }));
    }

    /**
     * Get number of users in room
     */
    getUserCount() {
        return this.users.size;
    }

    /**
     * Broadcast message to all users in room
     */
    broadcast(message, excludeWs = null) {
        const messageStr = JSON.stringify(message);
        this.users.forEach((user) => {
            if (excludeWs === null || user.ws !== excludeWs) {
                if (user.ws.readyState === 1) { // WebSocket.OPEN
                    user.ws.send(messageStr);
                }
            }
        });
    }

    /**
     * Get room info
     */
    getInfo() {
        return {
            roomId: this.roomId,
            userCount: this.getUserCount(),
            createdAt: this.createdAt,
            users: this.getUsersList()
        };
    }

    /**
     * Add a drawing operation to state
     */
    addDrawOperation(userId, drawData) {
        return this.drawingState.addDrawOperation(userId, drawData);
    }

    /**
     * Add a clear operation to state
     */
    addClearOperation(userId) {
        return this.drawingState.addClearOperation(userId);
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
     * Get all active operations
     */
    getActiveOperations() {
        return this.drawingState.getActiveOperations();
    }

    /**
     * Get drawing state info
     */
    getDrawingStateInfo() {
        return this.drawingState.getStateInfo();
    }
}

export class RoomManager {
    constructor() {
        this.rooms = new Map();
    }

    /**
     * Get or create a room
     */
    getOrCreateRoom(roomId) {
        if (!this.rooms.has(roomId)) {
            this.rooms.set(roomId, new Room(roomId));
        }
        return this.rooms.get(roomId);
    }

    /**
     * Get a room
     */
    getRoom(roomId) {
        return this.rooms.get(roomId);
    }

    /**
     * Delete a room
     */
    deleteRoom(roomId) {
        this.rooms.delete(roomId);
    }

    /**
     * Get all rooms info
     */
    getRoomsInfo() {
        return Array.from(this.rooms.values()).map(room => room.getInfo());
    }

    /**
     * Get number of active rooms
     */
    getRoomCount() {
        return this.rooms.size;
    }

    /**
     * Get total number of connected users
     */
    getTotalUserCount() {
        let total = 0;
        this.rooms.forEach(room => {
            total += room.getUserCount();
        });
        return total;
    }
}

