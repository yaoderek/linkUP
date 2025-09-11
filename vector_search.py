#!/usr/bin/env python3
"""
Vector search for RAG queries on Seattle parks opportunities.
Given a query, finds the most similar opportunities using cosine similarity.
"""

import json
import numpy as np
from openai import OpenAI
from typing import List, Dict, Any, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for a search query."""
    try:
        response = client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return []

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    
    # Calculate cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0
    
    return dot_product / (norm_a * norm_b)

def load_opportunities_with_embeddings(file_path: str, verbose: bool = True) -> List[Dict[str, Any]]:
    """Load opportunities with their embeddings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            opportunities = json.load(f)
        if verbose:
            print(f"✅ Loaded {len(opportunities)} opportunities with embeddings")
        return opportunities
    except Exception as e:
        if verbose:
            print(f"❌ Error loading opportunities: {e}")
        return []

def search_opportunities(query: str, opportunities: List[Dict[str, Any]], top_k: int = 10, min_results: int = 3, threshold: float = 0.75, verbose: bool = True) -> List[Tuple[Dict[str, Any], float]]:
    """
    Search for opportunities using vector similarity with dynamic threshold.
    
    Args:
        query: Search query string
        opportunities: List of opportunities with embeddings
        top_k: Maximum number of results to return
        min_results: Minimum number of results to return (even if below threshold)
        threshold: Minimum similarity score (0.0 to 1.0)
        verbose: Whether to print debug messages
    
    Returns:
        List of tuples (opportunity, similarity_score) sorted by similarity
    """
    if verbose:
        print(f"🔍 Searching for: '{query}'")
    
    # Generate embedding for the query
    query_embedding = generate_query_embedding(query)
    if not query_embedding:
        if verbose:
            print("❌ Failed to generate query embedding")
        return []
    
    if verbose:
        print(f"✅ Generated query embedding (dimension: {len(query_embedding)})")
    
    # Calculate similarities
    similarities = []
    for opportunity in opportunities:
        if 'embedding' in opportunity and opportunity['embedding']:
            similarity = cosine_similarity(query_embedding, opportunity['embedding'])
            similarities.append((opportunity, similarity))
        else:
            if verbose:
                print(f"⚠️  Opportunity missing embedding: {opportunity.get('activity_name', 'Unknown')}")
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Apply dynamic threshold logic
    # First, get all results above threshold
    above_threshold = [(opp, sim) for opp, sim in similarities if sim >= threshold]
    
    # If we have enough results above threshold, use them (up to top_k)
    if len(above_threshold) >= min_results:
        results = above_threshold[:top_k]
        if verbose:
            print(f"🎯 Found {len(results)} results above threshold {threshold:.2f}")
    else:
        # If not enough above threshold, take top min_results regardless of threshold
        results = similarities[:max(min_results, len(above_threshold))]
        if verbose:
            print(f"🎯 Found {len(results)} results (threshold {threshold:.2f} too restrictive, showing top {len(results)})")
    
    # Show similarity range for debugging
    if results and verbose:
        min_sim = min(sim for _, sim in results)
        max_sim = max(sim for _, sim in results)
        print(f"📊 Similarity range: {min_sim:.3f} - {max_sim:.3f}")
    
    return results

def format_search_result(opportunity: Dict[str, Any], similarity: float, rank: int) -> str:
    """Format a search result for display."""
    return f"""
{rank}. {opportunity.get('activity_name', 'Unknown')} (Similarity: {similarity:.3f})
   📍 Location: {opportunity.get('location', {}).get('name', 'N/A')}
   👥 Age Range: {opportunity.get('age_range', 'N/A')}
   💰 Cost: {opportunity.get('cost', 'N/A')}
   📅 Schedule: {', '.join(opportunity.get('schedule', {}).get('days', []))} {opportunity.get('schedule', {}).get('times', '')}
   🏷️  Categories: {', '.join(opportunity.get('tags', {}).get('categories', []))}
   📝 Description: {opportunity.get('activity_description', 'N/A')[:200]}...
   🔗 URL: {opportunity.get('url', 'N/A')}
"""

