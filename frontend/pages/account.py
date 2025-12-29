import streamlit as st
import requests
from api import API_URL, get_headers
from auth import logout
import time


# Redirect if not logged in
if "token" not in st.session_state:
    st.error("Your account is being deleted. Redirecting to login page...")
    time.sleep(2)
    st.switch_page("pages/login.py")
    
st.title("⚠️ Account")

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# First button - Delete Account
if st.button("Delete My Account", type="secondary"):
    st.session_state.confirm_delete = True

# If user clicked delete, show confirmation
if st.session_state.confirm_delete:
    st.warning("Are you sure you want to delete your account? This cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Delete", type="primary"):
            # Make delete request
            response = requests.delete(
                f"{API_URL}/account",
                headers=get_headers()
            )
            
            logout()
            
            if response.status_code == 204:
                st.success("Your account has been deleted successfully!")
                
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # Use markdown redirect instead
                st.markdown("""
                    <meta http-equiv="refresh" content="2; url='http://localhost:8501/'" />
                    Redirecting to home page...
                """, unsafe_allow_html=True)
                st.stop()
            else:
                st.error(f"Failed to delete account: {response.text}")
                st.session_state.confirm_delete = False
    
    with col2:
        if st.button("Cancel"):
            st.session_state.confirm_delete = False
            st.rerun()
            

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