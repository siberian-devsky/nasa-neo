
from webbrowser import get
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

@st.cache_data
def get_neo_data():
    raw_data = requests.get("https://ssd-api.jpl.nasa.gov/cad.api?dist-max=0.05")
    j_data = raw_data.json()
    df = pd.DataFrame(j_data['data'], columns=j_data['fields'])
    return df

with st.expander(":orange[:material/satellite_alt:] NASA NEO Data - About"):
    st.write("This plot shows the minimum and nominal (expected) distances for each Near Earth Object approach.")
    st.write("Equal Distance Line")
    st.write(":green[===================]")
    st.write(":orange[Points above]:")
    st.write("&emsp;&emsp;Objects where the minimum possible approach is closer than the nominal approach. "
             "The vertical distance from the line represents the difference between the nominal and minimum distances, which is a measure of the prediction's uncertainty.")
    st.write(":orange[Points below]:")
    st.write("&emsp;&emsp;Objects where the minimum possible approach is farther than the nominal approach. "
             "This is a highly unlikely scenario for NEOs")

df = get_neo_data()

# convert distances to int and calculate uncertainty (delta)
df['dist'] = pd.to_numeric(df['dist'])
df['dist_min'] = pd.to_numeric(df['dist_min'])
df['dist_delta'] = (df['dist'] - df['dist_min'])

# convert and format close approach date
df['cd'] = pd.to_datetime(df['cd'])
df['cd_formatted'] = df['cd'].dt.strftime('%m-%d-%y')

# Filter objects by approach date
with st.expander(':green[:material/filter_alt:] Filter Objects by Approach Date'):
    min_date = df['cd'].min().date()
    max_date = df['cd'].max().date()

    start_date = st.date_input('Start Date', min_date)
    end_date = st.date_input('End Date', max_date)

    filtered_df = df[(df['cd'].dt.date >= start_date) & (df['cd'].dt.date <= end_date)]

    st.write(f"Number of objects in date range: {len(filtered_df)}")

    if not filtered_df.empty:
        st.write(filtered_df[['des', 'cd', 'dist', 'dist_min', 'v_rel']])
    else:
        st.write("No objects found in the selected date range.")

# Create a scatter plot
fig = px.scatter(filtered_df, x='dist_min', y='dist', color="dist_delta",
                 hover_name='des', 
                 hover_data={
                     'des': False,
                     'cd_formatted': True,
                     'dist': ':.5f',
                     'dist_min': ':.5f',
                     'dist_delta': ':.5f',
                     'v_rel': ':.5f',
                     'v_inf': ':.5f',
                     'h': ':.5f'
                 },
                 labels={'dist_min': 'Minimum Distance (AU)',
                         'dist': 'Nominal Distance (AU)',
                         'des': 'Designation',
                         'dist_delta': 'Delta (AU)',
                         'cd_formatted': 'Close Approach Date',
                         'v_rel': 'Relative Velocity (km/s)',
                         'v_inf': 'Infinity Velocity (km/s)',
                         'h': 'Absolute Magnitude'},
                 title='NEO Approach Distances')

# Add the equal distance line
fig.add_scatter(x=[0, df['dist'].max()], 
                y=[0, df['dist_min'].max()], 
                mode='lines', line=dict(color='green'),
                name='Equal Distance Line')

st.plotly_chart(fig)

# Display the raw data
if st.checkbox('Show raw data'):
    st.write(df)
