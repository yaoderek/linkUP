// LinkUp! Frontend JavaScript
class LinkUpApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentQuery = '';
        this.isLoading = false;
        
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.searchButton = document.getElementById('searchButton');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.noResults = document.getElementById('noResults');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.suggestionTags = document.querySelectorAll('.suggestion-tag');
    }

    attachEventListeners() {
        // Search button click
        this.searchButton.addEventListener('click', () => this.performSearch());
        
        // Enter key in search input
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
        
        // Suggestion tag clicks
        this.suggestionTags.forEach(tag => {
            tag.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                this.searchInput.value = query;
                this.performSearch();
            });
        });
        
        // Real-time search as user types (with debounce)
        let searchTimeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (e.target.value.trim().length > 2) {
                    this.performSearch();
                } else if (e.target.value.trim().length === 0) {
                    this.clearResults();
                }
            }, 500);
        });
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.clearResults();
            return;
        }

        if (this.isLoading) return;
        
        this.currentQuery = query;
        this.showLoading();
        
        try {
            const results = await this.searchOpportunities(query);
            this.displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Sorry, there was an error searching for opportunities. Please try again.');
        }
    }

    async searchOpportunities(query) {
        const response = await fetch(`${this.apiBaseUrl}/semantic-search/${encodeURIComponent(query)}?limit=12`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    showLoading() {
        this.isLoading = true;
        this.loadingIndicator.classList.remove('hidden');
        this.noResults.classList.add('hidden');
        this.resultsContainer.innerHTML = '';
    }

    hideLoading() {
        this.isLoading = false;
        this.loadingIndicator.classList.add('hidden');
    }

    displayResults(results) {
        this.hideLoading();
        
        if (!results || results.length === 0) {
            this.showNoResults();
            return;
        }

        this.resultsContainer.innerHTML = results.map(result => this.createEventCard(result)).join('');
        this.noResults.classList.add('hidden');
    }

    createEventCard(opportunity) {
        const score = this.calculateMatchScore(opportunity.score);
        const cost = this.formatCost(opportunity.opportunity.cost);
        const ageRange = opportunity.opportunity.age_range || 'All ages';
        const dates = this.formatDates(opportunity.opportunity.dates);
        const categories = opportunity.opportunity.tags?.categories || [];
        
        return `
            <div class="event-card" role="article" aria-label="${opportunity.opportunity.activity_name}">
                <div class="match-score" aria-label="Match score: ${score}%">
                    ${score}% match
                </div>
                
                <h3 class="event-title">${this.escapeHtml(opportunity.opportunity.activity_name)}</h3>
                <p class="event-organization">${this.escapeHtml(opportunity.opportunity.organization_name)}</p>
                
                <p class="event-description">
                    ${this.escapeHtml(opportunity.opportunity.activity_description || opportunity.opportunity.program_description || 'No description available.')}
                </p>
                
                <div class="event-details">
                    <div class="event-detail">
                        <svg class="event-detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                        </svg>
                        <span class="event-cost">${cost}</span>
                    </div>
                    
                    <div class="event-detail">
                        <svg class="event-detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12,6 12,12 16,14"/>
                        </svg>
                        <span class="event-age">${ageRange}</span>
                    </div>
                    
                    <div class="event-detail">
                        <svg class="event-detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        <span class="event-date">${dates}</span>
                    </div>
                    
                    <div class="event-detail">
                        <svg class="event-detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                        <span>${this.escapeHtml(opportunity.opportunity.location?.name || 'Location TBD')}</span>
                    </div>
                </div>
                
                ${categories.length > 0 ? `
                    <div class="event-categories">
                        ${categories.map(category => `
                            <span class="category-tag">${this.escapeHtml(category)}</span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    calculateMatchScore(score) {
        // Convert the cosine similarity score to a percentage with one decimal place
        return ((score || 0.8) * 100).toFixed(1);
    }

    formatCost(cost) {
        if (!cost || cost === '0' || cost === '$0' || cost.toLowerCase().includes('free')) {
            return 'Free';
        }
        
        // If it's already formatted as currency, return as is
        if (typeof cost === 'string' && cost.includes('$')) {
            return cost;
        }
        
        // Otherwise, format as currency
        const numCost = parseFloat(cost);
        if (isNaN(numCost)) {
            return 'Contact for pricing';
        }
        
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(numCost);
    }

    formatDates(dates) {
        if (!dates) return 'Ongoing';
        
        const startDate = dates.start_date;
        const endDate = dates.end_date;
        
        if (!startDate) return 'Ongoing';
        
        try {
            const start = new Date(startDate);
            const end = endDate ? new Date(endDate) : null;
            
            const formatDate = (date) => {
                return new Intl.DateTimeFormat('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                }).format(date);
            };
            
            if (end && start.getTime() !== end.getTime()) {
                return `${formatDate(start)} - ${formatDate(end)}`;
            } else {
                return formatDate(start);
            }
        } catch (error) {
            return 'Ongoing';
        }
    }

    showNoResults() {
        this.noResults.classList.remove('hidden');
        this.resultsContainer.innerHTML = '';
    }

    showError(message) {
        this.hideLoading();
        this.resultsContainer.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">⚠️</div>
                <h3>Something went wrong</h3>
                <p>${message}</p>
            </div>
        `;
        this.noResults.classList.add('hidden');
    }

    clearResults() {
        this.resultsContainer.innerHTML = '';
        this.noResults.classList.add('hidden');
        this.loadingIndicator.classList.add('hidden');
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LinkUpApp();
});

// Add some helpful console logging for development
console.log('🔗 LinkUp! Frontend loaded successfully');
console.log('Search for youth opportunities in Seattle!');
