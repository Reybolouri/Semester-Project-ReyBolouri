
import streamlit as st
#st.write("Hello World")
import pandas as pd
import os


st.title("U.S. Labor Statistics")
st.markdown("### Visualizing trends in employment, unemployment, and earnings data")


DATA_FILE = "BLS_data.csv"

df = pd.read_csv(DATA_FILE)


series_names = {
    "LNS12000000": "Civilian Employment",
    "LNS13000000": "Civilian Unemployment",
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Total Nonfarm Employment",
    "CES0500000002": "Average Weekly Hours of All Employees",
    "CES0500000003": "Average Hourly Earnings of All Employees"
}

# Replace series IDs with user-friendly names
df['series_name'] = df['series_id'].map(series_names)

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_series = st.sidebar.multiselect(
    "Select Data Series",
    options=df['series_name'].unique(),
    default=df["Average Weekly Hours of All Employees", "Average Hourly Earnings of All Employees"].unique()
)

start_date = st.sidebar.date_input("Start Date", value=df['date'].min())
end_date = st.sidebar.date_input("End Date", value=df['date'].max())

# Filter Data
filtered_data = df[
    (df['series_name'].isin(selected_series)) &
    (df['date'] >= pd.Timestamp(start_date)) &
    (df['date'] <= pd.Timestamp(end_date))
]

# Display Filtered Data
st.write("### Filtered Data")
st.dataframe(filtered_data)

# Visualization
st.write("### Data Trends Over Time")
for series in selected_series:
    series_data = filtered_data[filtered_data['series_name'] == series]
    st.line_chart(series_data.set_index('date')['value'], use_container_width=True)
