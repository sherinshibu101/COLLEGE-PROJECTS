# Collaborative Drawing Canvas - Architecture

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Clients                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Client 1   │  │   Client 2   │  │   Client N   │      │
│  │  (Canvas UI) │  │  (Canvas UI) │  │  (Canvas UI) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                    WebSocket Connection                     │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Node.js Server│
                    │  (Express + WS)│
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐      ┌──────▼──────┐      ┌────▼────┐
    │ Room 1  │      │  Room 2     │      │ Room N  │
    │ (State) │      │  (State)    │      │ (State) │
    └─────────┘      └─────────────┘      └─────────┘
```

## 📊 Data Flow Diagram

### Drawing Event Flow

```
User draws on canvas
        │
        ▼
┌──────────────────────────────────────┐
│ Canvas.handleMouseMove()             │
│ - Detect drawing action              │
│ - Draw locally on canvas             │
│ - Emit drawing event                 │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ WebSocket.send('draw', data)         │
│ - Serialize drawing data             │
│ - Send to server                     │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ Server: handleDraw()                 │
│ - Receive drawing event              │
│ - Add to room drawing state          │
│ - Broadcast to other clients         │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ Other Clients: handleRemoteDraw()    │
│ - Receive drawing event              │
│ - Draw on canvas                     │
│ - Update display                     │
└──────────────────────────────────────┘
```

## 🔄 WebSocket Protocol

### Message Format

All WebSocket messages follow this JSON structure:

```json
{
  "type": "message_type",
  "data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

### Message Types

#### 1. User Management

**user-join** (Client → Server)
```json
{
  "type": "user-join",
  "data": {
    "userId": "user-123456-abc",
    "userName": "User-123456",
    "userColor": "#FF6B6B"
  }
}
```

**user-join** (Server → All Clients)
```json
{
  "type": "user-join",
  "data": {
    "userId": "user-123456-abc",
    "userName": "User-123456",
    "userColor": "#FF6B6B"
  }
}
```

**users-list** (Server → New Client)
```json
{
  "type": "users-list",
  "data": {
    "users": [
      {"userId": "user-1", "userName": "User1", "userColor": "#FF6B6B"},
      {"userId": "user-2", "userName": "User2", "userColor": "#4ECDC4"}
    ]
  }
}
```

#### 2. Drawing Operations

**draw** (Client → Server)
```json
{
  "type": "draw",
  "data": {
    "x0": 100,
    "y0": 100,
    "x1": 110,
    "y1": 110,
    "tool": "brush",
    "color": "#000000",
    "strokeWidth": 3
  }
}
```

**draw** (Server → Other Clients)
```json
{
  "type": "draw",
  "data": {
    "x0": 100,
    "y0": 100,
    "x1": 110,
    "y1": 110,
    "tool": "brush",
    "color": "#000000",
    "strokeWidth": 3
  }
}
```

#### 3. Cursor Tracking

**cursor-move** (Client → Server)
```json
{
  "type": "cursor-move",
  "data": {
    "x": 250,
    "y": 150
  }
}
```

**cursor-move** (Server → Other Clients)
```json
{
  "type": "cursor-move",
  "data": {
    "userId": "user-123456-abc",
    "x": 250,
    "y": 150,
    "userName": "User-123456",
    "userColor": "#FF6B6B"
  }
}
```

#### 4. Canvas Operations

**clear** (Client → Server)
```json
{
  "type": "clear",
  "data": {}
}
```

**remote-clear** (Server → All Clients)
```json
{
  "type": "remote-clear",
  "data": {}
}
```

#### 5. History Operations

**undo** (Client → Server)
```json
{
  "type": "undo",
  "data": {}
}
```

**undo** (Server → All Clients)
```json
{
  "type": "undo",
  "data": {
    "userId": "user-123456-abc",
    "newIndex": 5,
    "operations": [
      {"type": "draw", "data": {...}},
      {"type": "draw", "data": {...}}
    ]
  }
}
```

## 🔄 Undo/Redo Strategy

### Global Operation History

The server maintains a global operation history for each room:

```
Operations Array:
[
  {id: "op-1", type: "draw", userId: "user-1", data: {...}, timestamp: 1234567890},
  {id: "op-2", type: "draw", userId: "user-2", data: {...}, timestamp: 1234567891},
  {id: "op-3", type: "clear", userId: "user-1", data: {...}, timestamp: 1234567892},
  {id: "op-4", type: "draw", userId: "user-2", data: {...}, timestamp: 1234567893}
]

Current Index: 3 (pointing to op-4)
```

### Undo Operation

When a user clicks undo:
1. Server decrements the operation index
2. Server sends all active operations (up to new index) to all clients
3. Clients replay all operations to reconstruct canvas state

```
Before Undo:
Index: 3 (4 operations active)

After Undo:
Index: 2 (3 operations active)
Clients replay operations 0, 1, 2
```

### Redo Operation

When a user clicks redo:
1. Server increments the operation index
2. Server sends all active operations (up to new index) to all clients
3. Clients replay all operations

### Conflict Resolution

**Scenario**: User A undoes User B's drawing

**Solution**: 
- The undo is global - it removes the last operation regardless of who drew it
- All clients replay the remaining operations
- This ensures consistency across all clients

**Example**:
```
User A draws → op-1
User B draws → op-2
User A undoes → removes op-2 (User B's drawing)
All clients see User B's drawing disappear
```

## 🎨 Canvas Drawing Implementation

### Drawing Algorithm

1. **Mouse Down**: Save starting position
2. **Mouse Move**: 
   - Draw line from last position to current position
   - Send drawing event to server
   - Update last position
3. **Mouse Up**: Finalize stroke

### Line Drawing

```javascript
// Efficient line drawing using Canvas API
ctx.beginPath();
ctx.moveTo(x0, y0);
ctx.lineTo(x1, y1);
ctx.strokeStyle = color;
ctx.lineWidth = strokeWidth;
ctx.lineCap = 'round';
ctx.lineJoin = 'round';
ctx.stroke();
```

### Eraser Implementation

Uses Canvas composite operation:
```javascript
ctx.globalCompositeOperation = 'destination-out';
// This removes pixels instead of adding them
```

## 🏢 Room Management

### Room Structure

```javascript
class Room {
  roomId: string
  users: Map<userId, userData>
  drawingState: RoomDrawingState
  createdAt: Date
}
```

### Room Lifecycle

1. **Creation**: Room created when first user joins
2. **Active**: Room exists while users are connected
3. **Cleanup**: Room deleted when last user leaves

### Multi-Room Support

Multiple rooms can run simultaneously:
- Each room has isolated drawing state
- Users in different rooms don't see each other's drawings
- Default room ID is "default"

## 📈 Performance Optimizations

### 1. Event Batching
- Drawing events sent per mouse move (high frequency)
- Cursor events sent per mouse move (throttled in UI)
- Reduces network overhead

### 2. Efficient Redrawing
- Only replay operations when undo/redo occurs
- Normal drawing doesn't require full canvas redraw
- Canvas operations are GPU-accelerated

### 3. Memory Management
- Operation history limited to 200 operations per room
- Old operations discarded when limit reached
- Prevents unbounded memory growth

### 4. WebSocket Optimization
- Binary frame support (not currently used)
- Message compression possible with middleware
- Connection pooling handled by ws library

## 🔐 Security Considerations

### Current Implementation
- No authentication (suitable for local/trusted networks)
- No input validation (assumes trusted clients)
- No rate limiting

### Production Recommendations
1. Add user authentication (JWT tokens)
2. Validate drawing coordinates (prevent out-of-bounds)
3. Implement rate limiting per user
4. Use WSS (WebSocket Secure) with SSL/TLS
5. Add CORS headers for cross-origin requests
6. Sanitize user names and colors

## 🚀 Scalability Improvements

### Current Bottlenecks
- Single server instance
- In-memory state (lost on restart)
- No horizontal scaling

### Scaling Strategy
1. **Horizontal Scaling**:
   - Use Redis for shared room state
   - Implement sticky sessions for WebSocket
   - Load balance with nginx/HAProxy

2. **Persistence**:
   - Store operations in database
   - Implement session save/load
   - Add drawing export functionality

3. **Performance**:
   - Implement operation compression
   - Add client-side prediction
   - Use binary WebSocket frames

## 📊 State Management

### Client State
```javascript
{
  userId: string
  userName: string
  userColor: string
  currentTool: 'brush' | 'eraser'
  currentColor: string
  currentStrokeWidth: number
  isDrawing: boolean
  remoteUsers: Map<userId, userData>
  remoteCursors: Map<userId, cursorData>
}
```

### Server State (per Room)
```javascript
{
  roomId: string
  users: Map<userId, userData>
  operations: Array<Operation>
  operationIndex: number
}
```

## 🔄 Connection Lifecycle

```
Client connects
    ↓
WebSocket handshake
    ↓
Client sends user-join
    ↓
Server adds user to room
    ↓
Server sends users-list to new client
    ↓
Server broadcasts user-join to other clients
    ↓
Client ready for drawing
    ↓
... drawing operations ...
    ↓
Client disconnects
    ↓
Server removes user from room
    ↓
Server broadcasts user-leave to other clients
    ↓
Room cleaned up if empty
```

## 📝 Code Organization

### Frontend (`client/`)
- `index.html` - UI structure
- `style.css` - Styling
- `websocket.js` - WebSocket client
- `canvas.js` - Canvas drawing engine
- `main.js` - Application controller

### Backend (`server/`)
- `server.js` - Express + WebSocket server
- `rooms.js` - Room management
- `drawing-state.js` - Drawing state & history

## 🧪 Testing Strategy

### Unit Tests
- Drawing operations
- State management
- Message parsing

### Integration Tests
- Multi-user synchronization
- Undo/redo across users
- User join/leave

### Performance Tests
- Concurrent user load
- Large operation history
- Network latency simulation

