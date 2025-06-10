const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, '../public')));

// Store users: { socketId: { lat, lon, lastSeen, username } }
const users = {};

// Store matches: { socketId: buddySocketId }
const matches = {};

// Log active users periodically
setInterval(() => {
  console.log('\nActive Users:', Object.keys(users).length);
  Object.entries(users).forEach(([id, data]) => {
    console.log(`User ${data.username || id}:`, {
      location: `[${data.lat.toFixed(4)}, ${data.lon.toFixed(4)}]`,
      matched: matches[id] ? 'Yes' : 'No'
    });
  });
}, 5000);

io.on('connection', (socket) => {
  console.log('\nNew user connected:', socket.id);

  // Handle user login
  socket.on('user_login', ({ username }) => {
    console.log(`User ${socket.id} logged in as:`, username);
    users[socket.id] = {
      username,
      lat: null,
      lon: null,
      lastSeen: Date.now()
    };
    
    socket.emit('login_success', { username, user: { username } });
  });

  // Save user location on request_walk
  socket.on('request_walk', ({ lat, lon }) => {
    console.log(`\nUser ${socket.id} requesting walk at:`, { lat, lon });
    
    if (!users[socket.id]) {
      socket.emit('error', { message: 'Please login first' });
      return;
    }
    
    users[socket.id].lat = lat;
    users[socket.id].lon = lon;
    users[socket.id].lastSeen = Date.now();

    // Find another user nearby who is not matched yet
    const buddyId = Object.keys(users).find(id => {
      if (id === socket.id || matches[id] || !users[id].lat || !users[id].lon) return false;
      
      const distance = calculateDistance(users[socket.id], users[id]);
      console.log(`Distance between ${users[socket.id].username || socket.id} and ${users[id].username || id}:`, distance.toFixed(2), 'miles');
      
      return distance < 100; // 100 miles threshold
    });

    if (buddyId) {
      console.log(`\nMatch found! ${users[socket.id].username || socket.id} matched with ${users[buddyId].username || buddyId}`);
      
      // Mark both as matched
      matches[socket.id] = buddyId;
      matches[buddyId] = socket.id;

      // Notify both users
      socket.emit('match_found', { 
        id: buddyId, 
        username: users[buddyId].username,
        lat: users[buddyId].lat, 
        lon: users[buddyId].lon 
      });
      
      io.to(buddyId).emit('match_found', { 
        id: socket.id, 
        username: users[socket.id].username,
        lat, 
        lon 
      });
    } else {
      console.log(`\nNo match found for ${users[socket.id].username || socket.id}`);
      socket.emit('no_match');
    }
  });

  // Handle location updates
  socket.on('update_location', ({ lat, lon }) => {
    if (users[socket.id]) {
      users[socket.id].lat = lat;
      users[socket.id].lon = lon;
      users[socket.id].lastSeen = Date.now();
    }
  });

  // Relay chat messages between matched users
  socket.on('chat_message', ({ to, message }) => {
    if (matches[socket.id] === to) {
      console.log(`\nChat message from ${users[socket.id]?.username || socket.id} to ${users[to]?.username || to}:`, message);
      io.to(to).emit('chat_message', { 
        from: socket.id, 
        username: users[socket.id]?.username,
        message 
      });
    }
  });

  socket.on('disconnect', () => {
    console.log('\nUser disconnected:', users[socket.id]?.username || socket.id);

    // Remove user & notify buddy if any
    const buddyId = matches[socket.id];
    if (buddyId) {
      console.log(`Notifying buddy ${users[buddyId]?.username || buddyId} of disconnect`);
      io.to(buddyId).emit('buddy_disconnected');
      delete matches[buddyId];
    }
    delete matches[socket.id];
    delete users[socket.id];
  });
});

// Helper: Calculate distance in miles using Haversine formula
function calculateDistance(userA, userB) {
  const R = 3959; // Earth's radius in miles
  const dLat = toRad(userB.lat - userA.lat);
  const dLon = toRad(userB.lon - userA.lon);
  const lat1 = toRad(userA.lat);
  const lat2 = toRad(userB.lat);

  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function toRad(degrees) {
  return degrees * Math.PI / 180;
}

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`\nServer running on port ${PORT}`);
  console.log('Waiting for connections...');
});
