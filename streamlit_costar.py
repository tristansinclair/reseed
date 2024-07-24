import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
from shapely.geometry import Point, Polygon


def filter_data_within_bounds(data, polygon):
    # Function to check if a point is within the polygon
    def is_within_bounds(lat, lon, polygon):
        point = Point(lon, lat)
        return polygon.contains(point)

    # Apply the filter to the dataframe
    filtered_data = data[
        data.apply(
            lambda row: is_within_bounds(row["Latitude"], row["Longitude"], polygon),
            axis=1,
        )
    ]

    return filtered_data


# Load data
data = pd.read_csv(
    "costar/building_data/2024-07-22-23-47-05/costar_data_2024-07-22-23-47-05.csv"
)

# Initialize Streamlit app
st.set_page_config(page_title="ReSeed Costar", layout="wide")
st.title("San Diego Apartments")

# Sidebar filters
st.sidebar.header("Filter Options")
costar_ranking = st.sidebar.slider("Costar Ranking", 1, 5, (4, 5))
number_of_units = st.sidebar.slider("Number of Units", 0, 300, (0, 300))
year_built_input = st.sidebar.slider("Year Built", 1900, 2027, (1900, 2027), 1)
vacancy_rate = st.sidebar.slider("Vacancy %", 0, 100, (0, 100))

# Filter data based on sidebar inputs
filtered_data = data[
    (data["Star Rating"] >= costar_ranking[0])
    & (data["Star Rating"] <= costar_ranking[1])
    & (data["Number Of Units"] >= number_of_units[0])
    & (data["Number Of Units"] <= number_of_units[1])
    & (data["Year Built"] >= year_built_input[0])
    & (data["Year Built"] <= year_built_input[1])
    & (data["Vacancy %"] >= vacancy_rate[0])
]

# Show the map
st.header("Map")
m = folium.Map(location=(32.7157, -117.1611), zoom_start=12)
Draw(
    export=True,
    draw_options={"polyline": False, "marker": False, "circlemarker": False},
).add_to(m)

def popup(row):
    fields = [
        ("Property Name", row["Property Name"]),
        ("Property Address", row["Property Address"]),
        ("City", row["City"]),
        ("Zip", row["Zip"]),
        ("Units", row["Number Of Units"]),
        ("Costar Rating", row["Star Rating"]),
        ("Avg Asking/SF", row["Avg Asking/SF"]),
    ]

    details = [f"{label}: {value}" for label, value in fields if pd.notna(value)]

    return f'<div style="width: 200px; font-size: 14px">{details[0]}<br>{"<br>".join(details[1:])}</div>'


for i, row in filtered_data.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=popup(row),
    ).add_to(m)

# Display the map and get user interaction data
st_data = st_folium(m, width=1000)
# display the st_data to see the structure
# st.write(st_data)

# if there exits drawings, add a radio selector to choose which drawing to filter by:
if "all_drawings" in st_data and st_data["all_drawings"]:
    drawing_selector = st.radio(
        "Filter by Drawing",
        ["No Drawing Filter"]
        + [f"Drawing {i + 1}" for i in range(len(st_data["all_drawings"]))],
    )


# If the user has drawn a rectangle, filter the data accordingly
if (
    "bounds" in st_data
    and st_data["bounds"]
    and (
        "all_drawings" in st_data
        and st_data["all_drawings"]
        and drawing_selector != "No Drawing Filter"
    )
):
    bounds = st_data["bounds"]
    filtered_data = filtered_data[
        (filtered_data["Latitude"] > bounds["_southWest"]["lat"])
        & (filtered_data["Latitude"] < bounds["_northEast"]["lat"])
        & (filtered_data["Longitude"] > bounds["_southWest"]["lng"])
        & (filtered_data["Longitude"] < bounds["_northEast"]["lng"])
    ]

# Table view selector
view_selector = st.radio(
    "Table Views",
    ["All", "Unit Breakdown", "Financial Overview", "Property Management", "Sales Information", "Amenities"]
)

# if the user has selected a drawing, filter the data accordingly
if (
    "all_drawings" in st_data
    and st_data["all_drawings"]
    and drawing_selector != "No Drawing Filter"
):
    drawing = st_data["all_drawings"][int(drawing_selector.split(" ")[1]) - 1]
    polygon = Polygon(drawing["geometry"]["coordinates"][0])
    filtered_data = filter_data_within_bounds(filtered_data, polygon)

    # st.write(f"Number of properties in view: {len(filtered_data)}")

# Display the table based on the selected view
if view_selector == "All":
    st.dataframe(filtered_data, hide_index=True)
elif view_selector == "Unit Breakdown":
    unit_breakdown_columns = [
        "Property Name",
        "Property Address",
        "Number Of Units",
        "Number Of 1 Bedrooms Units",
        "Number Of 2 Bedrooms Units",
        "Number Of 3 Bedrooms Units",
        "Number Of 4 Bedrooms Units",
        "Number Of Studios Units",
    ]
    st.dataframe(filtered_data[unit_breakdown_columns], hide_index=True)
elif view_selector == "Financial Overview":
    financial_columns = [
        "Property Name",
        "Property Address",
        "Avg Asking/SF",
        "Avg Asking/Unit",
        "For Sale Price",
        "Cap Rate",
        "$Price/Unit",
    ]
    st.dataframe(filtered_data[financial_columns], hide_index=True)
elif view_selector == "Property Management":
    management_columns = [
        "Property Name",
        "Property Address",
        "Property Manager Name",
        "Property Manager Contact",
        "Property Manager Phone",
    ]
    st.dataframe(filtered_data[management_columns], hide_index=True)
elif view_selector == "Sales Information":
    sales_columns = [
        "Property Name",
        "Property Address",
        "Sale Company Name",
        "Sale Company Address",
        "Sale Company City State Zip",
        "Sale Company Phone",
        "Sale Company Fax",
        "Sale Company Contact",
    ]
    st.dataframe(filtered_data[sales_columns], hide_index=True)
elif view_selector == "Amenities":
    amenities_columns = [
        "Property Name",
        "Property Address",
        "Amenities",
        "Number Of Parking Spaces",
        "Number Of Elevators",
    ]
    st.dataframe(filtered_data[amenities_columns], hide_index=True)