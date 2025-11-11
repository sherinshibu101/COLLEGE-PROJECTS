## 🎯 Features

- **Real-time Drawing Sync**: See other users' drawings as they draw (not after they finish)
- **Multiple Drawing Tools**: Brush and eraser with adjustable stroke width
- **Color Picker**: Choose from any color for your drawings
- **User Indicators**: See where other users are drawing with cursor tracking
- **Global Undo/Redo**: Undo/redo operations that sync across all users
- **User Management**: See who's online with color-coded user list
- **Responsive Design**: Works on desktop and mobile browsers
- **Multi-room Support**: Multiple isolated canvases can run simultaneously

## 🚀 Quick Start

### Prerequisites
- Node.js 14+ installed
- npm or yarn package manager

### Installation

```bash
# Clone or download the project
cd collaborative-canvas

# Install dependencies
npm install
```

### Running the Application

```bash
# Start the server
npm start

# Server will run on http://localhost:8080
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `B` | Select Brush tool |
| `E` | Select Eraser tool |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |

## 📁 Project Structure

```
collaborative-canvas/
├── client/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Styling
│   ├── canvas.js           # Canvas drawing engine
│   ├── websocket.js        # WebSocket client
│   └── main.js             # Application controller
├── server/
│   ├── server.js           # Express + WebSocket server
│   ├── rooms.js            # Room management
│   └── drawing-state.js    # Drawing state & history
├── package.json            # Dependencies
├── README.md               # This file
├── ARCHITECTURE.md         # Technical architecture
└── TEST_GUIDE.md          # Testing instructions
```

## 🔧 Technical Stack

- **Frontend**: Vanilla JavaScript + HTML5 Canvas (no frameworks)
- **Backend**: Node.js + Express + WebSocket (ws library)
- **Communication**: WebSocket for real-time synchronization
- **No external drawing libraries** - all canvas operations implemented from scratch

## 📊 API Endpoints

### HTTP Endpoints
- `GET /health` - Server health check
- `GET /api/rooms` - Get list of active rooms and connected users

### WebSocket Messages

**Client → Server:**
- `user-join` - User joins the room
- `draw` - Drawing event (line segment)
- `cursor-move` - Cursor position update
- `clear` - Clear canvas
- `undo` - Undo last operation
- `redo` - Redo last undone operation

**Server → Client:**
- `user-join` - New user joined
- `user-leave` - User left
- `users-list` - List of all connected users
- `draw` - Remote drawing event
- `cursor-move` - Remote cursor position
- `remote-clear` - Canvas cleared by another user
- `undo` - Undo operation (with updated state)
- `redo` - Redo operation (with updated state)

## 🧪 Testing

### Automated Tests
```bash
# Run WebSocket tests
node test-websocket.js
```

## 🐛 Known Limitations

1. **No Persistence**: Canvas data is not saved to database. Refreshing the page clears the canvas.
2. **No Authentication**: Anyone can join without credentials
3. **Memory Usage**: Very large canvases with many operations may use significant memory
4. **No Drawing Persistence**: No save/load functionality for sessions
5. **Late Joiners**: Users who join after others have already drawn will only see new drawings made after they join (not previous drawings)

## 🔐 Security Notes

- No authentication implemented (suitable for local/trusted networks)
- No input validation on drawing data (assumes trusted clients)
- WebSocket connections are unencrypted (use WSS in production)

## 🛠️ Development

### Adding New Features

1. **New Drawing Tool**: Add to `canvas.js` `drawLine()` method
2. **New Message Type**: Add handler in `server.js` and client event listener
3. **New UI Element**: Add to `index.html` and style in `style.css`

### Debugging

- Open browser DevTools (F12) to see console logs
- Check server logs in terminal
- Use `curl` to test HTTP endpoints
- Use WebSocket client tools to test messages


