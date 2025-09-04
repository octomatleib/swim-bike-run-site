# scripts/fetch_data.py
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from garminconnect import Garmin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_garmin():
    """Connect to Garmin using credentials from environment variables"""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password:
        raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set")
    
    try:
        # Try to load existing session
        client = Garmin()
        client.login(email, password)
        logger.info("Successfully connected to Garmin Connect")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Garmin: {e}")
        raise

def fetch_activities(client, days_back=365):
    """Fetch activities from the last N days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    activities = []
    
    try:
        # Get activities list
        activities_list = client.get_activities(0, 100)  # Adjust limit as needed
        
        for activity in activities_list:
            activity_date = datetime.fromisoformat(activity['startTimeLocal'].replace('Z', '+00:00'))
            
            # Filter by date and activity types
            if (activity_date >= start_date and 
                activity['activityType']['typeKey'] in ['running', 'cycling', 'lap_swimming', 'open_water_swimming']):
                
                # Get detailed activity data
                activity_id = activity['activityId']
                detailed_activity = client.get_activity(activity_id)
                
                # Extract relevant data
                activity_data = {
                    'id': activity_id,
                    'date': activity_date.isoformat(),
                    'type': activity['activityType']['typeKey'],
                    'name': activity.get('activityName', ''),
                    'distance': activity.get('distance', 0),  # in meters
                    'duration': activity.get('duration', 0),  # in seconds
                    'calories': activity.get('calories', 0),
                    'avg_heart_rate': activity.get('averageHR'),
                    'max_heart_rate': activity.get('maxHR'),
                    'avg_speed': activity.get('averageSpeed'),
                    'max_speed': activity.get('maxSpeed'),
                    'elevation_gain': activity.get('elevationGain'),
                    'start_lat': detailed_activity.get('startLatitude'),
                    'start_lon': detailed_activity.get('startLongitude')
                }
                
                activities.append(activity_data)
                logger.info(f"Fetched activity: {activity_data['name']} ({activity_data['type']})")
        
        return activities
        
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        return []

def save_data(activities):
    """Save activities data to JSON file"""
    os.makedirs('data', exist_ok=True)
    
    # Save raw data
    with open('data/activities.json', 'w') as f:
        json.dump(activities, f, indent=2, default=str)
    
    # Save as CSV for easier analysis
    df = pd.DataFrame(activities)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['distance_km'] = df['distance'] / 1000
        df['duration_minutes'] = df['duration'] / 60
        df.to_csv('data/activities.csv', index=False)
    
    logger.info(f"Saved {len(activities)} activities to data files")

def main():
    try:
        client = connect_to_garmin()
        activities = fetch_activities(client)
        save_data(activities)
        
        # Save timestamp of last update
        with open('data/last_update.json', 'w') as f:
            json.dump({'last_update': datetime.now().isoformat()}, f)
            
        logger.info("Data fetch completed successfully")
        
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        raise

if __name__ == "__main__":
    main()