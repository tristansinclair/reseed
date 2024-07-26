import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw, MarkerCluster
import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd


@st.cache_data
def filter_data_within_bounds(data, bounds):
    south_west_lat = bounds["_southWest"]["lat"]
    south_west_lng = bounds["_southWest"]["lng"]
    north_east_lat = bounds["_northEast"]["lat"]
    north_east_lng = bounds["_northEast"]["lng"]

    # Create masks for latitude and longitude
    lat_mask = (data["Latitude"] >= south_west_lat) & (
        data["Latitude"] <= north_east_lat
    )
    lng_mask = (data["Longitude"] >= south_west_lng) & (
        data["Longitude"] <= north_east_lng
    )

    # Apply masks to filter data
    return data[lat_mask & lng_mask]


@st.cache_data
def filter_data_within_polygon(data, polygon):
    gdf = gpd.GeoDataFrame(
        data, geometry=gpd.points_from_xy(data.Longitude, data.Latitude)
    )
    return gdf[gdf.within(polygon)]


@st.cache_data
def load_data():
    data = pd.read_csv(
        "costar/building_data/2024-07-22-23-47-05/costar_data_2024-07-22-23-47-05.csv"
    )
    # data.set_index(["Market Name", "Submarket Name", "Building Status", "Star Rating", "Number Of Units", "Year Built"], inplace=True)
    return data


# Initialize Streamlit app
st.set_page_config(page_title="ReSeed Costar", layout="wide")
st.title("San Diego Apartments")

data = load_data()

st.sidebar.header("Filter Options")
market_name = st.sidebar.selectbox("Market", data["Market Name"].unique())
#  add a submarket filter, allow multiple selection
submarket_name = st.sidebar.multiselect("Submarket", data["Submarket Name"].unique())
costar_ranking = st.sidebar.slider("Costar Ranking", 1, 5, (1, 5))
number_of_units = st.sidebar.slider("Number of Units", 0, 300, (0, 300))
year_built_input = st.sidebar.slider("Year Built", 1900, 2027, (1900, 2027), 1)
building_status = st.sidebar.multiselect(
    "Building Status", data["Building Status"].unique()
)

# Filter data based on sidebar inputs
query_str = (
    f"`Market Name` == @market_name & "
    f"`Star Rating` >= {costar_ranking[0]} & "
    f"`Star Rating` <= {costar_ranking[1]} & "
    f"`Number Of Units` >= {number_of_units[0]} & "
    f"`Number Of Units` <= {number_of_units[1]} & "
    f"`Year Built` >= {year_built_input[0]} & "
    f"`Year Built` <= {year_built_input[1]}"
)

# Apply the query to filter data
filtered_data = data.query(query_str)

# Apply additional filters if necessary
if building_status:
    filtered_data = filtered_data[
        filtered_data["Building Status"].isin(building_status)
    ]
if submarket_name:
    filtered_data = filtered_data[filtered_data["Submarket Name"].isin(submarket_name)]


# Show the map
m = folium.Map(location=[
    filtered_data["Latitude"].mean(),
    filtered_data["Longitude"].mean(),
], zoom_start=12)
Draw(
    export=True,
    draw_options={
        "polyline": False,
        "marker": False,
        "circlemarker": False,
        "circle": False,
    },
).add_to(m)


@st.cache_data
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


# for _, row in filtered_data.iterrows():
#     folium.Marker(
#         location=[row["Latitude"], row["Longitude"]],
#         popup=popup(row),
#     ).add_to(marker_cluster)


# Create a MarkerCluster with disableClusteringAtZoom set to the desired zoom level
marker_cluster = MarkerCluster(
    disableClusteringAtZoom=16  # Adjust this zoom level as needed
).add_to(m)

@st.cache_data
def create_markers():
    for _, row in data.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f'<div style="width: 200px; font-size: 14px">{row["Property Name"]}<br>{row["Property Address"]}<br>{row["City"]}<br>{row["Zip"]}<br>{row["Number Of Units"]}<br>{row["Star Rating"]}<br>{row["Avg Asking/SF"]}</div>',
        ).add_to(marker_cluster)

markers = create_markers()

# Display the map and get user interaction data
c1, c2 = st.columns([3, 2])  # Adjust column width ratio here
with c1:
    st_data = st_folium(m, use_container_width=True, height=500)

# Table view selector
view_selector = st.radio(
    "Table View",
    [
        "All",
        "Unit Breakdown",
        "Financial Overview",
        "Property Management",
        "Sales Information",
        "Amenities",
    ],
    horizontal=True,
    key="view_selector",
)

# Check if a border filter is active
border_filter_active = False
if "all_drawings" in st_data and st_data["all_drawings"]:
    border_selector = st.radio(
        "Border Filter",
        ["No Border Filter"]
        + [f"Border {i + 1}" for i in range(len(st_data["all_drawings"]))],
        horizontal=True,
        key="border_selector",
    )
    if border_selector != "No Border Filter":
        border = st_data["all_drawings"][int(border_selector.split(" ")[1]) - 1]
        polygon = Polygon(border["geometry"]["coordinates"][0])
        filtered_data = filter_data_within_polygon(filtered_data, polygon)
        border_filter_active = True

# If no border filter is active, filter data based on map bounds
if not border_filter_active and "bounds" in st_data and st_data["bounds"]:
    bounds = st_data["bounds"]
    filtered_data = filter_data_within_bounds(filtered_data, bounds)

# Calculate metrics based on the currently displayed data
total_units = filtered_data["Number Of Units"].sum()
avg_vacancy_rate = (
    filtered_data["Vacancy %"].mean() if "Vacancy %" in filtered_data.columns else None
)
avg_price_per_sf = (
    filtered_data["Avg Asking/SF"].mean()
    if "Avg Asking/SF" in filtered_data.columns
    else None
)
avg_price_per_unit = (
    filtered_data["Avg Asking/Unit"].mean()
    if "Avg Asking/Unit" in filtered_data.columns
    else None
)
avg_stories = (
    filtered_data["Number Of Stories"].mean()
    if "Number Of Stories" in filtered_data.columns
    else None
)

unit_type_distribution = (
    filtered_data[
        [
            "Number Of 1 Bedrooms Units",
            "Number Of 2 Bedrooms Units",
            "Number Of 3 Bedrooms Units",
            "Number Of 4 Bedrooms Units",
            "Number Of Studios Units",
        ]
    ]
    .sum()
    .to_dict()
    if "Number Of 1 Bedrooms Units" in filtered_data.columns
    else {}
)

# Display the metrics
with c2:
    st.metric(label="Total Units", value=total_units)
    if avg_vacancy_rate is not None:
        avg_vacancy_rate = format(avg_vacancy_rate, ".2f")
        st.metric(label="Average Vacancy Rate", value=avg_vacancy_rate)
    if avg_price_per_sf is not None:
        avg_price_per_sf = format(avg_price_per_sf, ".2f")
        st.metric(label="Average Price per Sq Ft", value=f"${avg_price_per_sf}")
    if avg_price_per_unit is not None:
        avg_price_per_unit = format(avg_price_per_unit, ".2f")
        st.metric(label="Average Price per Unit", value=f"${avg_price_per_unit}")
    if avg_stories is not None:
        avg_stories = format(avg_stories, ".2f")
        st.metric(label="Average Stories", value=avg_stories)

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
