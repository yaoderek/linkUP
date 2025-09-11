# LinkUp! - Youth Opportunity Connector

A semantic search platform that connects Seattle's youth with amazing opportunities using AI-powered vector search.

## 🚀 Quick Start

### Demo Server (No MongoDB Required)

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# Start the demo server
node demo-server.js
```

Then open http://localhost:3000 in your browser!

### Environment Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Get your OpenAI API key:**
   - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key

3. **Update your `.env` file:**
   ```bash
   OPENAI_API_KEY=your_actual_api_key_here
   PORT=3000
   ```

**⚠️ Important:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

## ✨ Features

- **🔍 Semantic Search**: AI-powered search using OpenAI embeddings
- **🎯 Smart Matching**: Dynamic threshold ensures quality results
- **📱 Responsive Design**: Works on desktop and mobile
- **♿ Accessible**: Built with accessibility in mind
- **🎨 Modern UI**: Clean, friendly interface with light theme

## 🏗️ Architecture

### Frontend
- **HTML/CSS/JavaScript**: Vanilla web technologies
- **Responsive Design**: Mobile-first approach
- **Accessibility**: WCAG compliant with keyboard navigation

### Backend
- **Express.js**: RESTful API server
- **Vector Search**: Python script with OpenAI embeddings
- **Dynamic Thresholding**: Ensures minimum results with quality control

### Data
- **2,228 Opportunities**: Seattle Parks & Recreation activities
- **AI Embeddings**: 1536-dimensional vectors for semantic search
- **Rich Metadata**: Age ranges, costs, dates, categories, locations

## 🔧 API Endpoints

### Search
```
GET /api/semantic-search/:query?limit=10
```

### Health Check
```
GET /api/health
```

## 🎯 Search Examples

Try these queries in the search bar:
- "art classes for kids"
- "swimming lessons"
- "music lessons"
- "sports activities"
- "free programs for families"

## 🛠️ Development

### Full Server (Requires MongoDB)
```bash
# Start MongoDB
brew services start mongodb-community

# Start the full server
npm start
```

### Vector Search Testing
```bash
# Test vector search directly
python3 vector_search.py --query "art classes for kids" --limit 5
```

## 📊 Data Sources

- **Seattle Parks & Recreation**: 2,228 youth opportunities
- **Categories**: Arts, Sports, Music, Dance, STEM, and more
- **Age Ranges**: Toddlers to teens
- **Locations**: Community centers across Seattle

## 🎨 Design Features

- **LinkUp! Branding**: Green "Link" + Black "Up" + Map pin icon
- **Event Cards**: Match score, description, cost, age range, dates
- **Search Suggestions**: Quick-start tags for common queries
- **Loading States**: Smooth user experience with spinners
- **Error Handling**: Graceful fallbacks and user feedback

## 🔮 Future Enhancements

- User accounts and favorites
- Advanced filtering (location, age, cost)
- Calendar integration
- Push notifications for new opportunities
- Multi-language support

---

Built with ❤️ for Seattle's youth community