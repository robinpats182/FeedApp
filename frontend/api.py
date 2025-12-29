import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/"

def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
