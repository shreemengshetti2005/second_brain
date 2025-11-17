"""
Google Drive integration page
"""

import streamlit as st
import requests

st.set_page_config(page_title="Google Drive", page_icon="🔗", layout="wide")

API_BASE_URL = "http://localhost:8000/api"

if 'user_id' not in st.session_state:
    st.session_state.user_id = "test_user_001"

st.title("🔗 Google Drive Integration")
st.markdown("Export your notes to Google Drive as markdown files")

# Check connection status
try:
    response = requests.get(
        f"{API_BASE_URL}/gdrive/status",
        params={"user_id": st.session_state.user_id}
    )
    
    if response.status_code == 200:
        status = response.json()
        is_connected = status.get('connected', False)
        
        if is_connected:
            st.success("✅ Google Drive is connected")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Notes", status.get('total_notes', 0))
            
            with col2:
                st.metric("Synced to Drive", status.get('synced_notes', 0))
            
            with col3:
                st.metric("Pending Sync", status.get('pending_sync', 0))
        else:
            st.warning("⚠️ Google Drive is not connected")
    
    else:
        st.error("Unable to check Drive status")
        is_connected = False

except Exception as e:
    st.error(f"Error: {str(e)}")
    is_connected = False

st.markdown("---")

# Connection setup
if not is_connected:
    st.subheader("🔐 Connect Google Drive")
    
    st.info("""
    **To connect Google Drive:**
    
    1. Configure OAuth credentials in `.env` file:
       - `GDRIVE_CLIENT_ID`
       - `GDRIVE_CLIENT_SECRET`
    
    2. Restart the backend
    
    3. Use the authentication flow (coming soon)
    
    For detailed instructions: `python scripts/setup_google_apis.py`
    """)
    
    if st.button("🔗 Connect Google Drive", disabled=True):
        st.info("OAuth flow will be implemented here")

else:
    # Export options
    st.subheader("📤 Export Options")
    
    tab1, tab2 = st.tabs(["Export All", "Export by Category"])
    
    with tab1:
        st.markdown("**Export all your notes to Google Drive**")
        
        if st.button("📥 Export All Notes", use_container_width=True):
            with st.spinner("Exporting notes to Google Drive..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/gdrive/export-all",
                        params={"user_id": st.session_state.user_id}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Export complete!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Exported", result.get('exported', 0))
                        with col2:
                            st.metric("Failed", result.get('failed', 0))
                        with col3:
                            st.metric("Total", result.get('total', 0))
                    else:
                        st.error(f"Export failed: {response.json().get('detail')}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.markdown("**Export notes by category**")
        
        category = st.selectbox(
            "Select Category",
            ["Work", "Personal", "Travel", "Ideas", "Projects", "Health", "Learning", "Finance", "Shopping", "Other"]
        )
        
        if st.button(f"📥 Export {category} Notes", use_container_width=True):
            with st.spinner(f"Exporting {category} notes..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/gdrive/export-all",
                        params={
                            "user_id": st.session_state.user_id,
                            "primary_tag": category
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Exported {result.get('exported', 0)} {category} notes!")
                    else:
                        st.error("Export failed")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")

# Recent syncs
st.subheader("📋 Recently Synced Notes")

try:
    response = requests.get(
        f"{API_BASE_URL}/notes",
        params={
            "user_id": st.session_state.user_id,
            "page": 1,
            "page_size": 5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        notes = data.get('notes', [])
        
        synced_notes = [n for n in notes if n.get('synced_to_gdrive')]
        
        if synced_notes:
            for note in synced_notes:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{note['title']}**")
                    st.caption(f"Category: {note['primary_tag']}")
                
                with col2:
                    if note.get('gdrive_file_url'):
                        st.link_button("📁 Open in Drive", note['gdrive_file_url'])
        else:
            st.info("No synced notes yet")

except Exception as e:
    st.error(f"Error loading synced notes: {str(e)}")

# Help
st.markdown("---")
with st.expander("❓ Help"):
    st.markdown("""
    **File Format:**
    - Notes are exported as `.md` (Markdown) files
    - Files include metadata, content, and action items
    - Compatible with Obsidian and other markdown editors
    
    **File Organization:**
    - Files are organized by category
    - Filename format: `YYYY-MM-DD_title.md`
    
    **Sync Behavior:**
    - Manual sync: Use export buttons
    - Auto-sync: Enable in Settings (if configured)
    - Notes are synced once (not updated after export)
    """)