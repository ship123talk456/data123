# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import folium

# Page configuration
st.set_page_config(
    page_title="Port State Control Dashboard",
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
df = pd.read_csv('data/japan_port_inspections_2024_08.csv')

# Sidebar
with st.sidebar:
    st.title('🚢 Port State Control Dashboard')
    
    place_list = list(df['Place'].unique())
    selected_place = st.selectbox('Select a place', place_list, index=0)
    
    month_list = ['August', 'September', 'October', 'November', 'December']
    selected_month = st.selectbox('Select a month', month_list, index=0)
    
    df_filtered = df[(df['Place'] == selected_place) & (df['Date'].str.contains(selected_month))]

# Map visualization
def make_map(data):
    map = folium.Map(location=[36.2048, 138.2529], zoom_start=6, tiles='Stamen Terrain')
    for index, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Place']} - {row['Deficiencies']} Deficiencies"
        ).add_to(map)
    return map

# Generate map
map = make_map(df_filtered)

# Plots
def make_heatmap(data):
    heatmap = alt.Chart(data).mark_rect().encode(
        y=alt.Y('Type:O', axis=alt.Axis(title="Inspection Type")),
        x=alt.X('Date:O', axis=alt.Axis(title="Date")),
        color=alt.Color('Deficiencies:Q', scale=alt.Scale(scheme='redyellowblue')),
        tooltip=['Ship Name', 'Deficiencies']
    ).properties(width=600, height=400)
    return heatmap

heatmap = make_heatmap(df_filtered)

# Dashboard Main Panel
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.markdown('#### Total Inspections')
    st.metric(label='Total Inspections', value=len(df_filtered))

with col2:
    st.markdown('#### Inspections Heatmap')
    st.altair_chart(heatmap, use_container_width=True)

with col3:
    st.markdown('#### Map of Inspections')
    st.map(map)

# Save map to HTML
map.save('inspections_map.html')
st.download_button(
    label="Download Inspections Map",
    data=open('inspections_map.html', 'rb').read(),
    file_name='inspections_map.html',
    mime='text/html'
)
