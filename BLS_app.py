import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page configuration for a wider layout
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

# Sidebar Enhancements
st.sidebar.header("Filters")
st.sidebar.write("Use the filters below to customize the dashboard.")

# Dynamically assign defaults based on available options
available_options = data['series_name'].unique()
default_options = ["Civilian Employment",
                   "Civilian Unemployment",
                   "Unemployment Rate",
                   "Total Nonfarm Employment",
                   "Average Weekly Hours of All Employees",
                   "Average Hourly Earnings of All Employees"]

default_options = [opt for opt in default_options if opt in available_options]

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

st.sidebar.markdown(
    """
    ---
    **Data Source:** [Bureau of Labor Statistics](https://www.bls.gov/home.htm)
    """
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
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="color:#9C27B0;">US Labor Market</h1>
        <p style="color:gray;">Unemployment and Labor trends over the years. Data sourced from the U.S. Bureau of Labor Statistics.</p>
    </div>
    """,
    unsafe_allow_html=True
)



# Interactive Plot: Unemployment Rates
st.subheader("Unemployment Rates")
unemployment_data = filtered_data[filtered_data['series_id'] == 'LNS14000000']
fig_unemployment = go.Figure()

fig_unemployment.add_trace(
    go.Scatter(
        x=unemployment_data['date'],
        y=unemployment_data['value'],
        mode='lines+markers',
        name="Unemployment Rate",
        line=dict(color='blue'),
    )
)

fig_unemployment.update_layout(
    title="",
    xaxis_title="Date",
    yaxis_title="Unemployment Rate (%)",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig_unemployment, use_container_width=True)

# Interactive Plot: Total Nonfarm Workers
st.subheader("Number of Nonfarm Workers")
nonfarm_data = filtered_data[filtered_data['series_id'] == 'CES0000000001']
fig_nonfarm = go.Figure()

fig_nonfarm.add_trace(
    go.Scatter(
        x=nonfarm_data['date'],
        y=nonfarm_data['value'],
        mode='lines+markers',
        name="Total Nonfarm Workers",
        line=dict(color='green'),
    )
)

fig_nonfarm.update_layout(
    title="Total Nonfarm Workers Over Time",
    xaxis_title="Date",
    yaxis_title="Workers (in thousands)",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig_nonfarm, use_container_width=True)

# COVID-19's Impact
st.markdown("""
### COVID-19's Impact on the Labor Market
Wow! The impact of COVID-19 on the labor market is hard to miss. In 2020, unemployment rates skyrocketed, and millions of jobs seemed to disappear almost overnight.

Quarantines, businesses shutting down, and widespread illness left workplaces empty and people struggling. It was one of the most sudden and dramatic economic shocks in history.
""")

# Relationship between "Average Weekly Hours" and "Average Hourly Earnings"
st.subheader("Trends: Weekly Hours vs Hourly Earnings Over Time")

hours_data = data[data['series_id'] == 'CES0500000002']
earnings_data = data[data['series_id'] == 'CES0500000003']
merged_data = pd.merge(
    hours_data[['date', 'value']].rename(columns={'value': 'avg_weekly_hours'}),
    earnings_data[['date', 'value']].rename(columns={'value': 'avg_hourly_earnings'}),
    on='date'
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=merged_data['date'],
        y=merged_data['avg_weekly_hours'],
        mode='lines',
        name="Average Weekly Hours",
        line=dict(color='blue', width=2),
        hovertemplate="Date: %{x}<br>Weekly Hours: %{y:.2f}<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=merged_data['date'],
        y=merged_data['avg_hourly_earnings'],
        mode='lines',
        name="Average Hourly Earnings",
        line=dict(color='orange', width=2, dash='dot'),
        hovertemplate="Date: %{x}<br>Hourly Earnings: $%{y:.2f}<extra></extra>"
    )
)

fig.update_layout(
    title="Weekly Hours and Hourly Earnings Trends",
    xaxis=dict(
        title="Date",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False
    ),
    yaxis=dict(
        title="Value",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False
    ),
    legend=dict(
        title="Metrics",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True)

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
