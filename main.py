import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from geopy.geocoders import Nominatim
import folium

# Page configuration
st.set_page_config(
    page_title="Port State Control Dashboard - Japan August 2024",
    layout="wide",
    initial_sidebar_state="expanded")

# Load data
df = pd.read_csv('japan2024Aug.csv')

# Convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')

# Geocoding function
def get_location(place_name):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(place_name)
    if location:
        return [location.latitude, location.longitude]
    else:
        return [None, None]

# Add latitude and longitude to the dataframe
df['Latitude'], df['Longitude'] = zip(*df['Place'].apply(get_location))

# Filter null locations
df = df.dropna(subset=['Latitude', 'Longitude'])

# Sidebar
with st.sidebar:
    st.title('🚢 Port State Control Dashboard')
    
    place_list = list(df['Place'].unique())
    selected_place = st.selectbox('Select a place', place_list, index=0)
    
    df_filtered = df[df['Place'] == selected_place]

# Define the map visualization function
def make_map(data):
    map = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=6, tiles='Stamen Terrain')
    for index, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Place']} - {row['Deficiencies']} Deficiencies"
        ).add_to(map)
    return map

# Create a map
map_fig = make_map(df_filtered)

# Main panel
st.subheader(f'Port State Control Dashboard for {selected_place}')
st.map(map_fig)

# Bar chart for deficiencies
deficiencies_chart = px.bar(
    df_filtered,
    x='Deficiencies',
    y='Ship Name',
    color='Deficiencies',
    title='Deficiencies per Ship',
    labels={'Deficiencies': 'Number of Deficiencies'},
    height=600
)
st.subheader('Deficiencies per Ship')
st.plotly_chart(deficiencies_chart, use_container_width=True)

# Table display
st.subheader('Inspection Details')
st.dataframe(df_filtered[['Type', 'Date', 'Place', 'IMO number', 'Ship Name', 'Flag', 'Deficiencies', 'Detention', 'Ship Risk Profile at the time of inspection']], height=500)

# Heatmap for inspection types over time
heatmap_data = df_filtered.pivot_table(values='Deficiencies', index='Date', columns='Type', aggfunc='sum').fillna(0)
heatmap = alt.Chart(heatmap_data.reset_index()).mark_rect().encode(
    x='Date:O',
    y='Type:O',
    color='Deficiencies:Q',
    tooltip=['Date', 'Type', 'Deficiencies']
).properties(
    width=600,
    height=300
)
st.subheader('Heatmap of Inspections Over Time')
st.altair_chart(heatmap, use_container_width=True)
