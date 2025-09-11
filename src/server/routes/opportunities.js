// Import express to create a router for opportunity-related endpoints
const express = require('express');
// Create a router instance to attach route handlers
const router = express.Router();
// Import the Opportunity model to query MongoDB
const Opportunity = require('../models/opportunity');

// Helper: document the shape and behavior of the search functions
/**
 * Search functions exposed by this router:
 * - GET /opportunities                : list all opportunities (with optional limit)
 * - GET /opportunities/search        : text search across organization, activity, and description
 * - GET /opportunities/by-org        : filter by organization_name
 * - GET /opportunities/by-category   : filter by tag category
 * - GET /opportunities/by-location   : filter by location name or address
 * - GET /opportunities/by-age        : filter by age_range (exact match)
 */

// Route: list opportunities with optional ?limit=n query
router.get('/', async (req, res) => {
  // Parse optional limit parameter from query string
  const limit = parseInt(req.query.limit, 10) || 50; // default to 50 results
  // Query MongoDB for documents, limiting results and sorting by creation time
  const docs = await Opportunity.find().sort({ createdAt: -1 }).limit(limit).exec();
  // Return the documents as JSON
  return res.json(docs);
});

// Route: text search across name and description fields using a case-insensitive regex
router.get('/search', async (req, res) => {
  // Extract q param for the search term
  const q = req.query.q;
  // If no query provided, return bad request
  if (!q) return res.status(400).json({ error: 'Missing query param q' });
  // Build a case-insensitive regex from the query string
  const re = new RegExp(q, 'i');
  // Search across several fields for convenience
  const docs = await Opportunity.find({
    $or: [
      { organization_name: re },
      { activity_name: re },
      { activity_description: re },
      { program_description: re }
    ]
  }).exec();
  // Return matching documents
  return res.json(docs);
});

// Route: filter by organization name exact match (or partial via q)
router.get('/by-org', async (req, res) => {
  // Accept either org (exact) or q (partial)
  const org = req.query.org;
  const q = req.query.q;
  // Build query object accordingly
  const query = org ? { organization_name: org } : (q ? { organization_name: new RegExp(q, 'i') } : {});
  // Execute query and return results
  const docs = await Opportunity.find(query).exec();
  return res.json(docs);
});

// Route: filter by category tag (exact match within tags.categories array)
router.get('/by-category', async (req, res) => {
  // Expect category parameter
  const category = req.query.category;
  if (!category) return res.status(400).json({ error: 'Missing category param' });
  // Find documents where tags.categories contains the given category (case-insensitive)
  const docs = await Opportunity.find({ 'tags.categories': new RegExp(`^${category}$`, 'i') }).exec();
  return res.json(docs);
});

// Route: filter by location name or address
router.get('/by-location', async (req, res) => {
  // Accept q for partial match against location.name or location.address
  const q = req.query.q;
  if (!q) return res.status(400).json({ error: 'Missing q param' });
  const re = new RegExp(q, 'i');
  const docs = await Opportunity.find({ $or: [{ 'location.name': re }, { 'location.address': re }] }).exec();
  return res.json(docs);
});

// Route: filter by age_range exact or partial match
router.get('/by-age', async (req, res) => {
  // Accept age param or q for partial
  const age = req.query.age;
  const q = req.query.q;
  if (!age && !q) return res.status(400).json({ error: 'Missing age or q param' });
  const query = age ? { age_range: age } : { age_range: new RegExp(q, 'i') };
  const docs = await Opportunity.find(query).exec();
  return res.json(docs);
});

// Export the router to be mounted by the main app
module.exports = router;
