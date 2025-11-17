"""
Add Note page - Create audio or text notes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import require_login, render_sidebar_user_info

import streamlit as st
import requests
from io import BytesIO

st.set_page_config(page_title="Add Note", page_icon="📝", layout="wide")

# Check authentication
require_login()

API_BASE_URL = "http://localhost:8000/api"

st.title("📝 Add New Note")
st.markdown("Create a new note using text or audio input")

# Render sidebar
render_sidebar_user_info()

# Tabs for different input methods
tab1, tab2 = st.tabs(["💬 Text Note", "🎤 Audio Note"])

# ============================================
# TEXT NOTE TAB
# ============================================
with tab1:
    st.header("Create Text Note")
    
    with st.form("text_note_form"):
        text_input = st.text_area(
            "Enter your note",
            placeholder="Type your note here... (e.g., 'Meeting with team tomorrow at 10 AM to discuss Q4 goals')",
            height=200,
            help="Be specific and detailed for better AI categorization"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.selectbox(
                "Source",
                ["web", "api", "manual"],
                index=0,
                help="Where this note is coming from"
            )
        
        with col2:
            st.caption("AI will automatically categorize your note")
        
        submitted = st.form_submit_button("💾 Save Note", use_container_width=True, type="primary")
    
    # Handle submission OUTSIDE the form
    if submitted:
        if not text_input.strip():
            st.error("❌ Please enter some text!")
        else:
            with st.spinner("🤖 Processing your note with AI..."):
                try:
                    # Create note via API
                    response = requests.post(
                        f"{API_BASE_URL}/notes/text",
                        json={
                            "input_type": "text",
                            "source": source,
                            "original_text": text_input,
                            "user_id": st.session_state.user_id
                        }
                    )
                    
                    if response.status_code == 201:
                        note = response.json()
                        
                        # Clear search cache so new note appears immediately
                        if 'search_results' in st.session_state:
                            del st.session_state['search_results']
                        if 'search_performed' in st.session_state:
                            del st.session_state['search_performed']
                        
                        st.success("✅ Note saved successfully!")
                        
                        # Show results
                        st.markdown("---")
                        st.subheader("📊 AI Analysis Results")
                        
                        # Title and summary
                        st.markdown(f"### {note['title']}")
                        st.info(note['summary'])
                        
                        # Details in columns
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            tag_colors = {
                                "Work": "🔵",
                                "Personal": "🟢",
                                "Travel": "🟣",
                                "Ideas": "🟡",
                                "Projects": "🟠",
                                "Health": "❤️",
                                "Learning": "📚",
                                "Finance": "💰",
                                "Shopping": "🛒",
                                "Other": "⚪"
                            }
                            emoji = tag_colors.get(note['primary_tag'], "🏷️")
                            st.markdown(f"**Category:** {emoji} {note['primary_tag']}")
                            
                            if note.get('secondary_tags'):
                                st.markdown(f"**Tags:** {', '.join(note['secondary_tags'][:3])}")
                        
                        with col2:
                            priority_emoji = "🔴" if note['priority'] == 'high' else "🟡" if note['priority'] == 'medium' else "🟢"
                            st.markdown(f"**Priority:** {priority_emoji} {note['priority'].title()}")
                            st.markdown(f"**Sentiment:** {note['sentiment'].title()}")
                        
                        with col3:
                            st.markdown(f"**Source:** {note['source']}")
                            st.markdown(f"**Note ID:** `{note['id'][:8]}...`")
                        
                        # Action items if any
                        if note.get('actionable_items') and len(note['actionable_items']) > 0:
                            st.markdown("---")
                            st.markdown("### 📌 Action Items Detected")
                            for idx, item in enumerate(note['actionable_items'], 1):
                                priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🟢"
                                deadline = f" | Due: {item['deadline']}" if item.get('deadline') else ""
                                st.markdown(f"{idx}. {priority_emoji} **{item['task']}**{deadline}")
                        
                        # Key entities
                        if note.get('key_entities'):
                            entities = note['key_entities']
                            has_entities = any([
                                entities.get('people'),
                                entities.get('places'),
                                entities.get('companies'),
                                entities.get('dates')
                            ])
                            
                            if has_entities:
                                st.markdown("---")
                                st.markdown("### 🔍 Key Entities Extracted")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    if entities.get('people'):
                                        st.markdown("**👥 People**")
                                        for person in entities['people'][:3]:
                                            st.caption(f"• {person}")
                                
                                with col2:
                                    if entities.get('places'):
                                        st.markdown("**📍 Places**")
                                        for place in entities['places'][:3]:
                                            st.caption(f"• {place}")
                                
                                with col3:
                                    if entities.get('companies'):
                                        st.markdown("**🏢 Companies**")
                                        for company in entities['companies'][:3]:
                                            st.caption(f"• {company}")
                                
                                with col4:
                                    if entities.get('dates'):
                                        st.markdown("**📅 Dates**")
                                        for date in entities['dates'][:3]:
                                            st.caption(f"• {date}")
                        
                        # Topics
                        if note.get('topics'):
                            st.markdown("---")
                            st.markdown("**💭 Topics:** " + ", ".join([f"`{topic}`" for topic in note['topics'][:5]]))
                    
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error saving note: {str(e)}")

# ============================================
# AUDIO NOTE TAB
# ============================================
with tab2:
    st.header("Create Audio Note")
    
    st.info("🎤 Record or upload an audio file to create a note")
    
    # Try to import audio recorder
    try:
        from audio_recorder_streamlit import audio_recorder
        
        st.markdown("### 🎙️ Record Audio")
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_name="microphone",
            icon_size="3x"
        )
    except ImportError:
        st.warning("⚠️ Audio recorder not available. Please upload an audio file instead.")
        audio_bytes = None
    
    # File upload as alternative
    st.markdown("### 📁 Or Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'ogg', 'm4a', 'webm', 'flac'],
        help="Supported formats: MP3, WAV, OGG, M4A, WEBM, FLAC"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        source = st.selectbox(
            "Source",
            ["web", "api", "telegram"],
            index=0,
            key="audio_source",
            help="Where this audio note is coming from"
        )
    
    with col2:
        st.caption("Speech-to-Text API required for transcription")
    
    # Button OUTSIDE form
    if st.button("💾 Save Audio Note", use_container_width=True, type="primary"):
        audio_to_process = None
        filename = None
        
        # Determine which audio source to use
        if audio_bytes:
            audio_to_process = audio_bytes
            filename = "recorded_audio.wav"
        elif uploaded_file:
            audio_to_process = uploaded_file.read()
            filename = uploaded_file.name
        
        if audio_to_process:
            with st.spinner("🎯 Transcribing and processing your audio... This may take a moment."):
                try:
                    # Create note via API
                    files = {
                        'audio_file': (filename, audio_to_process, 'audio/wav')
                    }
                    data = {
                        'user_id': st.session_state.user_id,
                        'source': source
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/notes/audio",
                        files=files,
                        data=data,
                        timeout=60
                    )
                    
                    if response.status_code == 201:
                        note = response.json()
                        
                        # Clear search cache
                        if 'search_results' in st.session_state:
                            del st.session_state['search_results']
                        if 'search_performed' in st.session_state:
                            del st.session_state['search_performed']
                        
                        if note['processing_status'] == 'completed':
                            st.success("✅ Audio note saved and transcribed!")
                            
                            # Show results
                            st.markdown("---")
                            st.subheader("📊 Audio Analysis Results")
                            
                            # Transcription
                            st.markdown("### 🎯 Transcription")
                            st.info(note['transcription'])
                            
                            # Title and summary
                            st.markdown(f"### {note['title']}")
                            st.write(note['summary'])
                            
                            # Details
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                tag_colors = {
                                    "Work": "🔵",
                                    "Personal": "🟢",
                                    "Travel": "🟣",
                                    "Ideas": "🟡",
                                    "Projects": "🟠",
                                    "Health": "❤️",
                                    "Learning": "📚",
                                    "Finance": "💰",
                                    "Shopping": "🛒",
                                    "Other": "⚪"
                                }
                                emoji = tag_colors.get(note['primary_tag'], "🏷️")
                                st.markdown(f"**Category:** {emoji} {note['primary_tag']}")
                                st.markdown(f"**Duration:** {note.get('audio_duration_seconds', 0)}s")
                            
                            with col2:
                                priority_emoji = "🔴" if note['priority'] == 'high' else "🟡" if note['priority'] == 'medium' else "🟢"
                                st.markdown(f"**Priority:** {priority_emoji} {note['priority'].title()}")
                                st.markdown(f"**Sentiment:** {note['sentiment'].title()}")
                            
                            with col3:
                                st.markdown(f"**Language:** {note.get('language', 'en-US')}")
                                st.markdown(f"**Source:** {note['source']}")
                            
                            # Action items
                            if note.get('actionable_items'):
                                st.markdown("---")
                                st.markdown("### 📌 Action Items")
                                for idx, item in enumerate(note['actionable_items'], 1):
                                    priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🟢"
                                    st.markdown(f"{idx}. {priority_emoji} {item['task']}")
                        else:
                            st.warning(f"⚠️ Note saved but processing status: {note['processing_status']}")
                            if note.get('error_message'):
                                st.error(f"Error: {note['error_message']}")
                    
                    elif response.status_code == 503:
                        st.error("❌ Speech-to-Text API is not configured")
                        st.info("Configure Speech-to-Text API in Settings to enable audio transcription")
                    
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Please try with a shorter audio file.")
                except Exception as e:
                    st.error(f"❌ Error processing audio: {str(e)}")
        else:
            st.warning("⚠️ Please record audio or upload a file first!")

# ============================================
# TIPS SECTION
# ============================================
st.markdown("---")
with st.expander("💡 Tips for Better Results"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **For Text Notes:**
        - Be specific - Include dates, names, and details
        - Mention actions - Use words like "need to", "must", "should"
        - Include context - More detail = better categorization
        - Use natural language - Write as you would speak
        
        **Examples:**
        - "Team meeting tomorrow at 10 AM with Sarah to discuss Q4 marketing strategy"
        - "Need to buy groceries by Friday: milk, eggs, bread, coffee"
        - "Idea: Build a mobile app for habit tracking with AI insights"
        """)
    
    with col2:
        st.markdown("""
        **For Audio Notes:**
        - Speak clearly - Moderate pace works best
        - Minimize noise - Find a quiet environment
        - Keep it short - Under 2 minutes for best results
        - State key info - Dates, names, tasks clearly
        
        **Best Practices:**
        - Record in a quiet room
        - Speak into microphone directly
        - Pause between key points
        - Use simple, clear language
        """)