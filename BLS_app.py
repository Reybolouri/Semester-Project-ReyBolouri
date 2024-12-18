import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


series_names = {
    "LNS12000000": "Civilian Employment",
    "LNS13000000": "Civilian Unemployment",
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Total Nonfarm Employment",
    "CES0500000002": "Average Weekly Hours of All Employees",
    "CES0500000003": "Average Hourly Earnings of All Employees"
}
# Load data
@st.cache
def load_data():
    return pd.read_csv('BLS_data.csv', parse_dates=['date'])

data = load_data()

# Add a column for human-readable series names
data['series_name'] = data['series_id'].map(series_names)
data['series_name'].fillna('Unknown Series', inplace=True)


st.title("US Labor Statistics Dashboard")
st.write("""
This dashboard provides some visualization  of labor statistics released by the Bureau of Labor Statistics (BLS). 
Select filters below to explore features like employment, unemployment, and wages over time.
""")


# Sidebar filters
st.sidebar.header("Filters")
selected_series = st.sidebar.multiselect(
    "Select Data Series:",
    options=data['series_id'].unique(),
    default=["Total Nonfarm Employment", "Unemployment Rate"]
)

# Map selected series names back to series IDs
selected_series_ids = [
    series_id for series_id, name in series_names.items() if name in selected_series_names
]
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(data['year'].min()),
    max_value=int(data['year'].max()),
    value=(2019, int(data['year'].max()))
)
