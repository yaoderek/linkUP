import pandas as pd
import json
import re
from datetime import datetime
from typing import List, Dict, Any

def parse_age_range(ages_min: int, ages_min_month: int, ages_min_week: int, 
                   ages_max: int, ages_max_month: int, ages_max_week: int) -> str:
    """Parse age range from separate age fields"""
    try:
        # Handle minimum age
        min_age_str = ""
        if pd.notna(ages_min) and ages_min > 0:
            min_age_str = str(int(ages_min))
            if pd.notna(ages_min_month) and ages_min_month > 0:
                min_age_str += f".{int(ages_min_month)}"
        
        # Handle maximum age
        max_age_str = ""
        if pd.notna(ages_max) and ages_max > 0:
            max_age_str = str(int(ages_max))
            if pd.notna(ages_max_month) and ages_max_month > 0:
                max_age_str += f".{int(ages_max_month)}"
        
        # Create age range string
        if min_age_str and max_age_str:
            return f"{min_age_str}-{max_age_str} years"
        elif min_age_str:
            return f"{min_age_str}+ years"
        elif max_age_str:
            return f"Up to {max_age_str} years"
        else:
            return "All ages"
            
    except:
        return "All ages"

def parse_location(activity_location: str) -> Dict[str, Any]:
    """Parse location string into structured location object"""
    location = {
        "name": "",
        "address": "",
        "coordinates": {
            "type": "Point",
            "coordinates": [-122.3321, 47.6062]  # Default Seattle coordinates
        }
    }
    
    if pd.isna(activity_location) or not activity_location:
        return location
    
    # Split on " at " to separate room/facility from building
    if " at " in activity_location:
        parts = activity_location.split(" at ", 1)
        room_info = parts[0].strip()
        building_info = parts[1].strip()
        
        location["name"] = building_info
        location["address"] = f"{room_info}, {building_info}, Seattle, WA"
    else:
        location["name"] = activity_location.strip()
        location["address"] = f"{activity_location.strip()}, Seattle, WA"
    
    return location

def parse_dates(beginning_date: str, ending_date: str) -> Dict[str, str]:
    """Parse date strings into structured date object"""
    dates = {
        "start_date": "",
        "end_date": ""
    }
    
    try:
        if pd.notna(beginning_date) and beginning_date:
            # Parse date format like "1/23/2025"
            start_dt = pd.to_datetime(beginning_date)
            dates["start_date"] = start_dt.strftime("%Y-%m-%d")
        
        if pd.notna(ending_date) and ending_date:
            end_dt = pd.to_datetime(ending_date)
            dates["end_date"] = end_dt.strftime("%Y-%m-%d")
        elif dates["start_date"]:
            # If no end date, use start date
            dates["end_date"] = dates["start_date"]
            
    except:
        pass
    
    return dates

def parse_schedule(week_days: str, starting_time: str, ending_time: str) -> Dict[str, Any]:
    """Parse schedule information into structured schedule object"""
    schedule = {
        "days": [],
        "times": ""
    }
    
    # Parse days
    if pd.notna(week_days) and week_days:
        day_mapping = {
            'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday', 'Th': 'Thursday',
            'F': 'Friday', 'S': 'Saturday', 'Su': 'Sunday'
        }
        
        # Split by common separators
        day_parts = re.split(r'[,\s]+', week_days.strip())
        for day_part in day_parts:
            if day_part in day_mapping:
                schedule["days"].append(day_mapping[day_part])
    
    # Parse times
    if pd.notna(starting_time) and pd.notna(ending_time) and starting_time and ending_time:
        schedule["times"] = f"{starting_time} - {ending_time}"
    elif pd.notna(starting_time) and starting_time:
        schedule["times"] = starting_time
    
    return schedule

def parse_cost(key_fees_total: float, other_fees_total: float, fee_summary: str) -> str:
    """Parse cost information"""
    try:
        total_cost = 0
        if pd.notna(key_fees_total):
            total_cost += key_fees_total
        if pd.notna(other_fees_total):
            total_cost += other_fees_total
        
        if total_cost > 0:
            return f"${total_cost:.2f}"
        elif pd.notna(fee_summary) and fee_summary:
            if "Free" in fee_summary:
                return "Free"
            else:
                return fee_summary
        else:
            return "Free"
            
    except:
        return "Contact for pricing"

