"""
Utility functions for frontend
"""

import streamlit as st


def require_login():
    """
    Check if user is logged in. Redirect to login if not.
    Add this at the top of every page.
    """
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Please login to access this page")
        
        # Create a centered login button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h3>Authentication Required</h3>
                <p>You need to be logged in to access this page.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔐 Go to Login Page", use_container_width=True, type="primary"):
                # Set a flag to navigate
                st.session_state.navigate_to_login = True
                st.rerun()
        
        st.stop()


def get_current_user():
    """Get current logged in user info."""
    return {
        'user_id': st.session_state.get('user_id'),
        'email': st.session_state.get('user_email'),
        'name': st.session_state.get('user_name')
    }


def render_sidebar_user_info():
    """Render user info in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Account")
        st.markdown(f"**{st.session_state.get('user_name', 'User')}**")
        st.caption(st.session_state.get('user_email', ''))
        
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            logout()


def logout():
    """Logout current user."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.navigate_to_login = True
    st.rerun()


def safe_switch_page(page_path: str):
    """
    Safely switch pages - compatible with different Streamlit versions.
    
    Args:
        page_path: Path to the page (e.g., "pages/0_🔐_Login.py")
    """
    if hasattr(st, 'switch_page'):
        # New Streamlit version
        st.switch_page(page_path)
    else:
        # Old Streamlit version - use session state flag
        st.session_state.navigate_to = page_path
        st.rerun()