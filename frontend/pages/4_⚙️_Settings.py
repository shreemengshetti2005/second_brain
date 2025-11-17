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

# Render sidebar
render_sidebar_user_info()

# Initialize session state for user data cache
if 'user_data_cache' not in st.session_state:
    st.session_state.user_data_cache = None

# Fetch current user data
def load_user_data():
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            params={"user_id": st.session_state.user_id}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'id': st.session_state.user_id,
                'email': st.session_state.get('user_email', ''),
                'first_name': st.session_state.get('user_name', ''),
                'last_name': '',
                'telegram_id': None,
                'telegram_username': None,
                'language_preference': 'en',
                'auto_sync_gdrive': True,
                'default_tags': [],
                'created_at': None
            }
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return None

# Load user data
if st.session_state.user_data_cache is None or st.button("🔄 Refresh Data", help="Reload user data"):
    user_data = load_user_data()
    st.session_state.user_data_cache = user_data
else:
    user_data = st.session_state.user_data_cache

if not user_data:
    st.error("Unable to load user data")
    st.stop()

# ============================================
# USER INFORMATION (EDITABLE)
# ============================================
st.subheader("👤 User Information")

with st.form("user_info_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("User ID", value=st.session_state.user_id, disabled=True, help="User ID cannot be changed")
        
        new_first_name = st.text_input(
            "First Name",
            value=user_data.get('first_name', ''),
            placeholder="Enter your first name"
        )
        
        new_email = st.text_input(
            "Email",
            value=user_data.get('email', ''),
            placeholder="your.email@example.com"
        )
    
    with col2:
        new_last_name = st.text_input(
            "Last Name",
            value=user_data.get('last_name', ''),
            placeholder="Enter your last name"
        )
        
        st.text_input(
            "Telegram",
            value=user_data.get('telegram_username', 'Not connected'),
            disabled=True,
            help="Connect Telegram below"
        )
        
        if user_data.get('created_at'):
            st.text_input("Member Since", value=user_data['created_at'][:10], disabled=True)
    
    update_profile = st.form_submit_button("💾 Update Profile", use_container_width=True, type="primary")

# Handle profile update OUTSIDE the form
if update_profile:
    if not new_first_name or not new_email:
        st.error("❌ First name and email are required!")
    else:
        # Check if anything actually changed
        changed = (
            new_first_name != user_data.get('first_name', '') or
            new_last_name != user_data.get('last_name', '') or
            new_email != user_data.get('email', '')
        )
        
        if not changed:
            st.info("ℹ️ No changes detected")
        else:
            try:
                # Update user preferences endpoint
                response = requests.put(
                    f"{API_BASE_URL}/users/preferences",
                    params={"user_id": st.session_state.user_id},
                    json={
                        "first_name": new_first_name,
                        "last_name": new_last_name,
                        "email": new_email
                    }
                )
                
                if response.status_code == 200:
                    # Update session state
                    st.session_state.user_email = new_email
                    st.session_state.user_name = new_first_name
                    
                    # Update cache
                    user_data['first_name'] = new_first_name
                    user_data['last_name'] = new_last_name
                    user_data['email'] = new_email
                    st.session_state.user_data_cache = user_data
                    
                    st.success("✅ Profile updated successfully!")
                else:
                    st.error(f"❌ Failed to update profile: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")

# ============================================
# TELEGRAM CONNECTION
# ============================================
st.subheader("📱 Telegram Integration")

if user_data.get('telegram_id'):
    st.success(f"✅ Connected as @{user_data.get('telegram_username', 'Unknown')}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("""
        **You're connected!** Send voice or text messages to your bot to create notes automatically.
        """)
    
    with col2:
        if st.button("🔌 Disconnect Telegram", use_container_width=True):
            st.warning("Disconnect feature coming soon")
else:
    st.warning("⚠️ Telegram not connected")
    
    with st.expander("📚 How to Connect Telegram"):
        st.markdown("""
        **Setup Instructions:**
        
        1. Create your bot with @BotFather on Telegram
        2. Add bot token to `.env`: `TELEGRAM_BOT_TOKEN=your_token`
        3. Set up webhook (see documentation)
        4. Restart backend
        
        **For detailed guide:** Run `python scripts/setup_telegram_bot.py`
        """)

st.markdown("---")

# ============================================
# PREFERENCES
# ============================================
st.subheader("🎨 Preferences")

with st.form("preferences_form"):
    language = st.selectbox(
        "Preferred Language",
        ["en", "es", "fr", "de", "hi"],
        index=["en", "es", "fr", "de", "hi"].index(user_data.get('language_preference', 'en')),
        help="Language for transcriptions and interface"
    )
    
    auto_sync = st.checkbox(
        "Auto-sync to Google Drive",
        value=user_data.get('auto_sync_gdrive', True),
        help="Automatically export new notes to Google Drive"
    )
    
    default_tags = st.multiselect(
        "Default Tags",
        ["Work", "Personal", "Travel", "Ideas", "Projects", "Health", "Learning", "Finance"],
        default=user_data.get('default_tags', []),
        help="Default tags to suggest when creating notes"
    )
    
    save_prefs = st.form_submit_button("💾 Save Preferences", use_container_width=True, type="primary")

# Handle preferences update OUTSIDE the form
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
            # Update cache
            user_data['language_preference'] = language
            user_data['auto_sync_gdrive'] = auto_sync
            user_data['default_tags'] = default_tags
            st.session_state.user_data_cache = user_data
            
            st.success("✅ Preferences saved successfully!")
        else:
            st.error("❌ Failed to save preferences")
    except Exception as e:
        st.error(f"❌ Error: {e}")

st.markdown("---")

# ============================================
# API CONFIGURATION STATUS
# ============================================
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
                st.caption("AI classification active")
            else:
                st.error("❌ Gemini API")
                st.caption("Classification limited")
        
        with col2:
            stt_status = services.get('speech_to_text', 'not_configured')
            if stt_status == 'configured':
                st.success("✅ Speech-to-Text")
                st.caption("Audio transcription ready")
            else:
                st.warning("⚠️ Speech-to-Text")
                st.caption("Audio features disabled")
        
        with col3:
            drive_status = services.get('google_drive', 'not_configured')
            if drive_status == 'configured':
                st.success("✅ Google Drive")
                st.caption("Export enabled")
            else:
                st.warning("⚠️ Google Drive")
                st.caption("Export unavailable")
        
        # Configuration help
        if gemini_status != 'configured':
            with st.expander("📚 API Configuration Guide"):
                st.markdown("""
                **Gemini API (Required for AI features):**
                1. Get free key: https://aistudio.google.com/app/apikey
                2. Add to `.env`: `GEMINI_API_KEY=your_key`
                3. Restart backend
                
                **For other APIs:** Run `python scripts/setup_google_apis.py`
                """)
except Exception as e:
    st.warning("Unable to check API status")

st.markdown("---")

# ============================================
# DATA MANAGEMENT
# ============================================
st.subheader("💾 Data Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📥 Export Data**")
    
    if st.button("📥 Export All Notes (JSON)", use_container_width=True):
        try:
            response = requests.get(
                f"{API_BASE_URL}/notes",
                params={
                    "user_id": st.session_state.user_id,
                    "page": 1,
                    "page_size": 1000
                }
            )
            
            if response.status_code == 200:
                notes_data = response.json()
                notes = notes_data.get('notes', [])
                
                if notes:
                    import json
                    from datetime import datetime
                    
                    json_data = json.dumps(notes, indent=2)
                    
                    st.download_button(
                        label="⬇️ Download JSON",
                        data=json_data,
                        file_name=f"second_brain_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    st.success(f"✅ Ready to download {len(notes)} notes")
                else:
                    st.info("No notes to export")
            else:
                st.error("Failed to fetch notes")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    st.markdown("**🗑️ Danger Zone**")
    
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False
    
    if not st.session_state.confirm_delete:
        if st.button("🗑️ Delete All Notes", type="secondary", use_container_width=True):
            st.session_state.confirm_delete = True
            st.rerun()
    else:
        st.error("⚠️ Are you sure? This cannot be undone!")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/notes",
                        params={
                            "user_id": st.session_state.user_id,
                            "page": 1,
                            "page_size": 1000
                        }
                    )
                    
                    if response.status_code == 200:
                        notes = response.json().get('notes', [])
                        
                        deleted = 0
                        for note in notes:
                            try:
                                del_response = requests.delete(
                                    f"{API_BASE_URL}/notes/{note['id']}",
                                    params={"user_id": st.session_state.user_id}
                                )
                                if del_response.status_code == 200:
                                    deleted += 1
                            except:
                                pass
                        
                        st.session_state.confirm_delete = False
                        
                        if 'search_results' in st.session_state:
                            del st.session_state['search_results']
                        if 'search_performed' in st.session_state:
                            del st.session_state['search_performed']
                        
                        st.success(f"✅ Deleted {deleted} notes")
                        st.rerun()
                    else:
                        st.error("Failed to fetch notes")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col_b:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()

st.markdown("---")

# System info
with st.expander("ℹ️ System Information"):
    st.markdown(f"""
    **Application:** Second Brain Agent v1.0.0
    
    **Backend:** http://localhost:8000
    
    **Database:** PostgreSQL + ChromaDB
    
    **User:** {st.session_state.get('user_email', 'Unknown')}
    
    **User ID:** `{st.session_state.user_id}`
    """)