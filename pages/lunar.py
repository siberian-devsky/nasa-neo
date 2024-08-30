#1 .venv/bin/python

import streamlit as st
import http.client
import base64
import os
import json
import geocoder as gc

import pytz
from datetime import date, datetime as dt

from dotenv import load_dotenv

# fetch env vars from, you guessed it, .env
load_dotenv()

# localize TZ by IP
def get_time_and_space():
    # get location data (IP based)
    coords = gc.ip('me')
    lat, lon = coords.latlng
    tz = pytz.timezone(coords.timezone)

    return {
        'pretty_date': dt.now().astimezone(tz).strftime("%a %b %d %Y"),  # display
        'today': dt.now().astimezone(tz).strftime('%Y-%m-%d'), # api payload
        'lat': lat,
        'lon': lon,
        'address': coords.address,
        'tz': tz,
    }


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

spacetime = get_time_and_space()

st.header(f':orange[:material/bedtime:] Lunar Phase: {spacetime['address']}', divider='orange')

moon_style = st.selectbox('Moon Style',
                          ['photo', 'sketch', 'shaded'],
                          index=0)

# override 'photo' to API expected value
if moon_style == 'photo':
    moon_style = 'default'

st.sidebar.subheader(':orange[:material/bedtime:] Lunar Phase')
with st.sidebar.expander(':green[:material/location_on:] Location Data'):
    st.write(f'Date: :green[{spacetime['pretty_date']}]')
    st.write(f'Zone: :green[{spacetime['tz']}]')
    st.write(f'Lat: :green[{spacetime['lat']}]')
    st.write(f'Lon: :green[{spacetime['lon']}]')

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
        'latitude': spacetime['lat'],
        'longitude': spacetime['lon'],
        'date': spacetime['today']
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