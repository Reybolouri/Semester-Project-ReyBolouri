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
@st.cache_data
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
# Filter by years
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(data['year'].min()),
    max_value=int(data['year'].max()),
    value=(2019, int(data['year'].max()))
)
# Filter the data
filtered_data = data[
    (data['series_id'].isin(selected_series_ids)) &
    (data['year'].between(selected_years[0], selected_years[1]))
]
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