import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Load the CSV file into a DataFrame
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    return data

# Main App
st.title("Japan PSC Inspection Dashboard - August 2024")

# File path for CSV (replace with your local path if needed)
csv_file = 'japan2024Aug.csv'
df = load_data(csv_file)

# Sidebar for filtering data
st.sidebar.header("Filter Options")
place_filter = st.sidebar.selectbox("Select Inspection Place", df['Place'].unique())
month_filter = st.sidebar.slider("Select Month", 1, 12, 8)

# Filter the data based on selections
filtered_data = df[(df['Place'] == place_filter) & (df['Date'].dt.month == month_filter)]

# Dashboard Metrics
total_inspections = filtered_data.shape[0]
total_deficiencies = filtered_data['Deficiencies'].sum()
total_detentions = filtered_data['Detention'].sum()

# Display Metrics
st.subheader(f"Overview of PSC Inspections in {place_filter} for August 2024")
col1, col2, col3 = st.columns(3)
col1.metric("Total Inspections", total_inspections)
col2.metric("Total Deficiencies", total_deficiencies)
col3.metric("Total Detentions", total_detentions)

# Visualization 1: Ship Risk Profile Distribution
st.subheader("Ship Risk Profile Distribution")
risk_profile_count = filtered_data['Ship Risk Profile at the time of inspection'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(risk_profile_count, labels=risk_profile_count.index, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# Visualization 2: Deficiencies by Place
st.subheader("Deficiencies by Place")
deficiencies_by_place = df.groupby('Place')['Deficiencies'].sum().reset_index()
fig2 = px.bar(deficiencies_by_place, x='Place', y='Deficiencies', title="Deficiencies by Inspection Place")
st.plotly_chart(fig2)

# Visualization 3: Map of Inspection Locations
st.subheader("Inspection Locations Map")
inspection_map = folium.Map(location=[35.682839, 139.759455], zoom_start=5)  # Centered on Japan

for _, row in filtered_data.iterrows():
    folium.Marker(location=[row['Lat'], row['Long']],
                  popup=f"Ship: {row['Ship Name']}, Deficiencies: {row['Deficiencies']}").add_to(inspection_map)

st_folium(inspection_map, width=700, height=500)

# Option to download filtered data
st.sidebar.download_button(label="Download Filtered Data", data=filtered_data.to_csv(), mime='text/csv')
