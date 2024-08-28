#1 .venv/bin/python

import http.client
from altair import Header
import streamlit as st
import base64
import os
import json
import geocoder as gc

from datetime import date
from dotenv import load_dotenv

# fetch env vars from, you guessed it, .env
load_dotenv()

# make columns
def display_cols(dimensions: list | int = None, header=None,
                 text=None, img=None, col_for_image=1):
    if dimensions is None:
        # default to cols of equal width
        dimensions = 3

    col1,col2,col3 = st.columns(dimensions)
    with col1:
        if header:
            st.subheader(Header)
            if img and col_for_image == 0:
                st.image(image, use_column_width='always')
        if text:
            st.write(text[0])

    with col2:
        if header:
            st.subheader(Header)
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

# get location data (IP based)
coords = gc.ip('me')
lat, lon = coords.latlng
address = coords.address
tz = coords.timezone

st.header(f':orange[:material/bedtime:] Lunar Phase: {address}', divider='orange')
with st.expander(':green[:material/location_on:] Location Data'):
    display_cols(3, text=[f'Lat: :green[{lat}]', f'Lon: :green[{lon}]', f'Timezone: :green[{tz}]'])
    # st.write(f'Lat: :green[{lat}]')
    # st.write(f'Lon: :green[{lon}]')
    # st.write(f'Timezone: :green[{tz}]')

moon_style = st.selectbox('Moon Style',
                          ['photo', 'sketch', 'shaded'],
                          index=None,
                          placeholder='Select a render option for the lunar image ...',
                          label_visibility='collapsed')

# override 'photo' to API expected value
if moon_style == 'photo':
    moon_style = 'default'

st.sidebar.subheader(':orange[:material/bedtime:] Lunar Phase')

app_id = os.getenv('ApplicationId')
app_secret = os.getenv('ApplicationSecret')

conn = http.client.HTTPSConnection('api.astronomyapi.com')

userpass = f'{app_id}:{app_secret}'
authString = base64.b64encode(userpass.encode()).decode()

# set payload date to today
today = date.today().isoformat()

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