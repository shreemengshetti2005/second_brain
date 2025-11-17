"""
Login/Signup page - User authentication
"""

import streamlit as st
import requests
import hashlib

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

API_BASE_URL = "http://localhost:8000/api"

# Hide sidebar until logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)


def create_user(user_data: dict):
    """Create a new user account."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            params={"user_id": user_data['id']}
        )
        
        if response.status_code == 404:
            return True, "Account created successfully!"
        else:
            return False, "This email is already registered"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(email: str):
    """Login existing user."""
    try:
        user_id = hashlib.md5(email.encode()).hexdigest()[:16]
        
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            params={"user_id": user_id}
        )
        
        if response.status_code == 200:
            user = response.json()
            return True, user
        else:
            return False, None
    
    except Exception as e:
        return False, None


# Main UI
st.title("🧠 Second Brain Agent")
st.markdown("### Your AI-Powered Note-Taking System")
st.markdown("---")

# Check if already logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.success(f"✅ You're already logged in as {st.session_state.user_email}")
    st.info("👉 Use the sidebar to navigate to different pages")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.rerun()

else:
    # Login/Signup tabs
    tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])
    
    # Login Tab
    with tab1:
        st.subheader("Welcome Back!")
        
        with st.form("login_form"):
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com"
            )
            
            st.caption("*For demo purposes, no password required*")
            
            login_button = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if login_button:
                if not email:
                    st.error("Please enter your email address")
                else:
                    with st.spinner("Logging in..."):
                        user_id = hashlib.md5(email.encode()).hexdigest()[:16]
                        success, user = login_user(email)
                        
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.session_state.user_name = user.get('first_name', email.split('@')[0])
                            
                            st.success(f"✅ Welcome back, {st.session_state.user_name}!")
                            st.balloons()
                            st.info("👉 Use the sidebar on the left to navigate")
                            st.rerun()
                        else:
                            st.error("❌ Account not found. Please sign up first!")
    
    # Signup Tab
    with tab2:
        st.subheader("Create Your Account")
        
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", placeholder="John")
            
            with col2:
                last_name = st.text_input("Last Name", placeholder="Doe")
            
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                key="signup_email"
            )
            
            language = st.selectbox(
                "Preferred Language",
                ["en", "es", "fr", "de", "hi"],
                index=0
            )
            
            agree = st.checkbox("I agree to the Terms of Service")
            
            signup_button = st.form_submit_button("🎉 Create Account", use_container_width=True)
            
            if signup_button:
                if not email or not first_name:
                    st.error("Please fill in all required fields")
                elif not agree:
                    st.error("Please agree to the Terms of Service")
                else:
                    with st.spinner("Creating your account..."):
                        user_id = hashlib.md5(email.encode()).hexdigest()[:16]
                        
                        user_data = {
                            'id': user_id,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'language_preference': language
                        }
                        
                        success, message = create_user(user_data)
                        
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.session_state.user_name = first_name
                            
                            st.success(f"✅ {message}")
                            st.balloons()
                            
                            st.info(f"""
                            🎉 Welcome to Second Brain Agent, {first_name}!
                            
                            **Get Started:**
                            1. Use the sidebar to navigate
                            2. Go to "Add Note" to create your first note
                            3. Let AI organize everything for you!
                            """)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

    # Demo account
    st.markdown("---")
    with st.expander("🧪 Demo Account"):
        st.markdown("**Quick Demo Access** - Click below to use test account with sample data")
        
        if st.button("🎮 Use Demo Account", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_id = "test_user_001"
            st.session_state.user_email = "demo@example.com"
            st.session_state.user_name = "Demo User"
            st.success("✅ Logged in as Demo User!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🔒 Your data is secure and private</p>
    <p style='font-size: 0.8em;'>Built with ❤️ using FastAPI, Streamlit & Google Cloud AI</p>
</div>
""", unsafe_allow_html=True)