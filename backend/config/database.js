const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // Try to connect to MongoDB
    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/walking-buddy';
    const conn = await mongoose.connect(mongoUri, {
      serverSelectionTimeoutMS: 5000, // Timeout after 5s instead of 30s
      socketTimeoutMS: 45000, // Close sockets after 45s of inactivity
    });

    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error('Error connecting to MongoDB:', error.message);
    console.log('\n📋 To fix this, you have several options:');
    console.log('\n1. 🚀 EASIEST: Use MongoDB Atlas (Free cloud database)');
    console.log('   - Go to https://www.mongodb.com/atlas');
    console.log('   - Create a free account and cluster');
    console.log('   - Get your connection string and add it to .env file');
    console.log('   - Example: MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/walking-buddy');
    
    console.log('\n2. 💻 Install MongoDB locally:');
    console.log('   - Download from https://www.mongodb.com/try/download/community');
    console.log('   - Install and start the MongoDB service');
    
    console.log('\n3. 🧪 Use in-memory database for testing:');
    console.log('   - The app will work with fake users but data won\'t persist');
    
    console.log('\nFor now, the app will continue with limited functionality...\n');
    
    // Don't exit the process, let the app continue with limited functionality
    return false;
  }
  
  return true;
};

module.exports = connectDB; 