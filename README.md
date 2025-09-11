# LinkUp Backend

This backend imports sample opportunity data into a local MongoDB database called `LinkUp` and exposes simple search APIs.

Quick steps (Windows cmd.exe):

1. Install dependencies:

   npm install

2. Seed the database with sample entries:

   npm run seed

3. Start the server:

   npm start

API endpoints:

- GET /api/opportunities                : list opportunities (optional ?limit=n)
- GET /api/opportunities/search?q=term  : text search
- GET /api/opportunities/by-org?org=Name : filter by organization
- GET /api/opportunities/by-category?category=Arts : filter by category
- GET /api/opportunities/by-location?q=Jefferson : filter by location
- GET /api/opportunities/by-age?age=8-12 years : filter by age_range

Note: MongoDB must be running locally on port 27017.
## Youth Connector Catalog Builder Search Engine
AI-powered search engine that finds only the most relevant opportunities, events, social programs, and more for Seattle's youth.