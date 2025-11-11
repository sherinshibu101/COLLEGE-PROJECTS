# Collaborative Drawing Canvas

A real-time multi-user drawing application where multiple people can draw simultaneously on the same canvas with live synchronization.

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

Then open your browser and navigate to `http://localhost:8080`

## 🎮 How to Use

### Single User
1. Open the application in your browser
2. Use the toolbar on the left to:
   - Select **Brush** or **Eraser** tool
   - Pick a color with the color picker
   - Adjust stroke width with the slider
   - Draw on the canvas
   - Use **Undo/Redo** buttons or keyboard shortcuts (Ctrl+Z / Ctrl+Y)
   - Click **Clear** to clear the entire canvas

### Multi-User (Real-time Collaboration)
1. Open the application in multiple browser tabs/windows
2. Each user gets a unique color and name
3. Start drawing in one tab - see it appear in real-time in other tabs
4. Move your mouse - other users see your cursor position
5. Use undo/redo - changes sync to all users
6. Check "Users Online" section to see who's connected

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

### Manual Testing
See `TEST_GUIDE.md` for detailed testing instructions including:
- Single user testing
- Multi-user synchronization
- Feature testing (drawing, eraser, colors, etc.)
- Performance testing
- Browser compatibility

## 🐛 Known Limitations

1. **No Persistence**: Canvas data is not saved to database. Refreshing the page clears the canvas.
2. **No Authentication**: Anyone can join without credentials
3. **Memory Usage**: Very large canvases with many operations may use significant memory
4. **No Drawing Persistence**: No save/load functionality for sessions
5. **Late Joiners**: Users who join after others have already drawn will only see new drawings made after they join (not previous drawings)

## 🚀 Performance Characteristics

- **Latency**: Drawing events are sent in real-time (typically <50ms)
- **Throughput**: Handles 10+ concurrent users smoothly
- **Canvas Size**: Supports full HD (1920x1080) and larger
- **Operation History**: Stores up to 200 operations per room

## 🔐 Security Notes

- No authentication implemented (suitable for local/trusted networks)
- No input validation on drawing data (assumes trusted clients)
- WebSocket connections are unencrypted (use WSS in production)

## 📈 Scalability

Current implementation:
- Single server instance
- In-memory room management
- Suitable for small to medium groups (10-50 users)

For production scaling:
- Use Redis for room state management
- Implement load balancing with multiple server instances
- Add database persistence
- Use WSS (WebSocket Secure) with SSL/TLS

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

## 📝 Time Spent

- Project Setup: 30 minutes
- Frontend Implementation: 1 hour
- Backend Implementation: 1 hour
- Real-time Synchronization: 45 minutes
- Undo/Redo Implementation: 45 minutes
- Testing & Bug Fixes: 1 hour
- Documentation: 45 minutes
- **Total: ~5.5 hours**

## 📄 License

MIT License - Feel free to use this project for learning and development.

## 🤝 Contributing

This is an assignment project. For improvements or bug reports, please create an issue or pull request.

## 📞 Support

For issues or questions:
1. Check `TEST_GUIDE.md` for troubleshooting
2. Review `ARCHITECTURE.md` for technical details
3. Check browser console for error messages
4. Verify server is running: `curl http://localhost:8080/health`

