import streamlit as st
import requests
from api import API_URL, get_headers
import time

# Redirect if not logged in
if "token" not in st.session_state:
    st.error("You need to login first. Redirecting to login page...")
    time.sleep(4)
    st.switch_page("pages/login.py")

st.title("📤 Upload")

file = st.file_uploader("Image / Video", type=["jpg", "png", "mp4", "mov"])
caption = st.text_input("Caption")

if st.button("Upload"):
    if not file:
        st.warning("Select a file")
        st.stop()
    
    response = requests.post(
        f"{API_URL}/upload",
        headers=get_headers(),
        files={"file": (file.name, file, file.type)},
        data={"caption": caption},
    )
    
    st.success("Uploaded successfully....")
    time.sleep(2)
    st.switch_page("pages/feed.py")


# Custom sidebar logic
is_logged_in = "token" in st.session_state
with st.sidebar:
    st.markdown("---")    
    if is_logged_in:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.success("Logging out...")
            import time
            time.sleep(1)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        st.markdown("---")
        if st.button("🔐 Login", use_container_width=True):
            st.switch_page("pages/login.py")