const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    maxlength: 20
  },
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
  password: {
    type: String,
    required: true
  },
  profile: {
    firstName: {
      type: String,
      trim: true,
      maxlength: 50
    },
    lastName: {
      type: String,
      trim: true,
      maxlength: 50
    },
    bio: {
      type: String,
      maxlength: 500
    },
    profilePicture: {
      type: String // URL to stored image
    },
    interests: [{
      type: String,
      enum: ['nature', 'science', 'history', 'art', 'music', 'sports', 'technology', 'food', 'travel']
    }],
    walkingPace: {
      type: String,
      enum: ['slow', 'moderate', 'fast'],
      default: 'moderate'
    },
    preferredDistance: {
      type: Number, // in kilometers
      default: 5
    }
  },
  stats: {
    totalWalks: {
      type: Number,
      default: 0
    },
    totalDistance: {
      type: Number,
      default: 0 // in kilometers
    },
    totalTime: {
      type: Number,
      default: 0 // in minutes
    },
    averageRating: {
      type: Number,
      default: 0,
      min: 0,
      max: 5
    },
    totalRatings: {
      type: Number,
      default: 0
    }
  },
  location: {
    lat: Number,
    lon: Number,
    lastUpdated: {
      type: Date,
      default: Date.now
    }
  },
  isOnline: {
    type: Boolean,
    default: false
  },
  lastActive: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for location-based queries
userSchema.index({ location: '2dsphere' });

// Virtual for full name
userSchema.virtual('fullName').get(function() {
  return `${this.profile.firstName || ''} ${this.profile.lastName || ''}`.trim();
});

// Method to update walk statistics
userSchema.methods.updateWalkStats = function(distance, duration, rating) {
  this.stats.totalWalks += 1;
  this.stats.totalDistance += distance;
  this.stats.totalTime += duration;
  
  if (rating) {
    const totalRating = (this.stats.averageRating * this.stats.totalRatings) + rating;
    this.stats.totalRatings += 1;
    this.stats.averageRating = totalRating / this.stats.totalRatings;
  }
  
  return this.save();
};

module.exports = mongoose.model('User', userSchema); 