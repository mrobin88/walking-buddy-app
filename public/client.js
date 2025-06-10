// Client-side code
let map;
let userMarker;
let buddyMarker;
let socket;
let currentBuddyId = null;
let currentUsername = '';
let isLoggedIn = false;

// Initialize socket connection
function initializeSocket() {
  socket = io();
  console.log('Socket connected:', socket.id);

  // Handle socket events
  socket.on('login_success', ({ username, user }) => {
    console.log('Login successful:', username);
    currentUsername = username;
    document.getElementById('currentUsername').textContent = username;
    showApp();
  });

  socket.on('login_error', ({ message }) => {
    console.error('Login error:', message);
    alert('Login failed: ' + message);
  });

  socket.on('match_found', ({ id, username, lat, lon, walkId }) => {
    console.log('Match found with buddy:', username, 'at location:', { lat, lon });
    currentBuddyId = id;
    updateStatus(`Found a walking buddy: ${username}! You can start chatting.`);
    
    // Add buddy marker
    buddyMarker = L.marker([lat, lon]).addTo(map)
      .bindPopup(`Your walking buddy: ${username}`);
      
    // Add a line between buddies
    const userPos = userMarker.getLatLng();
    L.polyline([[userPos.lat, userPos.lng], [lat, lon]], {
      color: 'blue',
      weight: 2,
      opacity: 0.6,
      dashArray: '5, 10'
    }).addTo(map);
    
    // Add welcome message
    addMessage('System', `You are now connected with ${username}!`);
  });

  socket.on('no_match', () => {
    console.log('No match found');
    updateStatus('No walking buddy found nearby. Try again later!');
  });

  socket.on('buddy_disconnected', () => {
    console.log('Buddy disconnected');
    updateStatus('Your walking buddy has disconnected. Click the button to find a new buddy.');
    if (buddyMarker) {
      map.removeLayer(buddyMarker);
    }
    currentBuddyId = null;
    addMessage('System', 'Your walking buddy has disconnected.');
  });

  socket.on('chat_message', ({ from, username, message }) => {
    console.log('Received chat message:', { from, username, message });
    addMessage(username || 'Buddy', message);
  });

  socket.on('error', ({ message }) => {
    console.error('Server error:', message);
    updateStatus('Error: ' + message);
  });
}

// Show the main app after login
function showApp() {
  document.getElementById('loginView').style.display = 'none';
  document.getElementById('appView').style.display = 'block';
  
  // Initialize the map
  map = L.map('map').setView([0, 0], 2);
  
  // Add the tile layer (OpenStreetMap)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // Try to get user's location
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        console.log('Got user location:', { latitude, longitude });
        map.setView([latitude, longitude], 13);
        
        // Add user marker
        userMarker = L.marker([latitude, longitude]).addTo(map)
          .bindPopup('Your location')
          .openPopup();
          
        // Send location to server
        socket.emit('update_location', { lat: latitude, lon: longitude });
        
        updateStatus('Ready to find a buddy! Click the button above.');
      },
      (error) => {
        console.error('Error getting location:', error);
        updateStatus('Please enable location services to use this app');
      }
    );
  }

  // Add event listener for chat input
  const chatInput = document.getElementById('chatInput');
  chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  });
}

// Login function
function login() {
  const usernameInput = document.getElementById('usernameInput');
  const username = usernameInput.value.trim();
  
  if (!username) {
    alert('Please enter a username');
    return;
  }
  
  if (username.length > 20) {
    alert('Username must be 20 characters or less');
    return;
  }
  
  // Initialize socket if not already done
  if (!socket) {
    initializeSocket();
  }
  
  // Send login request
  socket.emit('user_login', { username });
}

// Function to update status message
function updateStatus(message) {
  console.log('Updating status:', message);
  const statusDiv = document.getElementById('status-message');
  if (statusDiv) {
    statusDiv.textContent = message;
  } else {
    console.error('Status message div not found!');
  }
}

// Function to add a message to the chat
function addMessage(sender, message) {
  console.log('Adding message to chat:', { sender, message });
  const messagesDiv = document.getElementById('messages');
  if (!messagesDiv) {
    console.error('Messages div not found!');
    return;
  }
  
  const messageElement = document.createElement('p');
  messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
  messagesDiv.appendChild(messageElement);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Function called when "Find Buddy" button is clicked
function findBuddy() {
  console.log('Find buddy button clicked');
  if (!userMarker) {
    updateStatus('Please allow location access to find a buddy');
    return;
  }

  if (currentBuddyId) {
    updateStatus('You already have a buddy!');
    return;
  }

  updateStatus('Searching for a walking buddy...');
  
  const { lat, lng } = userMarker.getLatLng();
  console.log('Requesting walk at location:', { lat, lng });
  socket.emit('request_walk', { lat, lon: lng });
}

// Function to send chat messages
function sendMessage() {
  console.log('Attempting to send message');
  const input = document.getElementById('chatInput');
  if (!input) {
    console.error('Chat input not found!');
    return;
  }

  const message = input.value.trim();
  console.log('Message to send:', message);
  
  if (message && socket && currentBuddyId) {
    console.log('Sending message to buddy:', currentBuddyId);
    socket.emit('chat_message', { 
      to: currentBuddyId,
      message 
    });
    
    addMessage(currentUsername, message);
    input.value = '';
  } else if (message && !currentBuddyId) {
    console.log('No buddy found, cannot send message');
    updateStatus('You need to find a buddy first!');
  } else {
    console.log('Message empty or socket not connected');
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  console.log('Page loaded, waiting for login...');
  
  // Add enter key support for login
  const usernameInput = document.getElementById('usernameInput');
  usernameInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      login();
    }
  });
}); 