const express = require('express');
const Walk = require('../models/Walk');
const User = require('../models/User');
const auth = require('../middleware/auth');
const upload = require('../middleware/upload');

const router = express.Router();

// Create a new walk
router.post('/', auth, async (req, res) => {
  try {
    const { startLocation, distance, duration, tags } = req.body;
    
    const walk = new Walk({
      participants: [{
        user: req.user._id,
        username: req.user.username
      }],
      route: {
        startLocation: startLocation
      },
      details: {
        distance: distance,
        duration: duration,
        startTime: new Date()
      },
      tags: tags || []
    });

    await walk.save();
    
    res.json(walk);
  } catch (error) {
    console.error('Create walk error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get all walks for a user
router.get('/my-walks', auth, async (req, res) => {
  try {
    const walks = await Walk.find({
      'participants.user': req.user._id
    }).populate('participants.user', 'username profile.firstName profile.lastName profile.profilePicture')
      .sort({ createdAt: -1 });
    
    res.json(walks);
  } catch (error) {
    console.error('Get my walks error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get walk by ID
router.get('/:id', auth, async (req, res) => {
  try {
    const walk = await Walk.findById(req.params.id)
      .populate('participants.user', 'username profile.firstName profile.lastName profile.profilePicture')
      .populate('photos.uploadedBy', 'username profile.firstName profile.lastName');
    
    if (!walk) {
      return res.status(404).json({ message: 'Walk not found' });
    }
    
    res.json(walk);
  } catch (error) {
    console.error('Get walk error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Join a walk
router.post('/:id/join', auth, async (req, res) => {
  try {
    const walk = await Walk.findById(req.params.id);
    
    if (!walk) {
      return res.status(404).json({ message: 'Walk not found' });
    }
    
    if (walk.status !== 'active') {
      return res.status(400).json({ message: 'Walk is not active' });
    }
    
    await walk.addParticipant(req.user._id, req.user.username);
    
    res.json(walk);
  } catch (error) {
    console.error('Join walk error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// End a walk
router.put('/:id/end', auth, async (req, res) => {
  try {
    const { endLocation, distance, duration } = req.body;
    
    const walk = await Walk.findById(req.params.id);
    
    if (!walk) {
      return res.status(404).json({ message: 'Walk not found' });
    }
    
    // Check if user is a participant
    const isParticipant = walk.participants.some(p => p.user.toString() === req.user._id.toString());
    if (!isParticipant) {
      return res.status(403).json({ message: 'Not authorized' });
    }
    
    walk.status = 'completed';
    walk.route.endLocation = endLocation;
    walk.details.endTime = new Date();
    walk.details.distance = distance;
    walk.details.duration = duration;
    
    await walk.save();
    
    // Update user stats
    const user = await User.findById(req.user._id);
    await user.updateWalkStats(distance, duration);
    
    res.json(walk);
  } catch (error) {
    console.error('End walk error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Add photo to walk
router.post('/:id/photos', auth, upload.single('photo'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' });
    }
    
    const walk = await Walk.findById(req.params.id);
    
    if (!walk) {
      return res.status(404).json({ message: 'Walk not found' });
    }
    
    const photoData = {
      url: `/uploads/${req.file.filename}`,
      caption: req.body.caption || '',
      uploadedBy: req.user._id,
      location: req.body.location ? JSON.parse(req.body.location) : null
    };
    
    await walk.addPhoto(photoData);
    
    res.json(walk);
  } catch (error) {
    console.error('Add photo error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Rate a walk participant
router.post('/:id/rate', auth, async (req, res) => {
  try {
    const { participantId, rating, review } = req.body;
    
    const walk = await Walk.findById(req.params.id);
    
    if (!walk) {
      return res.status(404).json({ message: 'Walk not found' });
    }
    
    const participant = walk.participants.find(p => p._id.toString() === participantId);
    if (!participant) {
      return res.status(404).json({ message: 'Participant not found' });
    }
    
    participant.rating = rating;
    participant.review = review;
    
    await walk.save();
    
    // Update user stats
    const user = await User.findById(participant.user);
    if (user) {
      await user.updateWalkStats(0, 0, rating);
    }
    
    res.json(walk);
  } catch (error) {
    console.error('Rate participant error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get nearby walks
router.get('/nearby', auth, async (req, res) => {
  try {
    const { lat, lon, maxDistance = 10 } = req.query; // maxDistance in km
    
    const walks = await Walk.find({
      status: 'active',
      'route.startLocation': {
        $near: {
          $geometry: {
            type: 'Point',
            coordinates: [parseFloat(lon), parseFloat(lat)]
          },
          $maxDistance: maxDistance * 1000 // Convert to meters
        }
      }
    }).populate('participants.user', 'username profile.firstName profile.lastName profile.profilePicture')
      .limit(20);
    
    res.json(walks);
  } catch (error) {
    console.error('Get nearby walks error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 