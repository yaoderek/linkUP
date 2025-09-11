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

// Import the Opportunity model so the semantic endpoint can query the DB
const Opportunity = require('./models/opportunity');

// Helper: simple semantic scoring function that ranks an opportunity for a given query
// This is an offline/simple approach: it calculates token overlap, boosts tag matches,
// and prefers more recently updated entries. For production, replace with an embedding
// model or a dedicated semantic-search service.
function scoreOpportunity(opportunity, query) {
	// Lowercase the query and split into words for simple token matching
	const q = (query || '').toLowerCase();
	const tokens = q.split(/\W+/).filter(Boolean);

	// Build a searchable string from the opportunity
	const hay = [
		opportunity.organization_name,
		opportunity.activity_name,
		opportunity.activity_description,
		opportunity.program_description,
		...(opportunity.tags && opportunity.tags.categories ? opportunity.tags.categories : [])
	].filter(Boolean).join(' ').toLowerCase();

	// Token overlap score: count how many tokens appear in hay
	let overlap = 0;
	for (const t of tokens) {
		if (hay.includes(t)) overlap += 1;
	}

	// Tag boost: if any query token matches a tag category, give extra weight
	let tagBoost = 0;
	if (opportunity.tags && Array.isArray(opportunity.tags.categories)) {
		for (const cat of opportunity.tags.categories) {
			for (const t of tokens) if (cat.toLowerCase().includes(t)) tagBoost += 1;
		}
	}

	// Recency boost: if last_updated.date exists, compute days since update and prefer recent
	let recencyBoost = 0;
	if (opportunity.last_updated && opportunity.last_updated.date) {
		const days = (Date.now() - new Date(opportunity.last_updated.date).getTime()) / (1000 * 60 * 60 * 24);
		recencyBoost = Math.max(0, 10 - days / 30); // small boost for items updated within months
	}

	// Combine scores into a single numeric score
	return overlap * 10 + tagBoost * 5 + recencyBoost;
}

// GET /api/semantic-search/:searchQuery
// Route param: searchQuery (natural-language query)
// Optional query param: ?limit=n
// Returns: top-matching opportunities according to a simple semantic score.
app.get('/api/semantic-search/:searchQuery', async (req, res) => {
	// Extract the searchQuery from the route params and optional limit from query string
	const query = req.params.searchQuery;
	const limit = req.query.limit ? Number(req.query.limit) : 10;

	// Validate input
	if (!query || typeof query !== 'string') return res.status(400).json({ error: 'Missing or invalid searchQuery in URL' });

	// Fetch candidate documents from DB (pull a reasonable number and rank in-app)
	const candidates = await Opportunity.find().limit(500).exec();

	// Score each candidate using the processor function and the provided query
	const scored = candidates.map(doc => ({ score: scoreOpportunity(doc.toObject(), query), doc }));

	// Sort by score descending and return the top `limit` results
	scored.sort((a, b) => b.score - a.score);
	const out = scored.slice(0, limit && Number(limit) > 0 ? Number(limit) : 10).map(s => ({ score: s.score, opportunity: s.doc }));

	// Respond with the ranked results
	return res.json({ query, results: out });
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
