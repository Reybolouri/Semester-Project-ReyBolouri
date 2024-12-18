import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
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

# Interactive Line Chart Visualization with Plotly
st.subheader("Interactive Time Series Trends")
# Create an empty figure
fig = go.Figure()

# Add traces for each selected series
for series_id in selected_series_ids:
    subset = filtered_data[filtered_data['series_id'] == series_id]
    series_label = series_names.get(series_id, series_id)  # Get human-readable label
    
    # Add a line trace for the series
    fig.add_trace(
        go.Scatter(
            x=subset['date'],
            y=subset['value'],
            mode='lines',
            name=series_label
        )
    )

# Update layout for better aesthetics
fig.update_layout(
    title="Time Series Trends",
    xaxis_title="Date",
    yaxis_title="Value",
    legend_title="Series",
    hovermode="x unified",
    template="plotly_white"
)

# Display the Plotly figure in Streamlit
st.plotly_chart(fig, use_container_width=True)


# Relationship between "Average Weekly Hours" and "Average Hourly Earnings" over time
st.subheader("Trends: Weekly Hours vs Hourly Earnings Over Time")

# Filter data for the two relevant series
hours_data = data[data['series_id'] == 'CES0500000002']
earnings_data = data[data['series_id'] == 'CES0500000003']

# Merge the two datasets on the date
merged_data = pd.merge(
    hours_data[['date', 'value']].rename(columns={'value': 'avg_weekly_hours'}),
    earnings_data[['date', 'value']].rename(columns={'value': 'avg_hourly_earnings'}),
    on='date'
)

# Create the dual-axis time series plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot "Average Weekly Hours" on the left y-axis
color = 'tab:blue'
ax1.set_xlabel("Date")
ax1.set_ylabel("Average Weekly Hours", color=color)
ax1.plot(merged_data['date'], merged_data['avg_weekly_hours'], color=color, label="Weekly Hours")
ax1.tick_params(axis='y', labelcolor=color)

# Plot "Average Hourly Earnings" on the right y-axis
ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis
color = 'tab:orange'
ax2.set_ylabel("Average Hourly Earnings ($)", color=color)
ax2.plot(merged_data['date'], merged_data['avg_hourly_earnings'], color=color, label="Hourly Earnings")
ax2.tick_params(axis='y', labelcolor=color)

# Add a title and grid
fig.suptitle("Average Weekly Hours vs Average Hourly Earnings Over Time")
ax1.grid(True)

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
