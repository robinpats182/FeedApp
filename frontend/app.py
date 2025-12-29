import streamlit as st

st.set_page_config(
    page_title="Home",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📝 FeedApp")
st.subheader("Share your thoughts, connect with others")

st.markdown("---")

# Check if user is logged in
is_logged_in = "token" in st.session_state

if is_logged_in:
    st.success("✅ You are logged in")
    st.markdown("""
    ### What you can do:
    
    📤 **Upload** - Share images and videos with captions
    
    📰 **Feed** - Browse posts from other users
    
    ❤️ **Like & Comment** - Engage with the community
    
    ⚙️ **Account** - Manage your profile and delete account
    """)
else:
    st.info("👤 Please login to get started")
    st.markdown("""
    ### Features:
    
    📤 **Upload Posts** - Share your moments
    
    📰 **Discover Feed** - See what others are sharing
    
    ❤️ **Interactions** - Like and comment on posts
    
    👥 **Community** - Connect with users
    """)
    
    if st.button("🔐 Go to Login", use_container_width=True):
        st.switch_page("pages/login.py")

st.markdown("---")

st.markdown("""
### About BlogHub
A simple social media platform to share and discover content.
Built with FastAPI and Streamlit.

**Version:** 1.0.0
""")

# Custom sidebar logic
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