# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Port State Control Dashboard - Japan August 2024",
    layout="wide",
    initial_sidebar_state="expanded")

# Load data
df = pd.read_csv('japan2024Aug.csv')

# Convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')

# Sidebar
with st.sidebar:
    st.title('🚢 Port State Control Dashboard')
    
    place_list = list(df['Place'].unique())
    selected_place = st.selectbox('Select a place', place_list, index=0)
    
    df_filtered = df[df['Place'] == selected_place]

# Define the map visualization function
def make_map(data):
    fig = px.scatter_geo(
        data,
        locations="Place",
        locationmode='country names',
        size='Deficiencies',
        color='Deficiencies',
        hover_name='Ship Name',
        size_max=15,
        projection='natural earth')
    fig.update_geos(
        visible=False,
        zoom=1.2,
        center=dict(lat=36.2048, lon=138.2529),
        scalezoom=0.5)
    return fig

# Create a map
map_fig = make_map(df_filtered)

# Main panel
st.subheader(f'Port State Control Dashboard for {selected_place}')
st.plotly_chart(map_fig, use_container_width=True)

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

# Set up Altair theme
alt.themes.enable('dark')

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
