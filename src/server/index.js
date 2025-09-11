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

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, '../../public')));

// Serve the main page
app.get('/', (req, res) => {
	res.sendFile(path.join(__dirname, '../../public/index.html'));
});

// Mount the opportunities router at /api/opportunities
app.use('/api/opportunities', opportunitiesRouter);

// Import the Opportunity model so the semantic endpoint can query the DB
const Opportunity = require('./models/opportunity');

// Import vector search functionality
const { spawn } = require('child_process');
const path = require('path');

// Helper: vector-based semantic search using OpenAI embeddings
async function vectorSearch(query, limit = 10, minResults = 3, threshold = 0.75) {
	return new Promise((resolve, reject) => {
		// Call our Python vector search script
		const pythonScript = path.join(__dirname, '../../vector_search.py');
		const pythonProcess = spawn('python3', [
			pythonScript, 
			'--query', query, 
			'--limit', limit.toString(),
			'--min_results', minResults.toString(),
			'--threshold', threshold.toString()
		]);
		
		let output = '';
		let error = '';
		
		pythonProcess.stdout.on('data', (data) => {
			output += data.toString();
		});
		
		pythonProcess.stderr.on('data', (data) => {
			error += data.toString();
		});
		
		pythonProcess.on('close', (code) => {
			if (code !== 0) {
				reject(new Error(`Python script failed: ${error}`));
				return;
			}
			
			try {
				const results = JSON.parse(output);
				resolve(results);
			} catch (parseError) {
				reject(new Error(`Failed to parse Python output: ${parseError.message}`));
			}
		});
	});
}

// GET /api/semantic-search/:searchQuery
// Route param: searchQuery (natural-language query)
// Optional query param: ?limit=n
// Returns: top-matching opportunities using vector similarity search.
app.get('/api/semantic-search/:searchQuery', async (req, res) => {
	try {
		// Extract the searchQuery from the route params and optional limit from query string
		const query = req.params.searchQuery;
		const limit = req.query.limit ? Number(req.query.limit) : 10;

		// Validate input
		if (!query || typeof query !== 'string') {
			return res.status(400).json({ error: 'Missing or invalid searchQuery in URL' });
		}

		// Use vector search to find similar opportunities with dynamic threshold
		const vectorResults = await vectorSearch(query, limit, 3, 0.75);
		
		// Format results to match expected API response
		const results = vectorResults.map((opportunity, index) => ({
			score: 1.0 - (index * 0.1), // Approximate similarity score based on ranking
			opportunity: opportunity
		}));

		// Respond with the ranked results
		return res.json({ 
			query, 
			results,
			search_type: 'vector_similarity',
			total_found: results.length
		});
	} catch (error) {
		console.error('Vector search error:', error);
		return res.status(500).json({ 
			error: 'Vector search failed', 
			details: error.message 
		});
	}
});

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
