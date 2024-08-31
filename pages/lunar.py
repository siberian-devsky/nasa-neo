#1 .venv/bin/python

import streamlit as st
import http.client
import base64
import json
import pytz
from datetime import datetime as dt

from helpers.helpers import get_client_location

from dotenv import load_dotenv

# fetch env vars from, you guessed it, .env
load_dotenv()

# found you!
client_loc = get_client_location()
city_state = f"{client_loc['city']}, {client_loc['region']}"
city_state_country = f"{client_loc['city']}, {client_loc['region']}, {client_loc['country']}"
timezone = client_loc['timezone']
lat = client_loc['latitude']
lon = client_loc['longitude']

# construct time data
pretty_date = dt.now().astimezone(pytz.timezone(timezone)).strftime("%a %b %d %Y")  # display
today = dt.now().astimezone(pytz.timezone(timezone)).strftime('%Y-%m-%d')  # api payload
cur_time = dt.now().astimezone(pytz.timezone(timezone)).strftime('%H:%M:%S')

# make columns
def display_cols(dimensions: list | int = None, header=None,
                 text=None, img=None, col_for_image=1):
    if dimensions is None:
        # default to cols of equal width
        dimensions = 3

    col1,col2,col3 = st.columns(dimensions)
    with col1:
        if header:
            st.subheader(header)
            if img and col_for_image == 0:
                st.image(image, use_column_width='always')
        if text:
            st.write(text[0])

    with col2:
        if header:
            st.subheader(header)
        if img and col_for_image == 1:
            st.image(image, use_column_width='always')
        if text:
            st.write(text[1])

    with col3:
        if header:
            st.subheader(header)
        if img and col_for_image == 2:
            st.image(image, use_column_width='always')
        if text:
            st.write(text[2])

st.header(f':orange[:material/bedtime:] Lunar Phase: {city_state_country}', divider='orange')

moon_style = st.selectbox(':orange[Moon Style]',
                          ['photo', 'sketch', 'shaded'],
                          index=0)

# override 'photo' to API expected value
if moon_style == 'photo':
    moon_style = 'default'

st.sidebar.subheader(':orange[:material/bedtime:] Lunar Phase')
with st.sidebar.expander(':green[:material/location_on:] Location Data'):
    st.markdown(f':orange[{pretty_date} - {cur_time}]')
    st.write(f':orange[{timezone}]')
    st.write(f':orange[{lat}]')
    st.write(f':orange[{lon}]')

app_id = st.secrets['ApplicationId']
app_secret = st.secrets['ApplicationSecret']

conn = http.client.HTTPSConnection('api.astronomyapi.com')

userpass = f'{app_id}:{app_secret}'
authString = base64.b64encode(userpass.encode()).decode()

# payload as a Python dictionary
payload_dict = {
    'style': {
        'moonStyle': moon_style,
        'backgroundStyle': 'stars',
        'backgroundColor': 'DimGray',
        'headingColor': '#45f792',
        'textColor': '#45f792'
    },
    'observer': {
        'latitude': lat,
        'longitude': lon,
        'date': today
    },
    'view': {
        'type': 'landscape-simple',
        'parameters': {}
    }
}

# Convert the dictionary to a JSON string and add auth header
payload = json.dumps(payload_dict)
headers = { 'Authorization': f'Basic {authString}' }

conn.request('POST', '/api/v2/studio/moon-phase', payload, headers)
res = conn.getresponse()

if res.status == 200:
    data = res.read()
    decoded = data.decode('utf-8')
    json_data = json.loads(decoded)
    
    image = json_data['data']['imageUrl']
    display_cols(dimensions=[0.15, 0.7, 0.15], img=image, col_for_image=1)