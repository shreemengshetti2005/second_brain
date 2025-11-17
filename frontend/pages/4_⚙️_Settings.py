"""
Settings page - User preferences and configuration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import require_login, render_sidebar_user_info

import streamlit as st
import requests

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

# Check authentication
require_login()

API_BASE_URL = "http://localhost:8000/api"

st.title("⚙️ Settings")
st.markdown("Manage your preferences and integrations")

# Render user info in sidebar
render_sidebar_user_info()

# User Info
st.subheader("👤 User Information")

col1, col2 = st.columns(2)

with col1:
    st.text_input("User ID", value=st.session_state.user_id, disabled=True)
    st.text_input("Name", value=st.session_state.get('user_name', 'N/A'), disabled=True)
    st.text_input("Email", value=st.session_state.get('user_email', 'Not set'), disabled=True)

with col2:
    # Try to get additional info from API
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            params={"user_id": st.session_state.user_id}
        )
        
        if response.status_code == 200:
            user = response.json()
            st.text_input("Telegram", value=user.get('telegram_username', 'Not connected'), disabled=True)
            st.text_input("Language", value=user.get('language_preference', 'en'), disabled=True)
            
            if user.get('created_at'):
                st.text_input("Member Since", value=user['created_at'][:10], disabled=True)
            
            # Show connection status
            if user.get('telegram_id'):
                st.success("✅ Telegram Connected")
            else:
                st.info("📱 Connect Telegram to use voice messages")
        else:
            st.info("📝 Complete your profile by adding notes")
    except Exception as e:
        st.warning("Unable to load additional profile info")

st.markdown("---")

# Preferences
st.subheader("🎨 Preferences")

with st.form("preferences_form"):
    language = st.selectbox(
        "Preferred Language",
        ["en", "es", "fr", "de", "hi"],
        index=0,
        help="Language for transcriptions and interface"
    )
    
    auto_sync = st.checkbox(
        "Auto-sync to Google Drive",
        value=True,
        help="Automatically export new notes to Google Drive"
    )
    
    default_tags = st.multiselect(
        "Default Tags",
        ["Work", "Personal", "Travel", "Ideas", "Projects", "Health", "Learning", "Finance"],
        default=[],
        help="Default tags to suggest when creating notes"
    )
    
    save_prefs = st.form_submit_button("💾 Save Preferences", use_container_width=True)
    
    if save_prefs:
        try:
            response = requests.put(
                f"{API_BASE_URL}/users/preferences",
                params={"user_id": st.session_state.user_id},
                json={
                    "language_preference": language,
                    "auto_sync_gdrive": auto_sync,
                    "default_tags": default_tags
                }
            )
            
            if response.status_code == 200:
                st.success("✅ Preferences saved!")
            else:
                st.error("Failed to save preferences")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")

# API Configuration Status
st.subheader("🔧 API Configuration")

try:
    response = requests.get(f"http://localhost:8000/health")
    
    if response.status_code == 200:
        health = response.json()
        services = health.get('services', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gemini_status = services.get('gemini_api', 'not_configured')
            if gemini_status == 'configured':
                st.success("✅ Gemini API")
            else:
                st.error("❌ Gemini API")
        
        with col2:
            stt_status = services.get('speech_to_text', 'not_configured')
            if stt_status == 'configured':
                st.success("✅ Speech-to-Text")
            else:
                st.error("❌ Speech-to-Text")
        
        with col3:
            drive_status = services.get('google_drive', 'not_configured')
            if drive_status == 'configured':
                st.success("✅ Google Drive")
            else:
                st.error("❌ Google Drive")
        
        # Configuration help
        if gemini_status != 'configured' or stt_status != 'configured':
            with st.expander("📚 How to configure APIs"):
                st.markdown("""
                **To enable AI features, you need to configure Google APIs:**
                
                1. **Gemini API (Required for classification)**
                   - Go to: https://aistudio.google.com/app/apikey
                   - Create API key
                   - Add to `.env`: `GEMINI_API_KEY=your_key`
                
                2. **Speech-to-Text API (For audio transcription)**
                   - Go to: https://console.cloud.google.com
                   - Enable Speech-to-Text API
                   - Download service account JSON
                   - Add to `.env`: `GOOGLE_APPLICATION_CREDENTIALS=path/to/json`
                
                3. **Restart the backend** after updating `.env`
                
                For detailed instructions, run: `python scripts/setup_google_apis.py`
                """)
    
except Exception as e:
    st.warning("Unable to check API status")

st.markdown("---")

# Data Management
st.subheader("💾 Data Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Export Data**")
    if st.button("📥 Export All Notes (JSON)", use_container_width=True):
        st.info("Export feature coming soon!")

with col2:
    st.markdown("**Danger Zone**")
    if st.button("🗑️ Delete All Notes", type="secondary", use_container_width=True):
        st.warning("⚠️ This action cannot be undone!")
        st.info("Delete feature disabled for safety")

st.markdown("---")

# System Info
with st.expander("ℹ️ System Information"):
    st.markdown(f"""
    **Backend API:** http://localhost:8000
    
    **Frontend:** Streamlit
    
    **Database:** PostgreSQL (secondbrain)
    
    **Vector Store:** ChromaDB
    
    **Version:** 1.0.0
    
    **Logged in as:** {st.session_state.get('user_email', 'Unknown')}
    """)