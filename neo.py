
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

with st.expander("NASA NEO Data"):
    st.write("This plot shows the minimum and nominal (expected) distances for each Near Earth Object approach. " 
             "Points below the red dashed line indicate objects where the minimum possible approach is closer than the nominal approach.")

df = get_neo_data()

df['dist'] = pd.to_numeric(df['dist'])
df['dist_min'] = pd.to_numeric(df['dist_min'])

# Create a scatter plot
fig = px.scatter(df, x='dist_min', y='dist', 
                 hover_name='des', 
                 hover_data={
                     'des': False,
                     'cd': True,
                     'dist': ':.3f',
                     'dist_min': ':.3',
                     'v_rel': ':.3f',
                     'v_inf': ':.3f',
                     'h': ':.3f'
                 },
                 labels={'dist_min': 'Minimum Distance (AU)',
                         'dist': 'Nominal Distance (AU)',
                         'des': 'Designation',
                         'cd': 'Close Approach Date',
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

# Filter objects by approach date
st.subheader('Filter Objects by Approach Date')

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

# Display the raw data
if st.checkbox('Show raw data'):
    st.write(df)
