import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Mapping of series IDs to human-readable names
series_names = {
    "LNS12000000": "Civilian Employment",
    "LNS13000000": "Civilian Unemployment",
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Total Nonfarm Employment",
    "CES0500000002": "Average Weekly Hours of All Employees",
    "CES0500000003": "Average Hourly Earnings of All Employees"
}

# Load data function with caching for performance
@st.cache_data
def load_data():
    return pd.read_csv('BLS_data.csv', parse_dates=['date'])

# Load the data
data = load_data()

# Add a column for human-readable series names
data['series_name'] = data['series_id'].map(series_names)
data['series_name'] = data['series_name'].fillna('Unknown Series')  # Handle unmapped series

# Debugging: Check unique values in series_name
st.sidebar.write("Available Series Options:", data['series_name'].unique())

# Dynamically assign defaults based on available options
available_options = data['series_name'].unique()
default_options = ["Total Nonfarm Employment", "Unemployment Rate"]

# Ensure default values exist in available options
default_options = [opt for opt in default_options if opt in available_options]

# Sidebar filters
st.sidebar.header("Filters")

# Multiselect for series names
selected_series_names = st.sidebar.multiselect(
    "Select Data Series:",
    options=available_options,
    default=default_options
)

# Filter by years
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(data['year'].min()),
    max_value=int(data['year'].max()),
    value=(2019, int(data['year'].max()))
)

# Map selected series names back to series IDs
selected_series_ids = [
    series_id for series_id, name in series_names.items() if name in selected_series_names
]

# Filter the data
filtered_data = data[
    (data['series_id'].isin(selected_series_ids)) &
    (data['year'].between(selected_years[0], selected_years[1]))
]

# Dashboard Title and Description
st.title("US Labor Market Dashboard")
st.write("""
This dashboard provides insights into key labor statistics from the Bureau of Labor Statistics (BLS).
Select the data series and time range below to explore trends and summaries.
""")

# Line Chart Visualization
st.subheader("Time Series Trends")
fig, ax = plt.subplots(figsize=(10, 6))
for series_id in selected_series_ids:
    subset = filtered_data[filtered_data['series_id'] == series_id]
    series_label = series_names.get(series_id, series_id)  # Get human-readable label
    ax.plot(subset['date'], subset['value'], label=series_label)

ax.set_xlabel("Date")
ax.set_ylabel("Value")
ax.legend(title="Series")
ax.grid(True)

st.pyplot(fig)

# Summary Statistics
st.subheader("Summary Statistics")
summary = filtered_data.groupby('series_name')['value'].describe()
st.dataframe(summary)

# Data Table
st.subheader("Filtered Data Table")
st.write(filtered_data)

# Download button for filtered data
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_bls_data.csv",
    mime="text/csv"
)
