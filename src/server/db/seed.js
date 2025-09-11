// Import filesystem utilities to read the JSON file
const fs = require('fs');
// Import path to construct OS-independent file paths
const path = require('path');
// Import mongoose to connect to MongoDB and use models
const mongoose = require('mongoose');
// Import the Opportunity model that defines the shape of the documents
const Opportunity = require('../models/opportunity');

// Build the absolute path to the sample_entries.json file that ships with the repo.
// We robustly resolve from the project root by navigating up from this file's directory
// (__dirname is .../src/server/db). The file actually lives at data/agent_outputs/schema/sample_entries.json
const samplePath = path.join(__dirname, '..', '..', '..', '..', 'data', 'agent_outputs', 'schema', 'sample_entries.json');

// // If the file isn't present, emit a helpful error with the exact path we tried
// if (!fs.existsSync(samplePath)) {
//   console.error('Seed data file not found at:', samplePath);
//   console.error('Current working directory:', process.cwd());
//   console.error('Please ensure the file exists and the path is correct relative to the project root.');
//   process.exit(1);
// }

// Main async function to run the seeding process
async function main() {
  // Connect to local MongoDB at the LinkUp database
  await mongoose.connect('mongodb://127.0.0.1:27017/LinkUp', { useNewUrlParser: true, useUnifiedTopology: true });

  // Read the sample JSON file from disk synchronously and parse into objects
  const raw = [
  {
    "organization_name": "Seattle Art Center",
    "program_description": "A series of after-school art programs for youth.",
    "activity_name": "Creative Expressions: After-School Arts",
    "activity_description": "Engage in painting, drawing, and mixed media projects to enhance artistic skills and self-expression.",
    "location": {
      "name": "Seattle Art Center",
      "address": "123 Art St, Seattle, WA"
    },
    "age_range": "8-12 years",
    "dates": {
      "start_date": "2025-09-20",
      "end_date": "2026-06-15"
    },
    "schedule": {
      "days": [ "Mondays", "Wednesdays" ],
      "times": "3:30 PM - 5:30 PM"
    },
    "cost": "$150",
    "url": "http://www.seattleartcenter.org/creativeexpressions",
    "tags": {
      "categories": [ "Arts & Crafts", "Music & Performing Arts" ],
      "demographics": [ "Ages 8-12", "All skill levels" ],
      "accessibility": [ "Transportation available", "Wheelchair accessible" ],
      "program_type": [ "After-School Program", "Seasonal" ]
    },
    "last_updated": {
      "date": "2025-09-11",
      "source_url": "http://www.seattleartcenter.org/youth"
    }
  },
  {
    "organization_name": "Seattle Youth Soccer League",
    "program_description": "Local soccer leagues and training for young athletes.",
    "activity_name": "Seattle Youth Soccer League",
    "activity_description": "Join local youth to learn soccer skills, teamwork, and sportsmanship while participating in matches.",
    "location": {
      "name": "Jefferson Park",
      "address": "4500 15th Ave S, Seattle, WA"
    },
    "age_range": "6-14 years",
    "dates": {
      "start_date": "2025-10-01",
      "end_date": "2025-11-30"
    },
    "schedule": {
      "days": [ "Saturdays" ],
      "times": "10:00 AM - 12:00 PM"
    },
    "cost": "$75",
    "url": "http://www.seattleyouthsoccer.org",
    "tags": {
      "categories": [ "Sports & Recreation", "Fitness" ],
      "demographics": [ "Ages 6-14", "Inclusive to all skill levels" ],
      "accessibility": [ "Special accommodations available", "Transportation support" ],
      "program_type": [ "Ongoing", "Registration required" ]
    },
    "last_updated": {
      "date": "2025-09-11",
      "source_url": "http://www.seattleyouthsoccer.org/programs"
    }
  },
  {
    "organization_name": "Seattle Community Center",
    "program_description": "Community-based programs covering a variety of interests.",
    "activity_name": "STEM Explorers Club",
    "activity_description": "Dive into exciting science experiments and technology projects that spark curiosity and innovation.",
    "location": {
      "name": "Seattle Community Center",
      "address": "456 Community Ave, Seattle, WA"
    },
    "age_range": "10-15 years",
    "dates": {
      "start_date": "2025-10-15",
      "end_date": "2026-04-15"
    },
    "schedule": {
      "days": [ "Tuesdays", "Thursdays" ],
      "times": "4:00 PM - 6:00 PM"
    },
    "cost": "$100",
    "url": "http://www.seattlecommunitycenter.org/stemexplorers",
    "tags": {
      "categories": [ "Science & Technology", "Academic & Tutoring" ],
      "demographics": [ "Ages 10-15", "Diverse cultural backgrounds" ],
      "accessibility": [ "Accessible facilities", "Transportation assistance" ],
      "program_type": [ "Ongoing", "Registration required" ]
    },
    "last_updated": {
      "date": "2025-09-11",
      "source_url": "http://www.seattlecommunitycenter.org/stem"
    }
  }
];
  const entries = raw;

  // Iterate over entries and upsert each one based on organization_name + activity_name
  for (const entry of entries) {
    // Build a query that uniquely identifies an opportunity for idempotent insertion
    const query = { organization_name: entry.organization_name, activity_name: entry.activity_name };

    // Prepare an update document that maps fields from the sample to the schema
    const update = {
      $set: {
        program_description: entry.program_description,
        activity_description: entry.activity_description,
        location: entry.location,
        age_range: entry.age_range,
        dates: {
          start_date: entry.dates && entry.dates.start_date ? new Date(entry.dates.start_date) : undefined,
          end_date: entry.dates && entry.dates.end_date ? new Date(entry.dates.end_date) : undefined
        },
        schedule: entry.schedule,
        cost: entry.cost,
        url: entry.url,
        tags: entry.tags,
        last_updated: {
          date: entry.last_updated && entry.last_updated.date ? new Date(entry.last_updated.date) : undefined,
          source_url: entry.last_updated && entry.last_updated.source_url
        }
      }
    };

    // Use findOneAndUpdate with upsert:true to insert if missing, ensuring idempotency
    const res = await Opportunity.findOneAndUpdate(query, update, { upsert: true, new: true, setDefaultsOnInsert: true });
    // Log the result for visibility
    console.log(`Upserted: ${res.organization_name} - ${res.activity_name}`);
  }

  // Close the mongoose connection cleanly
  await mongoose.disconnect();
}

// Execute the main function and surface errors to the console
main().catch(err => {
  console.error('Seeding failed:', err);
  process.exit(1);
});
