import streamlit as st
import requests
from api import API_URL
import time


# Redirect if already logged in
if "token" in st.session_state:
    st.warning("You are already logged in. Redirecting to feed...")
    time.sleep(2)
    st.switch_page("pages/feed.py")

st.title("📝 Register")

email = st.text_input("Email")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
st.caption("Password must be at least 8 characters long, with 1 uppercase and 1 lowercase letter.")

if st.button("Register"):
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password
        }
    )

    if response.status_code in [200, 201]:
        st.success("Account created. Please login.")
    else:
        try:
            error_data = response.json()
            
            if "detail" in error_data and isinstance(error_data["detail"], list):
                errors = error_data["detail"]
                for error in errors:
                    st.error(error.get("msg", "Validation error"))
            elif "detail" in error_data:
                st.error(error_data["detail"])
            else:
                st.error("Registration failed. Please try again.")
        except:
            st.error(f"Registration failed: {response.text}")



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