// Import the mongoose library to define schemas and interact with MongoDB
const mongoose = require('mongoose');

// Create a shorthand for mongoose.Schema to keep definitions concise
const { Schema } = mongoose;

// Define a schema that mirrors the provided opportunity_schema structure
// Each line is commented to explain the purpose and type expectation
const OpportunitySchema = new Schema({
  // Name of the organization offering the program
  organization_name: { type: String, required: true },
  // Short description of the program
  program_description: { type: String },
  // Name of the specific activity or program
  activity_name: { type: String },
  // Full description of the activity
  activity_description: { type: String },
  // Nested location object to store name, address, and optional geo data
  location: {
    name: { type: String },
    address: { type: String },
    // GeoJSON point for coordinates; optional but helpful for location queries
    coordinates: {
      type: { type: String, enum: ['Point'], default: 'Point' },
      coordinates: { type: [Number], index: '2dsphere' }
    }
  },
  // Age range string for simple filtering
  age_range: { type: String },
  // Dates object with ISO date strings
  dates: {
    start_date: { type: Date },
    end_date: { type: Date }
  },
  // Schedule information with days array and times string
  schedule: {
    days: { type: [String] },
    times: { type: String }
  },
  // Cost to participate as a string to preserve units like "$"
  cost: { type: String },
  // URL for more info
  url: { type: String },
  // Tags grouped into categories, demographics, accessibility, and program_type
  tags: {
    categories: { type: [String] },
    demographics: { type: [String] },
    accessibility: { type: [String] },
    program_type: { type: [String] }
  },
  // Last updated metadata to track source and refresh date
  last_updated: {
    date: { type: Date },
    source_url: { type: String }
  }
}, { timestamps: true }); // Add createdAt and updatedAt fields automatically

// Export the model so it can be used elsewhere in the application
module.exports = mongoose.model('Opportunity', OpportunitySchema);
