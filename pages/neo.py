#! .venv/bin/python3

import streamlit as st
import pandas as pd
import requests
import plotly.express as px

@st.cache_data
def get_neo_data():
    two_years = str(365*2)
    raw_data = requests.get("https://ssd-api.jpl.nasa.gov/cad.api?", params={"date-max": f"+{two_years}"})
    # grab the url for th description
    data_source = raw_data.request.url
    j_data = raw_data.json()
    df = pd.DataFrame(j_data['data'], columns=j_data['fields'])
    return df, data_source

df, data_source = get_neo_data()

st.header(":orange[:material/satellite_alt:] NASA NEO Data", divider="orange")
st.sidebar.subheader(":orange[:material/satellite_alt:] Near Earth Objects")

with st.expander(":blue[:material/newsmode:] About"):
    st.write(f"Data source: {data_source}")
    st.write("This plot shows the minimum and nominal (expected) distances for each " 
             "Near Earth Object approach for the next two years.")
    st.write("Equal Distance Line")
    st.write(":green[===================]")
    st.write(":orange[Points above]:")
    st.write("&emsp;&emsp;Objects where the minimum possible approach is closer than the nominal approach. "
             "The vertical distance from the line represents the difference between the nominal and minimum distances, which is a measure of the prediction's uncertainty.")
    st.write(":orange[Points below]:")
    st.write("&emsp;&emsp;Objects where the minimum possible approach is farther than the nominal approach. "
             "This is a highly unlikely scenario for NEOs")

# convert distances to int and calculate uncertainty (delta)
df['dist'] = pd.to_numeric(df['dist'])
df['dist_min'] = pd.to_numeric(df['dist_min'])
df['dist_delta'] = (df['dist'] - df['dist_min'])

# convert and format close approach date
df['cd'] = pd.to_datetime(df['cd'])
df['cd_formatted'] = df['cd'].dt.strftime('%m-%d-%y %H:%M')

# Filters
# st.subheader(':green[:material/filter_alt:] Filters')
with st.expander(':green[:material/filter_alt:] Filters'):
    # date of closest approach
    st.subheader(':orange[:material/date_range:] Approach Date')
    min_date = df['cd'].min().date()
    max_date = df['cd'].max().date()

    start_date = st.date_input('Start Date', min_date)
    end_date = st.date_input('End Date', max_date)

    # distance range AU
    st.subheader(":orange[:material/radar:] Closest Approach (AU)")
    min_au, max_au = st.select_slider("Distance", 
                                      options=[x/1000 for x in range(0, 61, 1)],
                                      value=(0.00, 0.05))
    
    # apply filters
    filtered_df = df[(df['cd'].dt.date >= start_date) & (df['cd'].dt.date <= end_date) &
                     (df['dist_min'] >= min_au) & (df['dist_min'] <= max_au)]
    
    # Create a boolean mask for the rows that were filtered out
    filtered_out_mask = ~((df['cd'].dt.date >= start_date) & (df['cd'].dt.date <= end_date) &
                          (df['dist_min'] >= min_au) & (df['dist_min'] <= max_au))

    # Use the mask to get the filtered out rows
    filtered_out_df = df[filtered_out_mask]

    st.write(f"Graphing :orange[{len(filtered_df)}] / :orange[{len(df)}] items")
    
    # st.write(f"Total objects returned from API: {len(df)}")
    # st.write(f"Number of objects filtered out: {len(df) - len(filtered_df)}")
    
    # display filtered out data
    if st.checkbox('Show filtered out data'):
        st.write(f"Items that were filtered out ({len(df) - len(filtered_df)})")
        st.write(filtered_out_df)

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
                mode='lines', line=dict(color='orange'),
                name='Equal Distance Line')

st.plotly_chart(fig)

# Display the raw data
if st.checkbox('Show raw data'):
    st.write(df)
