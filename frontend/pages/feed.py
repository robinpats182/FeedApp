import streamlit as st
import requests
from api import API_URL, get_headers

st.set_page_config(page_title="Feed", layout="centered")

st.markdown("""
    <style>
    .post-meta {
        font-size: 0.875rem;
        color: #666;
        margin: 0.5rem 0;
    }
    .post-divider {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e5e5e5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Feed")

response = requests.get(f"{API_URL}/feed")

if response.status_code != 200:
    st.error("Failed to load feed")
    st.stop()

posts = response.json()["posts"]

if not posts:
    st.info("No posts yet")
    st.stop()

for post in posts:
    # Media at top
    if post["file_type"] == "image":
        st.image(post["url"], width=500)
    else:
        st.video(post["url"])
    
    # Post header and meta
    st.markdown(f"#### @{post['username']}")
    st.markdown(f"<div class='post-meta'>{post['created_at'][:10]}</div>", unsafe_allow_html=True)
    
    # Caption
    st.markdown(f"{post['caption']}")
    
    # Get likes and comments count
    likes_count = 0
    comments_count = 0
    
    # if "token" in st.session_state:
    likes_response = requests.get(f"{API_URL}/posts/{post['id']}/likes")
    if likes_response.status_code == 200:
        likes_count = likes_response.json().get("likes_count", 0)
    
    comments_response = requests.get(f"{API_URL}/posts/{post['id']}/comments")
    if comments_response.status_code == 200:
        comments_count = len(comments_response.json()["comments"])
    
    # Actions row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if "token" in st.session_state:
            # Get like count (public endpoint)
            likes_response = requests.get(f"{API_URL}/posts/{post['id']}/likes")
            likes_count = 0
            if likes_response.status_code == 200:
                likes_count = likes_response.json().get("likes_count", 0)
            
            # Check if user liked (authenticated endpoint)
            user_liked = False
            user_like_response = requests.get(
                f"{API_URL}/posts/{post['id']}/user-like",
                headers=get_headers()
            )
            if user_like_response.status_code == 200:
                user_liked = user_like_response.json().get("user_liked", False)
            
            # Show filled heart if liked, empty if not
            button_text = f"❤️ ({likes_count})" if user_liked else f"🤍 ({likes_count})"
            
            if st.button(button_text, key=f"like_{post['id']}", use_container_width=True):
                if user_liked:
                    # Unlike
                    unlike_response = requests.delete(
                        f"{API_URL}/posts/{post['id']}/like",
                        headers=get_headers()
                    )
                    if unlike_response.status_code == 200:
                        st.rerun()
                else:
                    # Like
                    like_response = requests.post(
                        f"{API_URL}/posts/{post['id']}/like",
                        headers=get_headers()
                    )
                    if like_response.status_code == 200:
                        st.rerun()
        else:
            # Get like count for non-authenticated users
            likes_response = requests.get(f"{API_URL}/posts/{post['id']}/likes")
            likes_count = 0
            if likes_response.status_code == 200:
                likes_count = likes_response.json().get("likes_count", 0)
            
            st.button(f"🤍 ({likes_count})", key=f"like_{post['id']}", disabled=True, use_container_width=True)

    
    with col2:
        if st.button(f"💬 ({comments_count})", key=f"comment_{post['id']}", use_container_width=True):
            st.session_state[f"show_comments_{post['id']}"] = not st.session_state.get(f"show_comments_{post['id']}", False)
            st.rerun()
    
    with col3:
        st.button("📤 Share", key=f"share_{post['id']}", use_container_width=True, disabled=True)
    
    with col4:
        if "token" in st.session_state:
            if st.button("🗑️", key=f"delete_{post['id']}", use_container_width=True):
                delete = requests.delete(
                    f"{API_URL}/posts/{post['id']}",
                    headers=get_headers()
                )
                if delete.status_code == 200:
                    st.success("Deleted")
                    st.rerun()
                else:
                    st.error("Failed to delete")
    
    # Comments section
    if st.session_state.get(f"show_comments_{post['id']}", False):
        st.markdown("---")
        
        # Get comments
        comments_response = requests.get(f"{API_URL}/posts/{post['id']}/comments")
        if comments_response.status_code == 200:
            comments = comments_response.json()["comments"]
            if comments:
                for comment in comments:
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown(f"**@{comment['username']}**")
                        st.markdown(f"{comment['content']}")
                        st.caption(comment['created_at'][:10])
                    with col2:
                        if "token" in st.session_state:
                            if st.button("🗑", key=f"delete_comment_{comment['id']}"):
                                delete_comment = requests.delete(
                                    f"{API_URL}/comments/{comment['id']}",
                                    headers=get_headers()
                                )
                                if delete_comment.status_code == 200:
                                    st.rerun()
        
        # Add comment
        if "token" in st.session_state:
            st.markdown("---")
            comment_text = st.text_input("Add a comment...", key=f"comment_input_{post['id']}", label_visibility="collapsed")
            if st.button("Post Comment", key=f"post_comment_{post['id']}", use_container_width=True):
                if comment_text.strip():
                    comment_response = requests.post(
                        f"{API_URL}/posts/{post['id']}/comment",
                        data={"content": comment_text},
                        headers=get_headers()
                    )
                    if comment_response.status_code == 200:
                        st.rerun()
                    else:
                        st.error("Failed to post comment")
        else:
            st.info("Login to comment")
    
    st.markdown("<div class='post-divider'></div>", unsafe_allow_html=True)


    

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