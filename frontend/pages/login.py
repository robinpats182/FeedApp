import streamlit as st
import requests
from api import API_URL
import time


# Redirect if already logged in
if "token" in st.session_state:
    st.warning("You are already logged in. Redirecting to feed...")
    time.sleep(2)
    st.switch_page("pages/feed.py")

st.title("🔐 Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

login_clicked = st.button("Login")
register_clicked = st.button("Register Now")

if login_clicked:
    response = requests.post(
        f"{API_URL}/auth/jwt/login",
        data={
            "username": email,
            "password": password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        st.session_state["token"] = response.json()["access_token"]

        st.success("Login successful 🎉")
        st.switch_page("pages/feed.py")

        # ✅ Correct for new Streamlit versions
        st.rerun()
    else:
        st.error(response.text)

if register_clicked:
    st.success("Hold tight. Redirecting to register page...")
    time.sleep(2)
    st.switch_page("pages/register.py")
    

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