def interactive_search():
    """Interactive search interface."""
    # Load opportunities
    file_path = "/Users/yaoderek/Documents/vscode/youthconnectorhack/data/agent_outputs/seattle_parks_opportunities_with_embeddings.json"
    opportunities = load_opportunities_with_embeddings(file_path)
    
    if not opportunities:
        print("❌ No opportunities loaded. Exiting.")
        return
    
    print(f"\n🚀 Vector Search Ready! Loaded {len(opportunities)} opportunities.")
    print("💡 Try queries like:")
    print("   - 'art classes for kids'")
    print("   - 'swimming lessons for adults'")
    print("   - 'free programs for teenagers'")
    print("   - 'piano lessons in Ballard'")
    print("   - 'STEM activities for ages 8-12'")
    print("\nType 'quit' to exit.\n")
    
    while True:
        query = input("🔍 Enter your search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            print("❌ Please enter a search query.")
            continue
        
        # Search for opportunities
        results = search_opportunities(query, opportunities, top_k=5, min_results=3, threshold=0.75)
        
        if not results:
            print("❌ No results found.")
            continue
        
        # Display results
        print(f"\n🎯 Top {len(results)} results for '{query}':")
        print("=" * 80)
        
        for i, (opportunity, similarity) in enumerate(results, 1):
            print(format_search_result(opportunity, similarity, i))
        
        print("=" * 80)

def search_function(query: str, top_k: int = 10, min_results: int = 3, threshold: float = 0.75, verbose: bool = True) -> List[Dict[str, Any]]:
    """
    Function to be used by other scripts for vector search.
    
    Args:
        query: Search query string
        top_k: Maximum number of results to return
        min_results: Minimum number of results to return (even if below threshold)
        threshold: Minimum similarity score (0.0 to 1.0)
        verbose: Whether to print debug messages
    
    Returns:
        List of opportunity dictionaries sorted by similarity
    """
    file_path = "/Users/yaoderek/Documents/vscode/youthconnectorhack/data/agent_outputs/seattle_parks_opportunities_with_embeddings.json"
    opportunities = load_opportunities_with_embeddings(file_path, verbose)
    
    if not opportunities:
        return []
    
    results = search_opportunities(query, opportunities, top_k, min_results, threshold, verbose)
    return [opportunity for opportunity, similarity in results]

if __name__ == "__main__":
    import sys
    
    # Check if command line arguments are provided (for Express.js integration)
    if len(sys.argv) > 1:
        # Parse command line arguments
        query = None
        limit = 10
        min_results = 3
        threshold = 0.75
        
        i = 1
        while i < len(sys.argv):
            if sys.argv[i] == '--query' and i + 1 < len(sys.argv):
                query = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--limit' and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--min_results' and i + 1 < len(sys.argv):
                min_results = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--threshold' and i + 1 < len(sys.argv):
                threshold = float(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        if query:
            # Run search and output JSON for Express.js (non-verbose mode)
            # Get the raw results with similarity scores
            file_path = "/Users/yaoderek/Documents/vscode/youthconnectorhack/data/agent_outputs/seattle_parks_opportunities_with_embeddings.json"
            opportunities = load_opportunities_with_embeddings(file_path, verbose=False)
            
            if opportunities:
                search_results = search_opportunities(query, opportunities, limit, min_results, threshold, verbose=False)
                # Format for API: include both opportunity and similarity score
                formatted_results = []
                for opportunity, similarity in search_results:
                    formatted_results.append({
                        "opportunity": opportunity,
                        "similarity": similarity
                    })
                print(json.dumps(formatted_results))
            else:
                print(json.dumps([]))
        else:
            print("Usage: python3 vector_search.py --query 'search term' [--limit 10] [--min_results 3] [--threshold 0.75]")
            sys.exit(1)
    else:
        # Run interactive search
        interactive_search()
