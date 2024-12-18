import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="US Labor Market Dashboard", layout="wide")

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

# Sidebar: Enhanced Design
st.sidebar.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa; /* Light background */
        padding: 10px;
        border-radius: 8px;
    }
    .sidebar h3 {
        color: #4CAF50; /* Green accent for headings */
        margin-bottom: 5px;
    }
    .sidebar p {
        color: #6c757d; /* Subtle gray text */
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Content
st.sidebar.header("Filters")
st.sidebar.write("**Customize the data displayed below:**")

# Multiselect for Data Series
selected_series_names = st.sidebar.multiselect(
    "Select Data Series:",
    options=data['series_name'].unique(),
    default=[
        "Civilian Employment", 
        "Unemployment Rate",
        "Total Nonfarm Employment",
        "Average Weekly Hours of All Employees",
        "Average Hourly Earnings of All Employees"
    ]
)

# Year Range Selector
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(data['year'].min()),
    max_value=int(data['year'].max()),
    value=(2019, int(data['year'].max()))
)

# Sidebar Footer with a Note
st.sidebar.markdown(
    """
    ---
    <p style="font-size: 12px; color: #6c757d;">
    Use the filters above to explore trends in the US labor market. 
    Data sourced from the Bureau of Labor Statistics.
    </p>
    """,
    unsafe_allow_html=True
)


# Filter the data based on user input
filtered_data = data[
    (data['series_name'].isin(selected_series_names)) &
    (data['year'].between(selected_years[0], selected_years[1]))
]

# Dashboard Title and Introduction
st.title("US Labor Market Dashboard")
st.write("""
Explore key labor market trends with interactive visualizations. 
Use the filters in the sidebar to customize the data displayed.
""")

# Section: Visualizations
st.subheader("Key Trends Over Time")

# Unemployment Rate Visualization
if "Unemployment Rate" in selected_series_names:
    st.write("### Unemployment Rate Over Time")
    unemployment_data = filtered_data[filtered_data['series_name'] == "Unemployment Rate"]
    fig_unemployment = go.Figure()
    fig_unemployment.add_trace(
        go.Scatter(
            x=unemployment_data['date'],
            y=unemployment_data['value'],
            mode='lines+markers',
            name="Unemployment Rate",
            line=dict(color='blue')
        )
    )
    fig_unemployment.update_layout(
        title="Unemployment Rate Over Time",
        xaxis_title="Date",
        yaxis_title="Rate (%)",
        template="simple_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_unemployment, use_container_width=True)

# Total Nonfarm Workers Visualization
if "Total Nonfarm Employment" in selected_series_names:
    st.write("### Total Nonfarm Employment Over Time")
    nonfarm_data = filtered_data[filtered_data['series_name'] == "Total Nonfarm Employment"]
    fig_nonfarm = go.Figure()
    fig_nonfarm.add_trace(
        go.Scatter(
            x=nonfarm_data['date'],
            y=nonfarm_data['value'],
            mode='lines+markers',
            name="Total Nonfarm Workers",
            line=dict(color='green')
        )
    )
    fig_nonfarm.update_layout(
        title="Total Nonfarm Workers Over Time",
        xaxis_title="Date",
        yaxis_title="Workers (in thousands)",
        template="simple_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_nonfarm, use_container_width=True)

# Weekly Hours vs Hourly Earnings
if {"Average Weekly Hours of All Employees", "Average Hourly Earnings of All Employees"}.intersection(selected_series_names):
    st.write("### Weekly Hours vs Hourly Earnings")
    hours_data = filtered_data[filtered_data['series_name'] == "Average Weekly Hours of All Employees"]
    earnings_data = filtered_data[filtered_data['series_name'] == "Average Hourly Earnings of All Employees"]
    merged_data = pd.merge(
        hours_data[['date', 'value']].rename(columns={'value': 'Weekly Hours'}),
        earnings_data[['date', 'value']].rename(columns={'value': 'Hourly Earnings'}),
        on='date'
    )
    fig_hours_vs_earnings = go.Figure()
    fig_hours_vs_earnings.add_trace(
        go.Scatter(
            x=merged_data['date'],
            y=merged_data['Weekly Hours'],
            mode='lines',
            name="Weekly Hours",
            line=dict(color='blue')
        )
    )
    fig_hours_vs_earnings.add_trace(
        go.Scatter(
            x=merged_data['date'],
            y=merged_data['Hourly Earnings'],
            mode='lines',
            name="Hourly Earnings",
            line=dict(color='orange', dash='dot')
        )
    )
    fig_hours_vs_earnings.update_layout(
        title="Weekly Hours vs Hourly Earnings",
        xaxis_title="Date",
        yaxis_title="Value",
        template="simple_white"
    )
    st.plotly_chart(fig_hours_vs_earnings, use_container_width=True)

# Summary Statistics
st.subheader("Summary Statistics")
summary = filtered_data.groupby('series_name')['value'].describe()
st.dataframe(summary)

# Download Filtered Data
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_bls_data.csv",
    mime="text/csv"
)

# Footer
st.markdown("""
---
 Data sourced from the Bureau of Labor Statistics.https://data.bls.gov/toppicks?survey=bls 
""")
