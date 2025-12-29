import streamlit as st

def is_authenticated():
    return "token" in st.session_state

def logout():
    st.session_state.clear()
    st.rerun()
