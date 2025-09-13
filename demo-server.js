// Demo server for LinkUp! - works without MongoDB
const express = require('express');
const path = require('path');
const { spawn } = require('child_process');

const app = express();

// Use JSON body parsing middleware
app.use(express.json());

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

// Helper: vector-based semantic search using OpenAI embeddings
async function vectorSearch(query, limit = 10, minResults = 3, threshold = 0.75) {
    return new Promise((resolve, reject) => {
        // Call our Python vector search script
        const pythonScript = path.join(__dirname, 'vector_search.py');
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
        
        
        // Format results to match expected API response with real similarity scores
        const results = vectorResults.map((result, index) => {
            // Extract the opportunity data without the embedding array
            const opportunity = result.opportunity || result;
            const cleanOpportunity = {
                activity_name: opportunity.activity_name,
                organization_name: opportunity.organization_name,
                activity_description: opportunity.activity_description,
                program_description: opportunity.program_description,
                location: opportunity.location,
                age_range: opportunity.age_range,
                dates: opportunity.dates,
                schedule: opportunity.schedule,
                cost: opportunity.cost,
                url: opportunity.url,
                tags: opportunity.tags,
                last_updated: opportunity.last_updated
            };
            
            return {
                score: result.similarity || (0.9 - index * 0.05), // Use real similarity score or fallback
                opportunity: cleanOpportunity
            };
        });

        // Return the results as JSON
        res.json(results);
    } catch (error) {
        console.error('Semantic search error:', error);
        res.status(500).json({ 
            error: 'Internal server error during semantic search',
            details: error.message 
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        message: 'LinkUp! Demo server is running',
        timestamp: new Date().toISOString()
    });
});

// Start the server
const port = process.env.PORT || 3000;
const host = process.env.HOST || '0.0.0.0';
app.listen(port, host, () => {
    console.log(`🔗 LinkUp! Demo server listening on ${host}:${port}`);
    console.log(`📱 Server is ready for connections`);
    console.log(`🔍 Vector search powered by OpenAI embeddings`);
});

module.exports = app;
