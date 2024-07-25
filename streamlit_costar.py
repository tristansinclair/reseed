import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
from shapely.geometry import Point, Polygon

def filter_data_within_bounds(data, bounds):
    south_west = bounds["_southWest"]
    north_east = bounds["_northEast"]
    return data[
        (data["Latitude"] >= south_west["lat"]) &
        (data["Latitude"] <= north_east["lat"]) &
        (data["Longitude"] >= south_west["lng"]) &
        (data["Longitude"] <= north_east["lng"])
    ]

def filter_data_within_polygon(data, polygon):
    def is_within_polygon(lat, lon, polygon):
        point = Point(lon, lat)
        return polygon.contains(point)

    return data[data.apply(lambda row: is_within_polygon(row["Latitude"], row["Longitude"], polygon), axis=1)]

# Load data
data = pd.read_csv("costar/building_data/2024-07-22-23-47-05/costar_data_2024-07-22-23-47-05.csv")

# Initialize Streamlit app
st.set_page_config(page_title="ReSeed Costar", layout="wide")
st.title("San Diego Apartments")

st.sidebar.header("Filter Options")
costar_ranking = st.sidebar.slider("Costar Ranking", 1, 5, (4, 5))
number_of_units = st.sidebar.slider("Number of Units", 0, 300, (0, 300))
year_built_input = st.sidebar.slider("Year Built", 1900, 2027, (1900, 2027), 1)
building_status = st.sidebar.multiselect("Building Status", data["Building Status"].unique())

# Filter data based on sidebar inputs
filtered_data = data[
    (data["Star Rating"] >= costar_ranking[0]) &
    (data["Star Rating"] <= costar_ranking[1]) &
    (data["Number Of Units"] >= number_of_units[0]) &
    (data["Number Of Units"] <= number_of_units[1]) &
    (data["Year Built"] >= year_built_input[0]) &
    (data["Year Built"] <= year_built_input[1])
]

if building_status:
    filtered_data = filtered_data[filtered_data["Building Status"].isin(building_status)]

# Show the map
m = folium.Map(location=(32.7157, -117.1611), zoom_start=12)
Draw(export=True, draw_options={"polyline": False, "marker": False, "circlemarker": False, "circle": False}).add_to(m)

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
c1, c2 = st.columns([3, 2])  # Adjust column width ratio here
with c1:
    st_data = st_folium(m, use_container_width=True, height=500)

# Table view selector
view_selector = st.radio(
    "Table View",
    ["All", "Unit Breakdown", "Financial Overview", "Property Management", "Sales Information", "Amenities"],
    horizontal=True,
    key="view_selector"
)

# Check if a border filter is active
border_filter_active = False
if "all_drawings" in st_data and st_data["all_drawings"]:
    border_selector = st.radio(
        "Border Filter",
        ["No Border Filter"] + [f"Border {i + 1}" for i in range(len(st_data["all_drawings"]))],
        horizontal=True,
        key="border_selector"
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
avg_vacancy_rate = filtered_data["Vacancy %"].mean() if "Vacancy %" in filtered_data.columns else None
avg_price_per_sf = filtered_data["Avg Asking/SF"].mean() if "Avg Asking/SF" in filtered_data.columns else None
avg_price_per_unit = filtered_data["Avg Asking/Unit"].mean() if "Avg Asking/Unit" in filtered_data.columns else None
# total_stories = filtered_data["Number Of Stories"].sum() if "Number Of Stories" in filtered_data.columns else None
avg_stories = filtered_data["Number Of Stories"].mean() if "Number Of Stories" in filtered_data.columns else None

unit_type_distribution = filtered_data[[
    "Number Of 1 Bedrooms Units",
    "Number Of 2 Bedrooms Units",
    "Number Of 3 Bedrooms Units",
    "Number Of 4 Bedrooms Units",
    "Number Of Studios Units"
]].sum().to_dict() if "Number Of 1 Bedrooms Units" in filtered_data.columns else {}

# Display the metrics
with c2:
    # st.header("Metrics")
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
    # if total_stories is not None:
    #     st.metric(label="Total Stories", value=total_stories)
    if avg_stories is not None:
        avg_stories = format(avg_stories, ".2f")
        st.metric(label="Average Stories", value=avg_stories)

    # if unit_type_distribution:
    #     # st.header("Distribution of Unit Types")

    #     # Prepare data for Vega-Lite chart
    #     unit_distribution_df = pd.DataFrame(list(unit_type_distribution.items()), columns=['Unit Type', 'Count'])

    #     pie_chart_spec = {
    #         "mark": {"type": "arc", "tooltip": True},
    #         "encoding": {
    #             "theta": {"field": "Count", "type": "quantitative"},
    #             "color": {"field": "Unit Type", "type": "nominal"},
    #             "tooltip": [{"field": "Unit Type", "type": "nominal"}, {"field": "Count", "type": "quantitative"}]
    #         },
    #         "width": 200,
    #         "height": 200
    #     }

    #     st.vega_lite_chart(unit_distribution_df, pie_chart_spec, use_container_width=True)

# Display the table based on the selected view
if view_selector == "All":
    st.dataframe(filtered_data, hide_index=True)
elif view_selector == "Unit Breakdown":
    unit_breakdown_columns = [
        "Property Name", "Property Address", "Number Of Units",
        "Number Of 1 Bedrooms Units", "Number Of 2 Bedrooms Units",
        "Number Of 3 Bedrooms Units", "Number Of 4 Bedrooms Units",
        "Number Of Studios Units"
    ]
    st.dataframe(filtered_data[unit_breakdown_columns], hide_index=True)
elif view_selector == "Financial Overview":
    financial_columns = [
        "Property Name", "Property Address", "Avg Asking/SF",
        "Avg Asking/Unit", "For Sale Price", "Cap Rate", "$Price/Unit"
    ]
    st.dataframe(filtered_data[financial_columns], hide_index=True)
elif view_selector == "Property Management":
    management_columns = [
        "Property Name", "Property Address", "Property Manager Name",
        "Property Manager Contact", "Property Manager Phone"
    ]
    st.dataframe(filtered_data[management_columns], hide_index=True)
elif view_selector == "Sales Information":
    sales_columns = [
        "Property Name", "Property Address", "Sale Company Name",
        "Sale Company Address", "Sale Company City State Zip",
        "Sale Company Phone", "Sale Company Fax", "Sale Company Contact"
    ]
    st.dataframe(filtered_data[sales_columns], hide_index=True)
elif view_selector == "Amenities":
    amenities_columns = [
        "Property Name", "Property Address", "Amenities",
        "Number Of Parking Spaces", "Number Of Elevators"
    ]
    st.dataframe(filtered_data[amenities_columns], hide_index=True)
