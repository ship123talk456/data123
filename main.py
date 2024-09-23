# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import folium

# Page configuration
st.set_page_config(
    page_title="Port State Control Dashboard - Japan August 2024",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# CSS styling
st.markdown("""
<style>
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}
[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
""", unsafe_allow_html=True)

# Load data
df = pd.read_csv('japan2024Aug.csv')

# Convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')

# Sidebar
with st.sidebar:
    st.title('🚢 Port State Control Dashboard')
    
    month_list = ['August']
    selected_month = st.selectbox('Select a month', month_list, index=0)
    
    place_list = list(df['Place'].unique())
    selected_place = st.selectbox('Select a place', place_list, index=0)
    
    df_filtered = df[(df['Place'] == selected_place) & (df['Date'].dt.strftime('%B') == selected_month)]

# Map visualization
def make_map(data):
    # Create a map centered around Japan
    map = folium.Map(location=[36.2048, 138.2529], zoom_start=6, tiles='Stamen Terrain')
    
    # Add markers for each inspection location
    for index, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Place']} - {row['Deficiencies']} Deficiencies"
        ).add_to(map)
    
    return map

# Since we don't have Latitude and Longitude in the CSV, we'll skip the map part.
# If you have this data, you can uncomment the following part and use make_map function.

# Generate map
# map = make_map(df_filtered)
# st.map(map)

# Plots
def make_heatmap(data):
    heatmap = alt.Chart(data).mark_rect().encode(
        y=alt.Y('Type:N', axis=alt.Axis(title="Inspection Type")),
        x=alt.X('Date:N', axis=alt.Axis(title="Date")),
        color=alt.Color('Deficiencies:Q', scale=alt.Scale(scheme='redyellowblue')),
        tooltip=['Ship Name', 'Deficiencies', 'Detention']
    ).properties(width=600, height=400)
    return heatmap

heatmap = make_heatmap(df_filtered)

# Dashboard Main Panel
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('#### Total Inspections')
    st.metric(label='Total Inspections', value=len(df_filtered))

with col2:
    st.markdown('#### Inspections Heatmap')
    st.altair_chart(heatmap, use_container_width=True)

# If you have the latitude and longitude data, you can display the map with:
# st.map(map)
