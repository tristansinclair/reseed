import streamlit as st
import folium
import json
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from folium.map import Marker, Popup
import pandas as pd
from streamlit_extras.image_in_tables import table_with_images
from streamlit_extras.grid import grid
from folium.plugins import Draw

# Load data
with open(
    "costar/building_data/2024-07-22-23-47-05/costar_data_2024-07-22-23-47-05.csv"
) as f:
    data = pd.read_csv(f)
    # Property Address,Property Name,Number Of Units,Star Rating,Building Class,PropertyType,Secondary Type,Affordable Type,Building Status,Market Name,Submarket Name,City,State,Zip,Avg Unit SF,Avg Asking/SF,Avg Asking/Unit,For Sale Price,Cap Rate,$Price/Unit,Sale Company Name,Sale Company Address,Sale Company City State Zip,Sale Company Phone,Sale Company Fax,Sale Company Contact,Vacancy %,Month Built,Year Built,Year Renovated,Number Of Stories,Total Buildings,Rent Type,Property Manager Name,Property Manager Contact,Property Manager Phone,PropertyID,Owner Contact,Owner Name,Number Of Parking Spaces,County Name,Amenities,Number Of 1 Bedrooms Units,Number Of 2 Bedrooms Units,Number Of 3 Bedrooms Units,Number Of 4 Bedrooms Units,Number Of Studios Units,Number Of Elevators,Operational Status,Latitude,Longitude,Four Bedroom Vacancy %,One Bedroom Vacancy %,Studio Vacancy %,Three Bedroom Vacancy %,Two Bedroom Vacancy %

# Initialize Streamlit app
st.title("San Diego Apartments")


# Sidebar filters
st.sidebar.header("Filter Options")
# costar_ranking = st.sidebar.slider("Costar Ranking", 1, 5, (1, 5))
costar_ranking = st.sidebar.slider("Costar Ranking", 1, 5, (4, 5))
number_of_units = st.sidebar.slider("Number of Units", 0, 300, (0, 300))
# bedrooms = st.sidebar.slider('Number of Bedrooms', 0, 5, (0, 5))
# bathrooms = st.sidebar.slider('Number of Bathrooms', 1.0, 3.0, (1.0, 3.0), 0.5)
# sq_ft_min = st.sidebar.number_input('Min Square Footage', value=0, step=100)
# sq_ft_max = st.sidebar.number_input('Max Square Footage', value=5000, step=100)
# avg_sq_ft_input = st.sidebar.slider('Unit Avg. Square Footage', 0, 4000, (0, 4000), 100)
# avg_rent_input = st.sidebar.slider('Unit Avg. Rent', 0,  step=100)
year_built_input = st.sidebar.slider("Year Built", 1900, 2027, (1900, 2027), 1)


# Filter data, if certain filters are active and the data is empty, just leave it out
filtered_data = data[
    (data["Star Rating"] >= costar_ranking[0])
    & (data["Star Rating"] <= costar_ranking[1])
    & (data["Number Of Units"] >= number_of_units[0])
    & (data["Number Of Units"] <= number_of_units[1])
    &
    # (data['Avg Unit SF'] >= avg_sq_ft_input[0]) & (data['Avg Unit SF'] <= avg_sq_ft_input[1]) &
    # (data['Avg Asking/SF'] >= avg_rent_input[0]) & (data['Avg Asking/SF'] <= avg_rent_input[1]) &
    (data["Year Built"] >= year_built_input[0])
    & (data["Year Built"] <= year_built_input[1])
]


# Show the map
st.header("Map")
m = folium.Map(location=(32.7157, -117.1611), zoom_start=12)
for i, row in filtered_data.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=row["Property Name"],
    ).add_to(m)

Draw(export=True).add_to(m)


st_data = st_folium(m, width=1000)


filtered_data = filtered_data[filtered_data["Latitude"] > st_data["bounds"]["_southWest"]["lat"]]
filtered_data = filtered_data[filtered_data["Latitude"] < st_data["bounds"]["_northEast"]["lat"]]
filtered_data = filtered_data[filtered_data["Longitude"] > st_data["bounds"]["_southWest"]["lng"]]
filtered_data = filtered_data[filtered_data["Longitude"] < st_data["bounds"]["_northEast"]["lng"]]
st.write(f"Number of properties in view: {len(filtered_data)}")

view_selector = st.radio("Table Views", ["All", "Unit Breakdown"])

# here we create the view
if view_selector == "All":
    # show all the data columns
    view_data = filtered_data
    st.dataframe(view_data)
elif view_selector == "Unit Breakdown":
    # show the data columns: Number Of Units, Number Of 1 Bedrooms Units, Number Of 2 Bedrooms Units, Number Of 3 Bedrooms Units, Number Of 4 Bedrooms Units, Number Of Studios Units
    view_data = filtered_data[
        [
            "Property Name",
            "Property Address",
            "Number Of Units",
            "Number Of 1 Bedrooms Units",
            "Number Of 2 Bedrooms Units",
            "Number Of 3 Bedrooms Units",
            "Number Of 4 Bedrooms Units",
            "Number Of Studios Units",
        ]
    ]
    st.dataframe(view_data)
