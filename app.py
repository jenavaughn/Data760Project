# cd Desktop\Data760ProjectTest\Streamlit_Project
# python -m streamlit run app.py


# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Data 760 Project")

st.title("Marine Life Fishery Populations")

# --- Load CSV data ---
df = pd.read_csv('Biomass2013-2023.csv')

# Map display label → (lat, lon, source_code)
source_locations = {
    "Alaska Ecosystem Complex": (56.9449, -166.4648, "AlaskaEco"),
    "Atlantic Highly Migratory": (40.561778184679234, -71.09441053906247, "AtlanticHM"),
    "California Current": (42.34227629852246, -126.77312147656247, "California"),
    "Gulf of Mexico": (25.82828969709998, -90.40837538281247, "GulfMexico"),
    "Northeast Shelf": (37.815177624787175, -73.75310194531247, "NortheastShelf"),
    "Pacific Highly Migratory": (34.98834635945323, -124.15837538281247, "PacificHM"),
    "Pacific Islands Ecosystem Complex": (8.571583940486, -177.8936717411194, "PacificEco")
}

# Initial selected display source (none)
clicked_display_label = st.session_state.get("clicked_source_display", None)

# Build the map centered in the US
m = folium.Map(location=[34.98834635945323, -124.15837538281247], zoom_start=3, tiles="Esri.WorldImagery", key="initial_map")

# Add markers with display labels
for display_label, (lat, lon, source_code) in source_locations.items():
    folium.Marker(
        location=[lat, lon],
        tooltip=display_label,
        popup=display_label,
    ).add_to(m)

st.subheader("Select Fishery Location by Clicking a Marker")

# Show the map and get the last clicked popup label
map_data = st_folium(m, width=1000, height=600)
last_popup = map_data.get("last_object_clicked_popup")

if last_popup:
    st.session_state["clicked_source_display"] = last_popup
    clicked_display_label = last_popup

if clicked_display_label:
    st.success(f"Showing data for source: {clicked_display_label}")

    # Lookup the source code for filtering
    source_code = source_locations[clicked_display_label][2]

    # Filter the DataFrame by source code
    source_df = df[df["source"] == source_code]

    if source_df.empty:
        st.warning(f"No data available for source: {clicked_display_label}")
    else:
        # Ensure 'Assessment Year' is numeric and drop NaNs
        source_df["Assessment Year"] = pd.to_numeric(source_df["Assessment Year"], errors='coerce')
        source_df = source_df.dropna(subset=["Assessment Year"])

        # Species filter inside expander
        species_options = source_df["Stock Name"].unique()
        with st.expander("Select Stock Name(s)"):
            selected_stocks = st.multiselect("Stocks", species_options, default=list(species_options))

        min_year = int(source_df["Assessment Year"].min())
        max_year = int(source_df["Assessment Year"].max())

        year_range = st.slider("Select Assessment Year Range", min_year, max_year, (min_year, max_year))

        # Apply filters
        filtered_df = source_df[
            (source_df["Stock Name"].isin(selected_stocks)) &
            (source_df["Assessment Year"] >= year_range[0]) &
            (source_df["Assessment Year"] <= year_range[1])
        ]

        st.subheader("Estimated Biomass Over Time")
        fig = px.line(
            filtered_df,
            x="Assessment Year",
            y="Estimated B (Metric Tons)",
            color="Stock Name",
            markers=True,
            labels={
                "Assessment Year": "Year",
                "Estimated B (Metric Tons)": "Biomass (Metric Tons)",
                "Stock Name": "Stock"
            }
        )
        fig.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Click a marker on the map to select a location.")
