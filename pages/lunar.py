#1 .venv/bin/python

import streamlit as st
import base64
import os

userpass = os.getenv()  # "applicationId:applicationSecret"
authString = base64.b64encode(userpass.encode()).decode()

st.header(":orange[:material/bedtime:] Lunar Phase")
st.sidebar.subheader(":orange[:material/bedtime:] Lunar Phase")