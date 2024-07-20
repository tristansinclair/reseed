import streamlit as st
import folium
import json
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from folium.map import Marker, Popup
from geopy.geocoders import Nominatim
import random

# Load data
with open('data/apartments_COMPLETE_2024-07-14-23-47-46.json') as f:
    data = json.load(f)

# Initialize Streamlit app
st.title('San Diego Apartments')

# Sidebar filters
st.sidebar.header('Filter Options')
bedrooms = st.sidebar.slider('Number of Bedrooms', 0, 5, (0, 5))
# bathrooms = st.sidebar.slider('Number of Bathrooms', 1.0, 3.0, (1.0, 3.0)) increment this in 0.5s
bathrooms = st.sidebar.slider('Number of Bathrooms', 1.0, 3.0, (1.0, 3.0), 0.5)
# sq_ft_min = st.sidebar.number_input('Min Square Footage', value=0) increment in 100s
sq_ft_min = st.sidebar.number_input('Min Square Footage', value=0, step=100)
sq_ft_max = st.sidebar.number_input('Max Square Footage', value=5000, step=100)
rent_min = st.sidebar.number_input('Min Rent', value=0, step=100)
rent_max = st.sidebar.number_input('Max Rent', value=10000, step=100)

# Filter the data based on user input
filtered_data = [
    apt for apt in data if
    (apt.get('beds_min') is not None and bedrooms[0] <= apt.get('beds_min', 0) <= bedrooms[1]) and
    (apt.get('baths_min') is not None and bathrooms[0] <= apt.get('baths_min', 0.0) <= bathrooms[1]) and
    (apt.get('sq_ft_min') is not None and sq_ft_min <= apt.get('sq_ft_min', 0) <= sq_ft_max) and
    (apt.get('rent_min') is not None and rent_min <= apt.get('rent_min', 0) <= rent_max)
]

# Create a Folium map centered around San Diego
map_center = [32.7157, -117.1611]
zoom_start = 12

# Function to add markers to the map
def add_markers_to_map(m, data, zoom):
    cluster = MarkerCluster().add_to(m)
    for apartment in data:
        if 'address' in apartment and apartment['address']:
            info = f"""
            Name: {apartment.get('name', 'N/A')}<br>
            Neighborhood: {apartment.get('neighborhood', 'N/A')}<br>
            Address: {apartment.get('address', 'N/A')}<br>
            Rent: {apartment.get('rent', 'N/A')}<br>
            Beds: {apartment.get('beds', 'N/A')}<br>
            Baths: {apartment.get('baths', 'N/A')}<br>
            Sq Ft: {apartment.get('sq_ft', 'N/A')}
            """
            if zoom < 15:
                if random.random() > 0.1:  # Show fewer markers at lower zoom levels
                    continue
            # For now, randomize the lat long in the San Diego area
            lat = round(32.7157 + (0.1 * (2 * random.random() - 1)), 4)
            lon = round(-117.1611 + (0.1 * (2 * random.random() - 1)), 4)
            
            Marker(
                location=[lat, lon],
                popup=Popup(info, max_width=300),
                tooltip=apartment.get('name', 'Apartment')
            ).add_to(cluster)

# Initialize the map in session state if not already present
if 'map' not in st.session_state:
    st.session_state['map'] = folium.Map(location=map_center, zoom_start=zoom_start)
    st.session_state['zoom'] = zoom_start
    add_markers_to_map(st.session_state['map'], filtered_data, zoom_start)

# Render the map in Streamlit with a unique key
st_data = st_folium(st.session_state['map'], width=725, height=500, key='initial_map')

# Get the current zoom level from st_folium output
current_zoom = st_data['zoom']

# Update the map if the zoom level has changed
if current_zoom != st.session_state['zoom']:
    st.session_state['map'] = folium.Map(location=map_center, zoom_start=current_zoom)
    st.session_state['zoom'] = current_zoom
    add_markers_to_map(st.session_state['map'], filtered_data, current_zoom)

    # Render the updated map with a unique key
    st_data = st_folium(st.session_state['map'], width=725, height=500, key='updated_map')
