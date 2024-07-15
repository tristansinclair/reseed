import streamlit as st
import folium
import json
from streamlit_folium import st_folium
from folium import Marker, Popup
from geopy.geocoders import Nominatim
loc = Nominatim(user_agent="Geopy Library")



# Load data
with open('data/apartments_COMPLETE_2024-07-14-23-47-46.json') as f:
    data = json.load(f)

# Initialize Streamlit app
st.title('San Diego Apartments')

# Create a Folium map centered around San Diego
map_center = [32.7157, -117.1611]
m = folium.Map(location=map_center, zoom_start=12)

# Add markers for each apartment
for apartment in data:
    if 'address' in apartment and apartment['address']:
        try:
            # entering the location name
            getLoc = loc.geocode(apartment['address'])
            # printing address
            # print(getLoc.address)

            # printing latitude and longitude
            # print("Latitude = ", getLoc.latitude, "\n")
            # print("Longitude = ", getLoc.longitude)
            # Extract latitude and longitude from address (you may need a geocoding step here)
            # Here, we assume you have latitude and longitude already, if not, you need to use a geocoding service
            # lat, lon = get_lat_lon_from_address()  # Define this function or use geopy
            info = f"""
            Name: {apartment.get('name', 'N/A')}<br>
            Neighborhood: {apartment.get('neighborhood', 'N/A')}<br>
            Address: {apartment.get('address', 'N/A')}<br>
            Rent: {apartment.get('rent', 'N/A')}<br>
            Beds: {apartment.get('beds', 'N/A')}<br>
            Baths: {apartment.get('baths', 'N/A')}<br>
            Sq Ft: {apartment.get('sq_ft', 'N/A')}
            """
            Marker(
                location=[getLoc.latitude, getLoc.longitude],
                popup=Popup(info, max_width=300),
                tooltip=apartment.get('name', 'Apartment')
            ).add_to(m)
        except Exception as e:
            st.error(f"Error processing apartment: {apartment.get('name', 'N/A')} - {e}")

# Render the map in Streamlit
st_data = st_folium(m, width=725)

# Define a function to get latitude and longitude from address (assuming this step is needed)
def get_lat_lon_from_address(address):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    return location.latitude, location.longitude
