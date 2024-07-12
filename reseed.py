import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Initialize the geocoder
geolocator = Nominatim(user_agent="my_app")

# Function to get location suggestions
def get_suggestions(query):
    try:
        return geolocator.geocode(query, exactly_one=False, limit=5)
    except GeocoderTimedOut:
        return None

# Callback function for text input
def on_input_change():
    suggestions = get_suggestions(st.session_state.location_input)
    if suggestions:
        st.session_state.suggestions = [loc.address for loc in suggestions]
    else:
        st.session_state.suggestions = []

# Main app
st.title("Interactive Map Search")

# Initialize session state variables
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []

if 'marker_location' not in st.session_state:
    st.session_state.marker_location = None

# Text input with callback
st.text_input("Search for a location", key="location_input", on_change=on_input_change)

# Display suggestions
if st.session_state.suggestions:
    selected_suggestion = st.selectbox("Suggestions", st.session_state.suggestions)
    if selected_suggestion:
        location = geolocator.geocode(selected_suggestion)
        if location:
            x, y = location.latitude, location.longitude
            
            # Create the Folium map centered on the selected location
            m = folium.Map(location=[x, y], zoom_start=12)
            
            # Add LatLngPopup to allow dropping a pin
            m.add_child(folium.LatLngPopup())
            
            # Add a marker if a location has been clicked
            if st.session_state.marker_location:
                folium.Marker(st.session_state.marker_location).add_to(m)
            
            # Display the map
            map_data = st_folium(m, width=700, height=500)
            
            # Capture the clicked location's coordinates
            if map_data and map_data['last_clicked']:
                st.session_state.marker_location = [map_data['last_clicked']['lat'], map_data['last_clicked']['lng']]
else:
    st.write("No suggestions found. Try typing a location.")

# Default map view when no location is selected
if not st.session_state.location_input:
    default_location = [0, 0]  # Default to (0, 0) coordinates
    m = folium.Map(location=default_location, zoom_start=2)
    m.add_child(folium.LatLngPopup())
    
    # Add a marker if a location has been clicked
    if st.session_state.marker_location:
        folium.Marker(st.session_state.marker_location).add_to(m)
    
    map_data = st_folium(m, width=700, height=500)
    
    # Capture the clicked location's coordinates
    if map_data and map_data['last_clicked']:
        st.session_state.marker_location = [map_data['last_clicked']['lat'], map_data['last_clicked']['lng']]
