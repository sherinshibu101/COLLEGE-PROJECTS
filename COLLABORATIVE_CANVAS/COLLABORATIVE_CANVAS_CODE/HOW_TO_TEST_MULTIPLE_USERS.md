# 🧪 How to Test Multiple Users

## ✅ Server is Already Running

The server is running on **http://localhost:8080**

---

## 🎯 Method 1: Multiple Browser Tabs (Easiest)

### Step 1: Open First Tab
1. Open your browser
2. Go to **http://localhost:8080**
3. You should see the drawing canvas
4. Look at the **User List** on the right side - you should see yourself listed

### Step 2: Open Second Tab
1. Open a **new tab** in the same browser
2. Go to **http://localhost:8080**
3. You should see another canvas
4. Look at the **User List** - you should now see **2 users** listed

### Step 3: Test Real-time Sync
1. In **Tab 1**, draw something (e.g., a line)
2. **Immediately** look at **Tab 2**
3. You should see the same line appear in Tab 2 in real-time!
4. In **Tab 2**, draw something
5. **Immediately** look at **Tab 1**
6. You should see the same line appear in Tab 1 in real-time!

### Step 4: Test Undo/Redo
1. In **Tab 1**, click the **Undo** button
2. Look at **Tab 2** - the last drawing should disappear from both tabs!
3. In **Tab 2**, click the **Redo** button
4. Look at **Tab 1** - the drawing should reappear in both tabs!

### ✅ What You Should See
- ✅ Both tabs show the same canvas
- ✅ Both tabs show the same user list
- ✅ Drawing in one tab appears in the other tab immediately
- ✅ Undo/Redo works across both tabs
- ✅ Both users have different colors

---

## 🎯 Method 2: Multiple Browser Windows

### Step 1: Open First Window
1. Open your browser
2. Go to **http://localhost:8080**

### Step 2: Open Second Window
1. Open a **new browser window** (not tab)
2. Go to **http://localhost:8080**

### Step 3: Arrange Windows Side-by-Side
1. Resize windows so you can see both at the same time
2. You should see 2 separate canvases

### Step 4: Test Real-time Sync
1. Draw in Window 1
2. See it appear in Window 2 immediately
3. Draw in Window 2
4. See it appear in Window 1 immediately

### ✅ What You Should See
- ✅ Both windows show the same canvas
- ✅ Drawing in one window appears in the other window immediately
- ✅ Both windows show the same user list

---

## 🎯 Method 3: Different Browsers

### Step 1: Open First Browser
1. Open **Chrome** (or Firefox)
2. Go to **http://localhost:8080**

### Step 2: Open Second Browser
1. Open **Firefox** (or Edge)
2. Go to **http://localhost:8080**

### Step 3: Test Real-time Sync
1. Draw in Chrome
2. See it appear in Firefox immediately
3. Draw in Firefox
4. See it appear in Chrome immediately

### ✅ What You Should See
- ✅ Both browsers show the same canvas
- ✅ Drawing in one browser appears in the other browser immediately

---

## 🎯 Method 4: Automated Test (Most Reliable)

### Run the Automated Test
```bash
node test-websocket.js
```

### What the Test Does
- ✅ Simulates 2 users connecting
- ✅ Tests drawing synchronization
- ✅ Tests cursor tracking
- ✅ Tests undo/redo
- ✅ Tests user disconnect

### Expected Output
```
✓ Test 1: Single user connection
✓ Test 2: Two users connection
✓ Test 3: Drawing synchronization
✓ Test 4: Cursor tracking
✓ Test 5: Clear canvas
✓ Test 6: Undo/Redo
✓ Test 7: User disconnect

All tests passed!
```

---

## 📊 What to Look For

### User List
- Should show all connected users
- Each user has a unique color
- When a user joins, they appear in the list
- When a user leaves, they disappear from the list

### Drawing Synchronization
- When User 1 draws, User 2 sees it immediately
- When User 2 draws, User 1 sees it immediately
- Both users see the same drawing

### Cursor Tracking
- You can see where other users are moving their cursor
- Cursor position updates in real-time

