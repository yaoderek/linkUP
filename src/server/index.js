// Import the express framework to build HTTP servers
const express = require('express');
// Import mongoose to connect and interact with MongoDB
const mongoose = require('mongoose');
// Import built-in path utility to work with filesystem paths
const path = require('path');
// Import the opportunities router that provides search endpoints
const opportunitiesRouter = require('./routes/opportunities');

// Create an Express application instance
const app = express();

// Use JSON body parsing middleware so we can accept JSON payloads
app.use(express.json());

// Mount the opportunities router at /api/opportunities
app.use('/api/opportunities', opportunitiesRouter);

// Simple health-check endpoint at the root path for quick verification
app.get('/', (req, res) => {
	// Respond with a small JSON object indicating server is running
	res.json({ status: 'ok', message: 'LinkUp API is running' });
});

// Connect to MongoDB on application start. Use the LinkUp database on localhost.
mongoose.connect('mongodb://127.0.0.1:27017/LinkUp', { useNewUrlParser: true, useUnifiedTopology: true })
	.then(() => {
		// Start listening only after MongoDB connection is established
		const port = process.env.PORT || 3000; // Allow overriding port via environment
		app.listen(port, () => {
			// Log a message indicating the server is up and which port it's on
			console.log(`LinkUp API server listening on port ${port}`);
		});
	})
	.catch(err => {
		// If MongoDB connection fails, log the error and exit process with failure
		console.error('Failed to connect to MongoDB:', err);
		process.exit(1);
	});

// Export app for testing or external usage (optional)
module.exports = app;
