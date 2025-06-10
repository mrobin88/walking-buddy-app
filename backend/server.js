const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const cors = require('cors');
require('dotenv').config();

// Database connection
const connectDB = require('./config/database');

// Routes
const authRoutes = require('./routes/auth');
const walkRoutes = require('./routes/walks');

// Models
const User = require('./models/User');
const Walk = require('./models/Walk');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Connect to database
let dbConnected = false;
connectDB().then(connected => {
  dbConnected = connected;
  if (connected) {
    console.log('✅ Database connected successfully');
  } else {
    console.log('⚠️  Running in limited mode - database not available');
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Routes (only enable if database is connected)
if (dbConnected) {
  app.use('/api/auth', authRoutes);
  app.use('/api/walks', walkRoutes);
} else {
  // Fallback routes for when database is not available
  app.get('/api/status', (req, res) => {
    res.json({ 
      status: 'limited', 
      message: 'Database not available. App running in limited mode with fake users only.' 
    });
  });
}

// Page routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.get('/chat', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/chat.html'));
});

app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/admin.html'));
});

// Admin API routes
app.get('/api/admin/stats', async (req, res) => {
  try {
    if (!dbConnected) {
      return res.json({
        totalUsers: connectedUsers.size,
        onlineUsers: connectedUsers.size,
        totalWalks: activeWalks.size,
        activeWalks: activeWalks.size
      });
    }

    const totalUsers = await User.countDocuments();
    const onlineUsers = await User.countDocuments({ isOnline: true });
    const totalWalks = await Walk.countDocuments();
    const activeWalks = await Walk.countDocuments({ status: 'active' });

    res.json({
      totalUsers,
      onlineUsers,
      totalWalks,
      activeWalks
    });
  } catch (error) {
    console.error('Error getting stats:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/api/admin/users', async (req, res) => {
  try {
    if (!dbConnected) {
      const users = Array.from(connectedUsers.values()).map(user => ({
        id: user.id,
        username: user.username,
        email: user.email || `${user.username}@temp.com`,
        isOnline: true,
        lastActive: new Date(),
        isTemporary: user.isTemporary || false
      }));
      return res.json(users);
    }

    const users = await User.find().select('-password').sort({ lastActive: -1 });
    res.json(users);
  } catch (error) {
    console.error('Error getting users:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

app.delete('/api/admin/users/:userId', async (req, res) => {
  try {
    if (!dbConnected) {
      return res.status(400).json({ error: 'Database not available' });
    }

    const { userId } = req.params;
    await User.findByIdAndDelete(userId);
    
    // Remove from connected users if online
    for (const [socketId, user] of connectedUsers) {
      if (user.id === userId) {
        connectedUsers.delete(socketId);
        io.to(socketId).disconnect();
        break;
      }
    }

    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/api/admin/walks', async (req, res) => {
  try {
    if (!dbConnected) {
      const walks = Array.from(activeWalks.values()).map(walk => ({
        id: walk.id || walk._id,
        participants: walk.participants || [],
        status: walk.status || 'active',
        details: walk.details || { startTime: new Date() },
        route: walk.route || {}
      }));
      return res.json(walks);
    }

    const walks = await Walk.find().populate('participants.user', 'username').sort({ 'details.startTime': -1 });
    res.json(walks);
  } catch (error) {
    console.error('Error getting walks:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Store connected users and their data
const connectedUsers = new Map();
const waitingUsers = new Map();
const activeWalks = new Map();

// Fake user data
const fakeUsers = [
  { id: 'fake_user_1', username: 'WalkingBill', lat: 0, lon: 0, isFake: true },
  { id: 'fake_user_2', username: 'ScienceGuy', lat: 0, lon: 0, isFake: true },
  { id: 'fake_user_3', username: 'NatureExplorer', lat: 0, lon: 0, isFake: true }
];

// Calculate position 1km from user (roughly 0.009 degrees)
function calculateFakeUserPosition(userLat, userLon) {
  const offset = 0.009; // approximately 1km
  const angle = Math.random() * 2 * Math.PI; // random direction
  
  const fakeLat = userLat + (offset * Math.cos(angle));
  const fakeLon = userLon + (offset * Math.sin(angle));
  
  return { lat: fakeLat, lon: fakeLon };
}

// Get a random fake user
function getRandomFakeUser(userLat, userLon) {
  const fakeUser = { ...fakeUsers[Math.floor(Math.random() * fakeUsers.length)] };
  const position = calculateFakeUserPosition(userLat, userLon);
  fakeUser.lat = position.lat;
  fakeUser.lon = position.lon;
  return fakeUser;
}

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  // Handle user login (updated for database)
  socket.on('user_login', async ({ username, email, password, isRegistration = false }) => {
    try {
      if (!dbConnected) {
        // Fallback mode - create temporary user
        const tempUser = {
          id: socket.id,
          username: username || `User_${socket.id.slice(-4)}`,
          email: email || `${username}@temp.com`,
          isTemporary: true
        };
        
        connectedUsers.set(socket.id, {
          id: tempUser.id,
          username: tempUser.username,
          lat: null,
          lon: null,
          isFake: false,
          isTemporary: true
        });
        
        socket.userId = tempUser.id;
        
        socket.emit('login_success', { 
          username: tempUser.username,
          user: {
            id: tempUser.id,
            username: tempUser.username,
            email: tempUser.email,
            isTemporary: true
          }
        });
        
        console.log('Temporary user login:', tempUser.username);
        return;
      }

      let user;
      
      if (isRegistration) {
        // Registration logic
        const existingUser = await User.findOne({ $or: [{ email }, { username }] });
        if (existingUser) {
          socket.emit('login_error', { message: 'User already exists' });
          return;
        }
        
        const bcrypt = require('bcryptjs');
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        
        user = new User({
          username,
          email,
          password: hashedPassword
        });
        
        await user.save();
      } else {
        // Login logic
        user = await User.findOne({ email });
        if (!user) {
          socket.emit('login_error', { message: 'Invalid credentials' });
          return;
        }
        
        const bcrypt = require('bcryptjs');
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
          socket.emit('login_error', { message: 'Invalid credentials' });
          return;
        }
      }
      
      // Update user status
      user.isOnline = true;
      user.lastActive = new Date();
      await user.save();
      
      // Store user data in socket
      connectedUsers.set(socket.id, {
        id: user._id.toString(),
        username: user.username,
        lat: null,
        lon: null,
        isFake: false
      });
      
      socket.userId = user._id.toString();
      
      socket.emit('login_success', { 
        username: user.username,
        user: {
          id: user._id,
          username: user.username,
          email: user.email,
          profile: user.profile,
          stats: user.stats
        }
      });
      
      console.log('User login successful:', user.username);
    } catch (error) {
      console.error('Login error:', error);
      socket.emit('login_error', { message: 'Server error' });
    }
  });

  // Handle get connected users request
  socket.on('get_connected_users', () => {
    const users = Array.from(connectedUsers.values());
    socket.emit('connected_users', users);
  });

  // Handle location update
  socket.on('update_location', async ({ lat, lon }) => {
    try {
      const user = connectedUsers.get(socket.id);
      if (user) {
        user.lat = lat;
        user.lon = lon;
        
        // Update location in database if connected
        if (dbConnected && socket.userId && !user.isTemporary) {
          await User.findByIdAndUpdate(socket.userId, {
            'location.lat': lat,
            'location.lon': lon,
            'location.lastUpdated': new Date()
          });
        }
        
        console.log('Location updated for:', user.username, { lat, lon });
      }
    } catch (error) {
      console.error('Location update error:', error);
    }
  });

  // Handle walk request (updated for database)
  socket.on('request_walk', async ({ lat, lon }) => {
    try {
      const user = connectedUsers.get(socket.id);
      if (!user) {
        socket.emit('error', { message: 'Please login first' });
        return;
      }

      user.lat = lat;
      user.lon = lon;
      
      // Update location in database if connected
      if (dbConnected && socket.userId && !user.isTemporary) {
        await User.findByIdAndUpdate(socket.userId, {
          'location.lat': lat,
          'location.lon': lon,
          'location.lastUpdated': new Date()
        });
      }
      
      // Check if there are any real users waiting
      let foundRealMatch = false;
      for (const [waitingId, waitingUser] of waitingUsers) {
        if (waitingId !== socket.id && !waitingUser.isFake) {
          // Calculate distance (simple approximation)
          const distance = Math.sqrt(
            Math.pow(lat - waitingUser.lat, 2) + Math.pow(lon - waitingUser.lon, 2)
          );
          
          if (distance < 0.01) { // Within ~1km
            // Match found with real user
            waitingUsers.delete(waitingId);
            
            // Create walk in database if connected
            if (dbConnected) {
              const walk = new Walk({
                participants: [
                  { user: user.id, username: user.username },
                  { user: waitingUser.id, username: waitingUser.username }
                ],
                route: {
                  startLocation: { lat, lon }
                },
                details: {
                  distance: 0,
                  duration: 0,
                  startTime: new Date()
                }
              });
              
              await walk.save();
              activeWalks.set(walk._id.toString(), walk);
            }
            
            io.to(waitingId).emit('match_found', {
              id: socket.id,
              username: user.username,
              lat: lat,
              lon: lon,
              walkId: dbConnected ? walk._id.toString() : null
            });
            
            socket.emit('match_found', {
              id: waitingId,
              username: waitingUser.username,
              lat: waitingUser.lat,
              lon: waitingUser.lon,
              walkId: dbConnected ? walk._id.toString() : null
            });
            
            foundRealMatch = true;
            break;
          }
        }
      }

      if (!foundRealMatch) {
        // No real match found, create fake user
        const fakeUser = getRandomFakeUser(lat, lon);
        console.log('Creating fake user:', fakeUser.username, 'at', { lat: fakeUser.lat, lon: fakeUser.lon });
        
        // Add fake user to waiting users temporarily
        waitingUsers.set(fakeUser.id, fakeUser);
        
        // Simulate fake user accepting the request
        setTimeout(async () => {
          waitingUsers.delete(fakeUser.id);
          
          // Create walk with fake user if database connected
          if (dbConnected) {
            const walk = new Walk({
              participants: [
                { user: user.id, username: user.username },
                { user: fakeUser.id, username: fakeUser.username, isFake: true }
              ],
              route: {
                startLocation: { lat, lon }
              },
              details: {
                distance: 0,
                duration: 0,
                startTime: new Date()
              }
            });
            
            await walk.save();
            activeWalks.set(walk._id.toString(), walk);
          }
          
          socket.emit('match_found', {
            id: fakeUser.id,
            username: fakeUser.username,
            lat: fakeUser.lat,
            lon: fakeUser.lon,
            isFake: true,
            walkId: dbConnected ? walk._id.toString() : null
          });
        }, 1000 + Math.random() * 2000); // Random delay 1-3 seconds
      } else {
        // Add current user to waiting list for potential future matches
        waitingUsers.set(socket.id, user);
      }
    } catch (error) {
      console.error('Walk request error:', error);
      socket.emit('error', { message: 'Server error' });
    }
  });

  // Handle chat messages (updated for database)
  socket.on('chat_message', async ({ to, message, walkId }) => {
    try {
      const user = connectedUsers.get(socket.id);
      if (!user) return;

      // Save message to database if walkId is provided and database is connected
      if (dbConnected && walkId && activeWalks.has(walkId)) {
        const walk = activeWalks.get(walkId);
        await walk.addChatMessage(user.id, user.username, message);
      }

      if (to && to.startsWith('fake_user_')) {
        // Handle fake user responses
        const fakeResponses = [
          "Hey! Great to meet you! I love walking and exploring nature.",
          "The weather is perfect for a walk today, isn't it?",
          "I'm always up for a good conversation while walking.",
          "Have you been to any interesting places lately?",
          "Walking is such a great way to clear your mind.",
          "I enjoy learning about science and nature during my walks.",
          "What's your favorite walking route?",
          "I find walking helps me think better.",
          "It's amazing how much you can discover just by walking around.",
          "I'm always curious about new places and people."
        ];
        
        const response = fakeResponses[Math.floor(Math.random() * fakeResponses.length)];
        
        // Simulate typing delay
        setTimeout(() => {
          socket.emit('chat_message', {
            from: to,
            username: to.startsWith('fake_user_1') ? 'WalkingBill' : 
                     to.startsWith('fake_user_2') ? 'ScienceGuy' : 'NatureExplorer',
            message: response
          });
        }, 1000 + Math.random() * 3000); // 1-4 second delay
      } else {
        // Forward message to real user
        io.to(to).emit('chat_message', {
          from: socket.id,
          username: user.username,
          message: message
        });
      }
    } catch (error) {
      console.error('Chat message error:', error);
    }
  });

  // Handle walk end
  socket.on('end_walk', async ({ walkId, distance, duration, endLocation }) => {
    try {
      if (dbConnected && walkId && activeWalks.has(walkId)) {
        const walk = activeWalks.get(walkId);
        
        walk.status = 'completed';
        walk.route.endLocation = endLocation;
        walk.details.endTime = new Date();
        walk.details.distance = distance;
        walk.details.duration = duration;
        
        await walk.save();
        activeWalks.delete(walkId);
        
        // Update user stats
        const user = await User.findById(socket.userId);
        if (user) {
          await user.updateWalkStats(distance, duration);
        }
        
        socket.emit('walk_ended', { walkId });
      }
    } catch (error) {
      console.error('End walk error:', error);
    }
  });

  socket.on('disconnect', async () => {
    console.log('User disconnected:', socket.id);
    
    // Remove from connected users
    const user = connectedUsers.get(socket.id);
    if (user) {
      connectedUsers.delete(socket.id);
      waitingUsers.delete(socket.id);
      
      // Update user status in database if connected
      if (dbConnected && socket.userId && !user.isTemporary) {
        try {
          await User.findByIdAndUpdate(socket.userId, {
            isOnline: false,
            lastActive: new Date()
          });
        } catch (error) {
          console.error('Update user status error:', error);
        }
      }
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

