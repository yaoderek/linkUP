import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Any

class Events12SeattleParser:
    def __init__(self):
        self.base_url = "https://www.events12.com/seattle/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_page_content(self, url: str = None) -> BeautifulSoup:
        """Fetch page content and return BeautifulSoup object"""
        if url is None:
            url = self.base_url
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_date_text(self, date_text: str) -> Dict[str, str]:
        """Parse date text into structured format"""
        dates = {"start_date": "", "end_date": ""}
        
        if not date_text:
            return dates
        
        try:
            # Handle various date formats from Events12
            # Examples: "August 2, 2025", "August 2 - 3, 2025", "August 2 - Sept. 1, 2025"
            
            # Extract year first
            year_match = re.search(r'\b(20\d{2})\b', date_text)
            year = year_match.group(1) if year_match else "2025"
            
            # Clean up the date text
            date_clean = re.sub(r'\([^)]*\)', '', date_text)  # Remove parentheses content
            date_clean = re.sub(r'\s+', ' ', date_clean).strip()
            
            # Pattern for single date: "August 2, 2025"
            single_date = re.search(r'([A-Za-z]+\.?)\s+(\d{1,2}),?\s*(\d{4})', date_clean)
            if single_date:
                month, day, year = single_date.groups()
                parsed_date = self.normalize_date(f"{month} {day}, {year}")
                dates["start_date"] = parsed_date
                dates["end_date"] = parsed_date
                return dates
            
            # Pattern for date range within same month: "August 2 - 3, 2025"
            same_month_range = re.search(r'([A-Za-z]+\.?)\s+(\d{1,2})\s*-\s*(\d{1,2}),?\s*(\d{4})', date_clean)
            if same_month_range:
                month, start_day, end_day, year = same_month_range.groups()
                dates["start_date"] = self.normalize_date(f"{month} {start_day}, {year}")
                dates["end_date"] = self.normalize_date(f"{month} {end_day}, {year}")
                return dates
            
            # Pattern for cross-month range: "August 2 - Sept. 1, 2025"
            cross_month = re.search(r'([A-Za-z]+\.?)\s+(\d{1,2})\s*-\s*([A-Za-z]+\.?)\s+(\d{1,2}),?\s*(\d{4})', date_clean)
            if cross_month:
                start_month, start_day, end_month, end_day, year = cross_month.groups()
                dates["start_date"] = self.normalize_date(f"{start_month} {start_day}, {year}")
                dates["end_date"] = self.normalize_date(f"{end_month} {end_day}, {year}")
                return dates
            
        except Exception as e:
            print(f"Error parsing date '{date_text}': {e}")
        
        return dates

    def normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        try:
            # Handle month abbreviations
            month_abbrevs = {
                'Jan.': 'January', 'Feb.': 'February', 'Mar.': 'March', 'Apr.': 'April',
                'May.': 'May', 'Jun.': 'June', 'Jul.': 'July', 'Aug.': 'August',
                'Sep.': 'September', 'Sept.': 'September', 'Oct.': 'October', 
                'Nov.': 'November', 'Dec.': 'December'
            }
            
            for abbrev, full in month_abbrevs.items():
                date_str = date_str.replace(abbrev, full)
            
            # Try different date formats
            formats = ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return ""
        except:
            return ""

    def parse_location_and_neighborhood(self, location_text: str) -> Dict[str, Any]:
        """Parse location text into structured format"""
        location = {
            "name": "",
            "address": "",
            "coordinates": {
                "type": "Point",
                "coordinates": [-122.3321, 47.6062]  # Default Seattle coordinates
            }
        }
        
        if not location_text:
            return location
        
        # Events12 format often has: "Neighborhood (distance)" followed by venue and address
        # Example: "Downtown (0.3 miles S)\nSeattle Chamber Music Society at Benaroya Hall, 200 University St."
        
        try:
            lines = location_text.strip().split('\n')
            
            # First line is often neighborhood info
            if lines and '(' in lines[0] and 'miles' in lines[0]:
                # Skip neighborhood line, use venue info
                if len(lines) > 1:
                    venue_line = lines[1].strip()
                    location["name"] = venue_line.split(',')[0].strip() if ',' in venue_line else venue_line
                    if ',' in venue_line:
                        location["address"] = venue_line.split(',', 1)[1].strip() + ", Seattle, WA"
                    else:
                        location["address"] = f"{venue_line}, Seattle, WA"
            else:
                # Use the location text as-is
                location["name"] = location_text.split(',')[0].strip() if ',' in location_text else location_text
                if ',' in location_text:
                    location["address"] = location_text.split(',', 1)[1].strip() + ", Seattle, WA"
                else:
                    location["address"] = f"{location_text}, Seattle, WA"
        
        except Exception as e:
            print(f"Error parsing location '{location_text}': {e}")
            location["name"] = location_text
            location["address"] = f"{location_text}, Seattle, WA"
        
        return location

    def parse_time_and_cost(self, text: str) -> tuple:
        """Extract time and cost information from text"""
        time_info = ""
        cost_info = ""
        
        try:
            # Extract time patterns
            time_patterns = [
                r'(\d{1,2}:\d{2}\s*[ap]\.?m\.?)',
                r'(\d{1,2}\s*[ap]\.?m\.?)',
                r'(\d{1,2}:\d{2}\s*[AP]\.?M\.?)',
                r'(\d{1,2}\s*[AP]\.?M\.?)'
            ]
            
            times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                times.extend(matches)
            
            if times:
                if len(times) >= 2:
                    time_info = f"{times[0]} - {times[-1]}"
                else:
                    time_info = times[0]
            
            # Extract cost patterns
            cost_patterns = [
                r'\$(\d+(?:\.\d{2})?)',
                r'(\$\d+)',
                r'(free)',
                r'(sold out)',
                r'(admission[:\s]*\$?\d*)',
                r'(no charge)',
                r'(complimentary)'
            ]
            
            for pattern in cost_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    cost_info = match.group(0)
                    break
            
            # Default to free if no cost found and contains "free" keywords
            if not cost_info and any(word in text.lower() for word in ['free', 'no charge', 'complimentary']):
                cost_info = "Free"
        
        except Exception as e:
            print(f"Error parsing time/cost from '{text}': {e}")
        
        return time_info, cost_info

    def generate_tags_from_content(self, event_text: str, title: str) -> Dict[str, List[str]]:
        """Generate tags based on event content"""
        tags = {
            "categories": [],
            "demographics": [],
            "accessibility": [],
            "program_type": []
        }
        
        # Combine all text for analysis
        full_text = (title + " " + event_text).lower()
        
        # Categories
        category_mapping = {
            'music': ['concert', 'music', 'band', 'symphony', 'jazz', 'blues', 'rock', 'festival'],
            'arts': ['art', 'gallery', 'exhibit', 'artist', 'painting', 'sculpture', 'craft'],
            'theater': ['theater', 'theatre', 'play', 'performance', 'show', 'drama'],
            'sports': ['sports', 'game', 'race', 'run', 'marathon', 'competition'],
            'food': ['food', 'restaurant', 'taste', 'wine', 'beer', 'dining', 'culinary'],
            'festival': ['festival', 'fest', 'celebration', 'fair', 'carnival'],
            'outdoor': ['park', 'outdoor', 'hiking', 'garden', 'nature', 'beach'],
            'family': ['family', 'kids', 'children', 'child'],
            'nightlife': ['bar', 'club', 'nightlife', 'party', 'cocktail'],
            'education': ['class', 'workshop', 'lesson', 'learn', 'educational'],
            'community': ['community', 'neighborhood', 'local', 'volunteer']
        }
        
        for category, keywords in category_mapping.items():
            if any(keyword in full_text for keyword in keywords):
                tags["categories"].append(category)
        
        # Demographics
        if any(word in full_text for word in ['kids', 'children', 'family', 'child']):
            tags["demographics"].append('family')
        if any(word in full_text for word in ['adult', '21+', 'age 21']):
            tags["demographics"].append('adult')
        if any(word in full_text for word in ['senior', 'elder']):
            tags["demographics"].append('senior')
        
        # Program type
        if any(word in full_text for word in ['free', 'no charge', 'complimentary']):
            tags["program_type"].append('free')
        if '$' in full_text or 'ticket' in full_text:
            tags["program_type"].append('ticketed')
        if any(word in full_text for word in ['festival', 'fair', 'celebration']):
            tags["program_type"].append('festival')
        if any(word in full_text for word in ['outdoor', 'park']):
            tags["program_type"].append('outdoor')
        
        return tags

    def parse_event_text(self, event_text: str) -> Dict[str, Any]:
        """Parse individual event text block into structured data"""
        lines = event_text.strip().split('\n')
        
        # Initialize event structure
        event = {
            "organization_name": "Events12 Seattle",
            "program_description": "",
            "activity_name": "",
            "activity_description": "",
            "location": {
                "name": "",
                "address": "",
                "coordinates": {
                    "type": "Point",
                    "coordinates": [-122.3321, 47.6062]
                }
            },
            "age_range": "",
            "dates": {
                "start_date": "",
                "end_date": ""
            },
            "schedule": {
                "days": [],
                "times": ""
            },
            "cost": "",
            "url": self.base_url,
            "tags": {
                "categories": [],
                "demographics": [],
                "accessibility": [],
                "program_type": []
            },
            "last_updated": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source_url": self.base_url
            }
        }
        
        try:
            # First line is usually the date
            if lines:
                date_line = lines[0]
                event["dates"] = self.parse_date_text(date_line)
            
            # Second line is often location/neighborhood
            if len(lines) > 1:
                location_line = lines[1]
                event["location"] = self.parse_location_and_neighborhood(location_line)
            
            # Find the main event description (usually the longest line or contains event name)
            description_lines = []
            title_found = False
            
            for i, line in enumerate(lines[2:], 2):  # Skip date and location lines
                if line.strip():
                    # Look for event title (often contains brackets or starts with description)
                    if '[' in line and ']' in line and not title_found:
                        # Extract title from brackets
                        title_match = re.search(r'\[([^\]]+)\]', line)
                        if title_match:
                            event["activity_name"] = title_match.group(1)
                            title_found = True
                    
                    # Add to description
                    description_lines.append(line.strip())
            
            # If no bracketed title found, use first substantial line as title
            if not event["activity_name"] and description_lines:
                # Look for a substantial first line as title
                first_line = description_lines[0]
                if len(first_line) > 10 and len(first_line) < 100:
                    event["activity_name"] = first_line.split('.')[0]  # Take first sentence
            
            # Combine all description lines
            full_description = " ".join(description_lines)
            event["activity_description"] = full_description
            event["program_description"] = full_description
            
            # Extract time and cost from description
            time_info, cost_info = self.parse_time_and_cost(full_description)
            event["schedule"]["times"] = time_info
            event["cost"] = cost_info or "Contact for pricing"
            
            # Extract age information
            age_patterns = [
                r'age (\d+)[+\s]',
                r'(\d+)[+\s]',
                r'children age (\d+)',
                r'for age (\d+)'
            ]
            
            for pattern in age_patterns:
                match = re.search(pattern, full_description, re.IGNORECASE)
                if match:
                    age = match.group(1)
                    event["age_range"] = f"{age}+"
                    break
            
            # Generate tags
            event["tags"] = self.generate_tags_from_content(full_description, event["activity_name"])
            
        except Exception as e:
            print(f"Error parsing event text: {e}")
        
        return event

    def parse_events_from_html(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse events from the HTML content"""
        events = []
        
        try:
            # The Events12 page has event content in text blocks
            # We need to find patterns that separate individual events
            
            # Get all text content
            page_text = soup.get_text()
            
            # Split by date patterns to separate events
            # Events typically start with a date like "August 2, 2025"
            date_pattern = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\.?\s+\d{1,2}(?:\s*-\s*\d{1,2})?,?\s+\d{4})'
            
            # Split the text by date patterns
            event_blocks = re.split(date_pattern, page_text)
            
            # Process pairs of (date, content)
            for i in range(1, len(event_blocks), 2):
                if i + 1 < len(event_blocks):
                    date_text = event_blocks[i].strip()
                    content_text = event_blocks[i + 1].strip()
                    
                    # Combine date and content
                    full_event_text = f"{date_text}\n{content_text}"
                    
                    # Skip very short content (likely not real events)
                    if len(content_text) > 50:
                        event = self.parse_event_text(full_event_text)
                        if event["activity_name"]:  # Only add if we found a name
                            events.append(event)
            
            print(f"Parsed {len(events)} events from HTML")
            
        except Exception as e:
            print(f"Error parsing events from HTML: {e}")
        
        return events

    def scrape_events(self) -> List[Dict[str, Any]]:
        """Main method to scrape events from Events12 Seattle page"""
        print(f"Scraping events from: {self.base_url}")
        
        soup = self.fetch_page_content()
        if not soup:
            print("Failed to fetch page content")
            return []
        
        events = self.parse_events_from_html(soup)
        
        # Clean and validate events
        valid_events = []
        for event in events:
            if event["activity_name"] and len(event["activity_name"]) > 3:
                valid_events.append(event)
        
        print(f"Found {len(valid_events)} valid events")
        return valid_events

    def save_events_to_json(self, events: List[Dict[str, Any]], filename: str = "events12_seattle_events.json"):
        """Save events to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(events)} events to {filename}")

def main():
    """Main execution function"""
    parser = Events12SeattleParser()
    
    try:
        # Scrape events
        events = parser.scrape_events()
        
        if events:
            # Save to JSON
            parser.save_events_to_json(events)
            
            # Print summary
            print(f"\nScraping completed successfully!")
            print(f"Total events: {len(events)}")
            
            # Show categories found
            all_categories = set()
            for event in events:
                all_categories.update(event['tags']['categories'])
            print(f"Categories found: {sorted(list(all_categories))}")
            
            # Show sample event
            if events:
                print(f"\nSample event (first):")
                sample = events[0]
                print(f"Name: {sample['activity_name']}")
                print(f"Date: {sample['dates']['start_date']} to {sample['dates']['end_date']}")
                print(f"Location: {sample['location']['name']}")
                print(f"Cost: {sample['cost']}")
                print(f"Categories: {', '.join(sample['tags']['categories'])}")
        
        else:
            print("No events found. The parsing may need adjustment for the current page structure.")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()