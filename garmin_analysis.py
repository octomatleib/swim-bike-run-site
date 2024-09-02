# %%
# Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
from garminconnect import Garmin
from garminconnect import (
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)

# Reading Garmin account credentials
load_dotenv()
email = os.getenv('email')
password = os.getenv('password')

# Authenticate with Garmin Connect
garmin = Garmin(email, password)
garmin.login()

try:
    # Create a Garmin client and login
    client = Garmin(email, password)
    client.login()
    # Fetch user profile data
    user_data = client.get_user_profile()
    print("User Profile Data:", user_data)
except GarminConnectConnectionError as err:
    print("Error connecting to Garmin Connect:", err)
except GarminConnectAuthenticationError as err:
    print("Error authenticating with Garmin Connect:", err)
except GarminConnectTooManyRequestsError as err:
    print("Too many requests made to Garmin Connect:", err)
except Exception as err:
    print("An error occurred:", err)

# Fetch activities data
activities = client.get_activities(0,10000)  # Fetch all activities

# Convert activities to DataFrame
df = pd.DataFrame(activities)

# Extract 'typeKey' from 'activityType' and create a new column 'typeKey'
df['typeKey'] = df['activityType'].apply(lambda x: x['typeKey'])

# Filter typeKeys
typeKeylist = ['cycling', 'running', 'lap_swimming', 'open_water_swimming']
df = df[df['typeKey'].isin(typeKeylist)]

# Converting data types
df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

# Data transformations
df['distance'] = df['distance']/1000

# Parse dates and sort the data by date
df = df.sort_values(by='startTimeLocal')

# Add year column
df['Year'] = df['startTimeLocal'].dt.year

# Get list of unique years and typeKeys
years = df['Year'].unique()
type_keys = df['typeKey'].unique()

# Create a multiselect widget for filtering years, default all years are selected
selected_years = st.multiselect('Select Years', options=years, default=years)

# Create a plot for each typeKey
for type_key in type_keys:
    st.subheader(f'Cumulative Distance for {type_key}')
    
    # Filter data for the current typeKey
    type_key_df = df[df['typeKey'] == type_key]
    
    # Further filter by selected years
    filtered_df = type_key_df[type_key_df['Year'].isin(selected_years)]
    
    # Calculate cumulative distance
    filtered_df['Cumulative Distance'] = filtered_df['distance'].cumsum()
    
    # Plot cumulative distance over time
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_df['startTimeLocal'], filtered_df['Cumulative Distance'], label=type_key)
    
    plt.title(f'Cumulative Distance ({type_key})')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Distance (km)')
    plt.grid(True)
    
    # Show the plot in the Streamlit app
    st.pyplot(plt.gcf())
    
    # Optional: Show the raw data for this typeKey
    st.write(filtered_df)