def generate_tags(row: pd.Series) -> Dict[str, List[str]]:
    """Generate structured tags based on activity data"""
    tags = {
        "categories": [],
        "demographics": [],
        "accessibility": [],
        "program_type": []
    }
    
    # Categories based on CategoryName
    category_name = str(row.get('CategoryName', '')).lower()
    if 'academic' in category_name or 'career' in category_name:
        tags["categories"].append('education')
    if 'aquatic' in category_name:
        tags["categories"].append('aquatics')
    if 'art' in category_name or 'craft' in category_name:
        tags["categories"].append('arts')
    if 'athletic' in category_name or 'sport' in category_name:
        tags["categories"].append('sports')
    if 'boat' in category_name:
        tags["categories"].append('boating')
    if 'camp' in category_name:
        tags["categories"].append('camps')
    if 'fitness' in category_name or 'health' in category_name or 'wellness' in category_name:
        tags["categories"].append('fitness')
    if 'nature' in category_name or 'environment' in category_name:
        tags["categories"].append('outdoor')
    if 'performing' in category_name or 'dance' in category_name:
        tags["categories"].append('performing_arts')
    if 'martial' in category_name:
        tags["categories"].append('martial_arts')
    
    # Demographics based on OtherCategoryName and age ranges
    other_category = str(row.get('OtherCategoryName', '')).lower()
    if 'adult' in other_category:
        tags["demographics"].append('adult')
    if 'senior' in other_category:
        tags["demographics"].append('senior')
    if 'teen' in other_category:
        tags["demographics"].append('teen')
    if 'youth' in other_category:
        tags["demographics"].append('youth')
    if 'family' in other_category:
        tags["demographics"].append('family')
    if 'toddler' in other_category or 'early childhood' in other_category:
        tags["demographics"].append('toddler')
    
    # Age-based demographics
    ages_min = row.get('AgesMin', 0)
    ages_max = row.get('AgesMax', 0)
    if pd.notna(ages_min) and ages_min > 0:
        if ages_min < 6:
            tags["demographics"].append('early_childhood')
        elif ages_min < 13:
            tags["demographics"].append('youth')
        elif ages_min < 18:
            tags["demographics"].append('teen')
        elif ages_min >= 55:
            tags["demographics"].append('senior')
        else:
            tags["demographics"].append('adult')
    
    # Program type based on Type and other indicators
    activity_type = str(row.get('Type', '')).lower()
    if 'drop' in str(row.get('ActivityName', '')).lower():
        tags["program_type"].append('drop-in')
    else:
        tags["program_type"].append('registration')
    
    # Cost-based tags
    key_fees = row.get('KeyFeesTotal', 0)
    other_fees = row.get('OtherFeesTotal', 0)
    if pd.isna(key_fees) or key_fees == 0:
        if pd.isna(other_fees) or other_fees == 0:
            tags["program_type"].append('free')
    
    # Remove duplicates
    for category in tags:
        tags[category] = list(set(tags[category]))
    
    return tags

