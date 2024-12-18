import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="US Labor Market Dashboard", layout="wide")

# Header with Banner
st.markdown(
    """
    <div style="background-color:#4CAF50; padding:10px; border-radius:10px;">
        <h1 style="color:white; text-align:center;">US Labor Market Dashboard</h1>
        <p style="color:white; text-align:center;">
        Explore labor market trends with interactive visualizations and custom filters.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Filters
st.sidebar.header("Filters")

# Data Loading and Mapping
@st.cache_data
def load_data():
    return pd.read_csv('BLS_data.csv', parse_dates=['date'])

data = load_data()

# Series Mapping
series_names = {
    "LNS12000000": "Civilian Employment",
    "LNS13000000": "Civilian Unemployment",
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Total Nonfarm Employment",
    "CES0500000002": "Average Weekly Hours of All Employees",
    "CES0500000003": "Average Hourly Earnings of All Employees",
}
data['series_name'] = data['series_id'].map(series_names)

# Sidebar Multiselect
available_options = data['series_name'].unique()
selected_series_names = st.sidebar.multiselect(
    "Select Data Series:",
    options=available_options,
    default=["Unemployment Rate", "Total Nonfarm Employment"]
)

# Sidebar Date Range Slider
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(data['year'].min()),
    max_value=int(data['year'].max()),
    value=(2019, int(data['year'].max()))
)

# Filter Data
filtered_data = data[
    (data['series_name'].isin(selected_series_names)) &
    (data['year'].between(selected_years[0], selected_years[1]))
]

# Dashboard Content
st.subheader("Unemployment Rate Over Time")
unemployment_data = filtered_data[filtered_data['series_name'] == "Unemployment Rate"]

fig_unemployment = go.Figure()
fig_unemployment.add_trace(
    go.Scatter(
        x=unemployment_data['date'],
        y=unemployment_data['value'],
        mode='lines+markers',
        name="Unemployment Rate",
        line=dict(color='#007acc')
    )
)
fig_unemployment.update_layout(
    title="Unemployment Rate Over Time",
    xaxis_title="Date",
    yaxis_title="Rate (%)",
    template="plotly_white"
)
st.plotly_chart(fig_unemployment, use_container_width=True)

# Total Nonfarm Workers Plot
st.subheader("Total Nonfarm Workers Over Time")
nonfarm_data = filtered_data[filtered_data['series_name'] == "Total Nonfarm Employment"]

fig_nonfarm = go.Figure()
fig_nonfarm.add_trace(
    go.Scatter(
        x=nonfarm_data['date'],
        y=nonfarm_data['value'],
        mode='lines+markers',
        name="Total Nonfarm Workers",
        line=dict(color='#FFA500')
    )
)
fig_nonfarm.update_layout(
    title="Total Nonfarm Workers Over Time",
    xaxis_title="Date",
    yaxis_title="Workers (in thousands)",
    template="plotly_white"
)
st.plotly_chart(fig_nonfarm, use_container_width=True)

# Weekly Hours vs Hourly Earnings
st.subheader("Trends: Weekly Hours vs Hourly Earnings")
hours_data = data[data['series_id'] == 'CES0500000002']
earnings_data = data[data['series_id'] == 'CES0500000003']
merged_data = pd.merge(
    hours_data[['date', 'value']].rename(columns={'value': 'Weekly Hours'}),
    earnings_data[['date', 'value']].rename(columns={'value': 'Hourly Earnings'}),
    on='date'
)
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=merged_data['date'],
        y=merged_data['Weekly Hours'],
        fill='tozeroy',
        mode='lines',
        name="Weekly Hours",
        line=dict(color='blue')
    )
)
fig.add_trace(
    go.Scatter(
        x=merged_data['date'],
        y=merged_data['Hourly Earnings'],
        fill='tonexty',
        mode='lines',
        name="Hourly Earnings",
        line=dict(color='orange', dash='dot')
    )
)
fig.update_layout(
    title="Weekly Hours vs Hourly Earnings",
    xaxis_title="Date",
    yaxis_title="Value",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# Summary Statistics
st.subheader("Summary Statistics")
summary = filtered_data.groupby('series_name')['value'].describe()
st.dataframe(summary)

# Footer
st.markdown(
    """
    <hr style="border:1px solid gray;">
    <p style="text-align:center; color:gray;">
    Built with ❤️ using Streamlit | Data sourced from the Bureau of Labor Statistics
    </p>
    """,
    unsafe_allow_html=True
)
