/**
 * WebSocket Test Script
 * Tests the collaborative drawing canvas functionality
 */

import { WebSocket } from 'ws';

const SERVER_URL = 'ws://localhost:8080';

class TestClient {
    constructor(name) {
        this.name = name;
        this.ws = null;
        this.userId = `test-user-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
        this.messages = [];
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(SERVER_URL);

                this.ws.onopen = () => {
                    console.log(`[${this.name}] Connected`);
                    this.send('user-join', {
                        userId: this.userId,
                        userName: this.name,
                        userColor: '#' + Math.floor(Math.random()*16777215).toString(16)
                    });
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.messages.push(message);
                    console.log(`[${this.name}] Received:`, message.type);
                };

                this.ws.onerror = (error) => {
                    console.error(`[${this.name}] Error:`, error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log(`[${this.name}] Disconnected`);
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    send(type, data) {
        if (this.ws && this.ws.readyState === 1) {
            this.ws.send(JSON.stringify({ type, data }));
            console.log(`[${this.name}] Sent:`, type);
        }
    }

    draw(x0, y0, x1, y1) {
        this.send('draw', {
            x0, y0, x1, y1,
            tool: 'brush',
            color: '#000000',
            strokeWidth: 3
        });
    }

    moveCursor(x, y) {
        this.send('cursor-move', { x, y });
    }

    clear() {
        this.send('clear', {});
    }

    undo() {
        this.send('undo', {});
    }

    redo() {
        this.send('redo', {});
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }

    getMessagesByType(type) {
        return this.messages.filter(m => m.type === type);
    }
}

async function runTests() {
    console.log('=== Collaborative Drawing Canvas Tests ===\n');

    try {
        // Test 1: Single user connection
        console.log('Test 1: Single user connection');
        const client1 = new TestClient('User1');
        await client1.connect();
        await new Promise(r => setTimeout(r, 500));

        const usersList = client1.getMessagesByType('users-list');
        console.log(`✓ User list received: ${usersList.length > 0 ? 'PASS' : 'FAIL'}\n`);

        // Test 2: Two users connection
        console.log('Test 2: Two users connection');
        const client2 = new TestClient('User2');
        await client2.connect();
        await new Promise(r => setTimeout(r, 500));

        const userJoin = client1.getMessagesByType('user-join');
        console.log(`✓ User join event received: ${userJoin.length > 0 ? 'PASS' : 'FAIL'}\n`);

        // Test 3: Drawing synchronization
        console.log('Test 3: Drawing synchronization');
        client1.draw(10, 10, 20, 20);
        await new Promise(r => setTimeout(r, 200));

        const drawMessages = client2.getMessagesByType('draw');
        console.log(`✓ Draw event received by other user: ${drawMessages.length > 0 ? 'PASS' : 'FAIL'}\n`);

        // Test 4: Cursor tracking
        console.log('Test 4: Cursor tracking');
        client1.moveCursor(50, 50);
        await new Promise(r => setTimeout(r, 200));

        const cursorMessages = client2.getMessagesByType('cursor-move');
        console.log(`✓ Cursor move event received: ${cursorMessages.length > 0 ? 'PASS' : 'FAIL'}\n`);

        // Test 5: Clear canvas
        console.log('Test 5: Clear canvas');
        client1.clear();
        await new Promise(r => setTimeout(r, 200));

        const clearMessages = client2.getMessagesByType('remote-clear');
        console.log(`✓ Clear event received: ${clearMessages.length > 0 ? 'PASS' : 'FAIL'}\n`);

        // Test 6: Undo/Redo
        console.log('Test 6: Undo/Redo');
        client1.draw(30, 30, 40, 40);
        await new Promise(r => setTimeout(r, 200));
        client1.undo();
        await new Promise(r => setTimeout(r, 200));

        const undoMessages = client2.getMessagesByType('undo');
        console.log(`✓ Undo event received: ${undoMessages.length > 0 ? 'PASS' : 'FAIL'}\n`);

        // Test 7: Disconnect
        console.log('Test 7: User disconnect');
        client1.close();
        await new Promise(r => setTimeout(r, 500));

        const userLeave = client2.getMessagesByType('user-leave');
        console.log(`✓ User leave event received: ${userLeave.length > 0 ? 'PASS' : 'FAIL'}\n`);

        client2.close();

        console.log('=== All tests completed ===');
    } catch (error) {
        console.error('Test error:', error);
    }
}

runTests();

