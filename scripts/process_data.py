# scripts/process_data.py
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def load_activities():
    """Load activities from JSON file"""
    try:
        with open('data/activities.json', 'r') as f:
            activities = json.load(f)
        return pd.DataFrame(activities)
    except FileNotFoundError:
        print("No activities data found")
        return pd.DataFrame()

def calculate_summary_stats(df):
    """Calculate summary statistics by activity type"""
    if df.empty:
        return {}
    
    df['date'] = pd.to_datetime(df['date'])
    df['distance_km'] = df['distance'] / 1000
    df['duration_hours'] = df['duration'] / 3600
    
    stats = {}
    
    # Overall stats
    stats['total_activities'] = len(df)
    stats['total_distance_km'] = df['distance_km'].sum()
    stats['total_duration_hours'] = df['duration_hours'].sum()
    stats['total_calories'] = df['calories'].sum()
    
    # By activity type
    stats['by_type'] = {}
    for activity_type in df['type'].unique():
        type_df = df[df['type'] == activity_type]
        stats['by_type'][activity_type] = {
            'count': len(type_df),
            'total_distance_km': type_df['distance_km'].sum(),
            'avg_distance_km': type_df['distance_km'].mean(),
            'total_duration_hours': type_df['duration_hours'].sum(),
            'avg_duration_hours': type_df['duration_hours'].mean(),
            'total_calories': type_df['calories'].sum()
        }
    
    return stats

def create_monthly_trends(df):
    """Create monthly trend data"""
    if df.empty:
        return []
    
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    df['distance_km'] = df['distance'] / 1000
    
    monthly_data = []
    
    for month in df['month'].unique():
        month_df = df[df['month'] == month]
        
        month_stats = {
            'month': str(month),
            'total_activities': len(month_df),
            'total_distance_km': month_df['distance_km'].sum(),
            'by_type': {}
        }
        
        # Break down by activity type
        for activity_type in month_df['type'].unique():
            type_df = month_df[month_df['type'] == activity_type]
            month_stats['by_type'][activity_type] = {
                'count': len(type_df),
                'distance_km': type_df['distance_km'].sum()
            }
        
        monthly_data.append(month_stats)
    
    # Sort by month
    monthly_data.sort(key=lambda x: x['month'])
    return monthly_data

def create_weekly_trends(df):
    """Create weekly distance trends"""
    if df.empty:
        return []
    
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.to_period('W')
    df['distance_km'] = df['distance'] / 1000
    
    weekly_data = []
    
    for week in df['week'].unique():
        week_df = df[df['week'] == week]
        
        weekly_stats = {
            'week': str(week),
            'week_start': week.start_time.isoformat(),
            'total_distance_km': week_df['distance_km'].sum(),
            'activities': len(week_df),
            'by_type': {}
        }
        
        # Break down by activity type
        for activity_type in week_df['type'].unique():
            type_df = week_df[week_df['type'] == activity_type]
            weekly_stats['by_type'][activity_type] = type_df['distance_km'].sum()
        
        weekly_data.append(weekly_stats)
    
    # Sort by week and take last 12 weeks
    weekly_data.sort(key=lambda x: x['week'])
    return weekly_data[-12:]

def create_recent_activities(df, limit=10):
    """Get recent activities for display"""
    if df.empty:
        return []
    
    df['date'] = pd.to_datetime(df['date'])
    df['distance_km'] = df['distance'] / 1000
    df['duration_minutes'] = df['duration'] / 60
    
    recent = df.nlargest(limit, 'date')
    
    activities = []
    for _, row in recent.iterrows():
        activities.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'name': row['name'],
            'type': row['type'],
            'distance_km': round(row['distance_km'], 2),
            'duration_minutes': round(row['duration_minutes'], 1),
            'calories': int(row['calories']) if pd.notna(row['calories']) else None
        })
    
    return activities

def generate_dashboard_data():
    """Generate all dashboard data"""
    df = load_activities()
    
    dashboard_data = {
        'generated_at': datetime.now().isoformat(),
        'summary': calculate_summary_stats(df),
        'monthly_trends': create_monthly_trends(df),
        'weekly_trends': create_weekly_trends(df),
        'recent_activities': create_recent_activities(df)
    }
    
    return dashboard_data

def save_dashboard_data(dashboard_data):
    """Save dashboard data to docs folder for GitHub Pages"""
    os.makedirs('docs', exist_ok=True)
    
    # Save main dashboard data
    with open('docs/dashboard_data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    print(f"Generated dashboard data with {len(dashboard_data.get('recent_activities', []))} recent activities")

def main():
    try:
        dashboard_data = generate_dashboard_data()
        save_dashboard_data(dashboard_data)
        print("Dashboard data processing completed successfully")
        
    except Exception as e:
        print(f"Error processing dashboard data: {e}")
        raise

if __name__ == "__main__":
    main()