const mongoose = require('mongoose');

const walkSchema = new mongoose.Schema({
  participants: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    username: String,
    joinedAt: {
      type: Date,
      default: Date.now
    },
    leftAt: Date,
    rating: {
      type: Number,
      min: 1,
      max: 5
    },
    review: {
      type: String,
      maxlength: 500
    }
  }],
  route: {
    startLocation: {
      lat: Number,
      lon: Number,
      address: String
    },
    endLocation: {
      lat: Number,
      lon: Number,
      address: String
    },
    waypoints: [{
      lat: Number,
      lon: Number,
      timestamp: Date
    }]
  },
  details: {
    distance: {
      type: Number, // in kilometers
      required: true
    },
    duration: {
      type: Number, // in minutes
      required: true
    },
    startTime: {
      type: Date,
      required: true
    },
    endTime: Date,
    pace: {
      type: Number // minutes per kilometer
    },
    weather: {
      temperature: Number,
      conditions: String,
      humidity: Number
    }
  },
  photos: [{
    url: {
      type: String,
      required: true
    },
    caption: String,
    uploadedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    uploadedAt: {
      type: Date,
      default: Date.now
    },
    location: {
      lat: Number,
      lon: Number
    }
  }],
  chat: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    username: String,
    message: {
      type: String,
      required: true
    },
    timestamp: {
      type: Date,
      default: Date.now
    }
  }],
  status: {
    type: String,
    enum: ['active', 'completed', 'cancelled'],
    default: 'active'
  },
  tags: [{
    type: String,
    enum: ['nature', 'city', 'historical', 'scenic', 'exercise', 'social', 'exploration']
  }]
}, {
  timestamps: true
});

// Index for location-based queries
walkSchema.index({ 'route.startLocation': '2dsphere' });

// Pre-save middleware to calculate pace
walkSchema.pre('save', function(next) {
  if (this.details.distance && this.details.duration) {
    this.details.pace = this.details.duration / this.details.distance;
  }
  next();
});

// Method to add participant
walkSchema.methods.addParticipant = function(userId, username) {
  const existingParticipant = this.participants.find(p => p.user.toString() === userId.toString());
  if (!existingParticipant) {
    this.participants.push({
      user: userId,
      username: username
    });
  }
  return this.save();
};

// Method to remove participant
walkSchema.methods.removeParticipant = function(userId) {
  const participant = this.participants.find(p => p.user.toString() === userId.toString());
  if (participant) {
    participant.leftAt = new Date();
  }
  return this.save();
};

// Method to add photo
walkSchema.methods.addPhoto = function(photoData) {
  this.photos.push(photoData);
  return this.save();
};

// Method to add chat message
walkSchema.methods.addChatMessage = function(userId, username, message) {
  this.chat.push({
    user: userId,
    username: username,
    message: message
  });
  return this.save();
};

module.exports = mongoose.model('Walk', walkSchema); 