def convert_csv_to_mongodb_schema(csv_file_path: str, output_file_path: str = 'activities_mongodb.json'):
    """Convert CSV to MongoDB schema format"""
    
    # Read CSV file
    print(f"Reading CSV file: {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    
    print(f"Processing {len(df)} activities...")
    
    activities = []
    
    for index, row in df.iterrows():
        # Create MongoDB document
        activity = {
            "organization_name": "Seattle Parks and Recreation",
            "program_description": str(row.get('Description', '')).strip() if pd.notna(row.get('Description')) else "",
            "activity_name": str(row.get('ActivityName', '')).strip() if pd.notna(row.get('ActivityName')) else "",
            "activity_description": str(row.get('Description', '')).strip() if pd.notna(row.get('Description')) else "",
            "location": parse_location(row.get('ActivityLocation')),
            "age_range": parse_age_range(
                row.get('AgesMin'), row.get('AgesMinMonth'), row.get('AgesMinWeek'),
                row.get('AgesMax'), row.get('AgesMaxMonth'), row.get('AgesMaxWeek')
            ),
            "dates": parse_dates(row.get('BeginningDate'), row.get('EndingDate')),
            "schedule": parse_schedule(row.get('WeekDays'), row.get('StartingTime'), row.get('EndingTime')),
            "cost": parse_cost(row.get('KeyFeesTotal'), row.get('OtherFeesTotal'), row.get('FeeSummary')),
            "url": str(row.get('PublicURL', '')).strip() if pd.notna(row.get('PublicURL')) else "",
            "tags": generate_tags(row),
            "last_updated": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source_url": "ParkCatalog.csv"
            }
        }
        
        # Add additional fields from CSV for reference
        activity["_csv_data"] = {
            "activity_id": int(row.get('Activity_ID')) if pd.notna(row.get('Activity_ID')) else None,
            "activity_number": int(row.get('ActivityNumber')) if pd.notna(row.get('ActivityNumber')) else None,
            "season_name": str(row.get('SeasonName', '')).strip() if pd.notna(row.get('SeasonName')) else "",
            "child_season_name": str(row.get('ChildSeasonName', '')).strip() if pd.notna(row.get('ChildSeasonName')) else "",
            "category_name": str(row.get('CategoryName', '')).strip() if pd.notna(row.get('CategoryName')) else "",
            "other_category_name": str(row.get('OtherCategoryName', '')).strip() if pd.notna(row.get('OtherCategoryName')) else "",
            "primary_instructor": str(row.get('PrimaryInstructorName', '')).strip() if pd.notna(row.get('PrimaryInstructorName')) else "",
            "enrollment_min": int(row.get('EnrollMin')) if pd.notna(row.get('EnrollMin')) else None,
            "enrollment_max": str(row.get('EnrollMax', '')).strip() if pd.notna(row.get('EnrollMax')) else "",
            "number_enrolled": int(row.get('NumberEnrolled')) if pd.notna(row.get('NumberEnrolled')) else 0,
            "number_of_hours": float(row.get('NumberOfHours')) if pd.notna(row.get('NumberOfHours')) else None,
            "number_of_dates": int(row.get('NumberOfDates')) if pd.notna(row.get('NumberOfDates')) else None
        }
        
        activities.append(activity)
        
        # Progress indicator
        if (index + 1) % 100 == 0:
            print(f"Processed {index + 1} activities...")
    
    # Save to JSON file
    print(f"Saving to {output_file_path}...")
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(activities, f, indent=2, ensure_ascii=False)
    
    print(f"Conversion completed! Saved {len(activities)} activities to {output_file_path}")
    
    # Generate summary statistics
    summary = {
        "total_activities": len(activities),
        "organizations": list(set([a["organization_name"] for a in activities])),
        "categories_found": [],
        "demographics_found": [],
        "program_types_found": [],
        "cost_distribution": {"free": 0, "paid": 0, "unknown": 0},
        "location_count": len(set([a["location"]["name"] for a in activities if a["location"]["name"]])),
        "date_range": {
            "earliest": None,
            "latest": None
        }
    }
    
    # Collect tag statistics
    all_categories = set()
    all_demographics = set()
    all_program_types = set()
    all_dates = []
    
    for activity in activities:
        all_categories.update(activity["tags"]["categories"])
        all_demographics.update(activity["tags"]["demographics"])
        all_program_types.update(activity["tags"]["program_type"])
        
        # Cost distribution
        cost = activity["cost"].lower()
        if "free" in cost or "$0" in cost:
            summary["cost_distribution"]["free"] += 1
        elif "$" in cost:
            summary["cost_distribution"]["paid"] += 1
        else:
            summary["cost_distribution"]["unknown"] += 1
        
        # Date range
        if activity["dates"]["start_date"]:
            all_dates.append(activity["dates"]["start_date"])
    
    summary["categories_found"] = sorted(list(all_categories))
    summary["demographics_found"] = sorted(list(all_demographics))
    summary["program_types_found"] = sorted(list(all_program_types))
    
    if all_dates:
        summary["date_range"]["earliest"] = min(all_dates)
        summary["date_range"]["latest"] = max(all_dates)
    
    # Save summary
    summary_file = output_file_path.replace('.json', '_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to {summary_file}")
    
    return activities, summary

def main():
    """Main execution function"""
    csv_file = 'ParkCatalog.csv'
    output_file = 'seattle_parks_activities_mongodb.json'
    
    try:
        activities, summary = convert_csv_to_mongodb_schema(csv_file, output_file)
        
        print(f"\n{'='*50}")
        print("CONVERSION SUMMARY")
        print(f"{'='*50}")
        print(f"Total activities processed: {summary['total_activities']}")
        print(f"Unique locations: {summary['location_count']}")
        print(f"Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
        print(f"Cost distribution: {summary['cost_distribution']}")
        print(f"Categories found: {len(summary['categories_found'])}")
        print(f"Demographics found: {len(summary['demographics_found'])}")
        print(f"Program types found: {len(summary['program_types_found'])}")
        
        # Show sample activity
        if activities:
            print(f"\nSample activity (first record):")
            print(json.dumps(activities[0], indent=2)[:1000] + "..." if len(json.dumps(activities[0], indent=2)) > 1000 else json.dumps(activities[0], indent=2))
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        raise

if __name__ == "__main__":
    main()