### Undo/Redo
- When User 1 clicks Undo, both users see the change
- When User 2 clicks Redo, both users see the change
- Undo/Redo is global (affects all users)

### Colors
- Each user has a different color
- Your drawings appear in your color
- Other users' drawings appear in their color

---

## 🔍 How to Verify It's Working

### Check 1: User List Updates
1. Open Tab 1 - you should see 1 user
2. Open Tab 2 - you should see 2 users in both tabs
3. Close Tab 1 - you should see 1 user in Tab 2

### Check 2: Real-time Drawing
1. Open Tab 1 and Tab 2
2. Draw a line in Tab 1
3. The line should appear in Tab 2 within 50ms (almost instantly)

### Check 3: Undo/Redo Sync
1. Open Tab 1 and Tab 2
2. Draw in Tab 1
3. Click Undo in Tab 1
4. The drawing should disappear from both Tab 1 and Tab 2

### Check 4: Different Colors
1. Open Tab 1 and Tab 2
2. Draw in Tab 1 - your drawing should be one color
3. Draw in Tab 2 - your drawing should be a different color
4. Both colors should be visible on both canvases

---

## 🎮 Interactive Testing

### Test 1: Simple Drawing
1. Open 2 tabs
2. Draw a simple line in Tab 1
3. Verify it appears in Tab 2 immediately

### Test 2: Complex Drawing
1. Open 2 tabs
2. Draw a complex shape in Tab 1
3. Draw a different shape in Tab 2
4. Verify both shapes appear on both canvases

### Test 3: Rapid Drawing
1. Open 2 tabs
2. Draw quickly in Tab 1
3. Verify all lines appear in Tab 2 smoothly

### Test 4: Undo/Redo
1. Open 2 tabs
2. Draw in Tab 1
3. Draw in Tab 2
4. Click Undo in Tab 1 - Tab 1's drawing should disappear from both tabs
5. Click Redo in Tab 2 - Tab 1's drawing should reappear in both tabs

### Test 5: User Join/Leave
1. Open Tab 1 - you should see 1 user
2. Open Tab 2 - you should see 2 users in both tabs
3. Close Tab 1 - you should see 1 user in Tab 2

---

## 📱 Mobile Testing

### Test on Mobile Device
1. Find your computer's IP address
   ```bash
   ipconfig  # Windows
   ifconfig  # Mac/Linux
   ```
2. On mobile, go to **http://YOUR_IP:8080**
3. Draw on mobile
4. See it appear on desktop in real-time

---

## 🐛 Troubleshooting

### Problem: Can't connect to http://localhost:8080
**Solution**: 
- Make sure server is running: `npm start`
- Check if port 8080 is in use: `netstat -ano | findstr :8080`

### Problem: Drawing doesn't sync between tabs
**Solution**:
- Check browser console (F12) for errors
- Refresh the page
- Make sure both tabs show "Connected" status

### Problem: User list doesn't update
**Solution**:
- Refresh the page
- Check browser console for errors
- Make sure WebSocket connection is established

### Problem: Undo/Redo doesn't work
**Solution**:
- Check server logs for errors
- Verify operation history is being tracked
- Try with fresh connection

---

## ✅ Verification Checklist

- [ ] Server is running on http://localhost:8080
- [ ] Can open multiple tabs
- [ ] User list shows all connected users
- [ ] Drawing in one tab appears in other tabs
- [ ] Undo/Redo works across all tabs
- [ ] Each user has a different color
- [ ] Cursor tracking works
- [ ] Automated tests pass (7/7)
- [ ] Can test on mobile device
- [ ] No errors in browser console

---

## 🎉 Success Criteria

✅ **Multiple users are working if:**
1. You can open multiple tabs/windows
2. User list shows all connected users
3. Drawing in one tab appears in other tabs immediately
4. Undo/Redo works across all tabs
5. Each user has a different color
6. Automated tests pass (7/7)

---

## 📞 Quick Commands

```bash
# Start server
npm start

# Run automated tests
node test-websocket.js

# Check if server is running
curl http://localhost:8080/health

# Check connected users
curl http://localhost:8080/api/rooms
```

---

**You're ready to test! Open multiple tabs and start drawing! 🎨**

