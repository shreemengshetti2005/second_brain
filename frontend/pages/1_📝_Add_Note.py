"""
Add Note page - Create audio or text notes
"""

import streamlit as st
import requests
from io import BytesIO
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Add Note", page_icon="📝", layout="wide")

API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = "test_user_001"

st.title("📝 Add New Note")
st.markdown("Create a new note using text or audio input")

# Tabs for different input methods
tab1, tab2 = st.tabs(["💬 Text Note", "🎤 Audio Note"])

# Text Note Tab
with tab1:
    st.header("Create Text Note")
    
    with st.form("text_note_form"):
        text_input = st.text_area(
            "Enter your note",
            placeholder="Type your note here... (e.g., 'Meeting with team tomorrow at 10 AM to discuss Q4 goals')",
            height=200
        )
        
        source = st.selectbox(
            "Source",
            ["web", "api"],
            index=0
        )
        
        submitted = st.form_submit_button("💾 Save Note", use_container_width=True)
        
        if submitted:
            if not text_input.strip():
                st.error("Please enter some text!")
            else:
                with st.spinner("Processing your note..."):
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
                            st.success("✅ Note saved successfully!")
                            
                            # Show results
                            st.markdown("---")
                            st.subheader("📊 Analysis Results")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Title:** {note['title']}")
                                st.markdown(f"**Category:** {note['primary_tag']}")
                                st.markdown(f"**Priority:** {note['priority']}")
                            
                            with col2:
                                st.markdown(f"**Sentiment:** {note['sentiment']}")
                                if note.get('secondary_tags'):
                                    st.markdown(f"**Tags:** {', '.join(note['secondary_tags'])}")
                            
                            st.markdown(f"**Summary:** {note['summary']}")
                            
                            # Show action items if any
                            if note.get('actionable_items'):
                                st.markdown("**📌 Action Items:**")
                                for item in note['actionable_items']:
                                    priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🟢"
                                    st.markdown(f"{priority_emoji} {item['task']}")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Error saving note: {str(e)}")

# Audio Note Tab
with tab2:
    st.header("Create Audio Note")
    
    st.info("🎤 Click the button below to record your voice note")
    
    # Audio recorder
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="3x"
    )
    
    # File upload as alternative
    st.markdown("**Or upload an audio file:**")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'ogg', 'm4a', 'webm'],
        help="Supported formats: MP3, WAV, OGG, M4A, WEBM"
    )
    
    source = st.selectbox(
        "Source",
        ["web", "api"],
        index=0,
        key="audio_source"
    )
    
    if st.button("💾 Save Audio Note", use_container_width=True):
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
            with st.spinner("Processing your audio note... This may take a moment."):
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
                        data=data
                    )
                    
                    if response.status_code == 201:
                        note = response.json()
                        
                        if note['processing_status'] == 'completed':
                            st.success("✅ Audio note saved and transcribed!")
                            
                            # Show results
                            st.markdown("---")
                            st.subheader("📊 Analysis Results")
                            
                            # Transcription
                            st.markdown("**🎯 Transcription:**")
                            st.info(note['transcription'])
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Title:** {note['title']}")
                                st.markdown(f"**Category:** {note['primary_tag']}")
                                st.markdown(f"**Duration:** {note.get('audio_duration_seconds', 0)}s")
                            
                            with col2:
                                st.markdown(f"**Priority:** {note['priority']}")
                                st.markdown(f"**Sentiment:** {note['sentiment']}")
                                st.markdown(f"**Language:** {note['language']}")
                            
                            st.markdown(f"**Summary:** {note['summary']}")
                            
                            # Show action items
                            if note.get('actionable_items'):
                                st.markdown("**📌 Action Items:**")
                                for item in note['actionable_items']:
                                    priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🟢"
                                    st.markdown(f"{priority_emoji} {item['task']}")
                        else:
                            st.warning(f"Note saved but processing status: {note['processing_status']}")
                            if note.get('error_message'):
                                st.error(f"Error: {note['error_message']}")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")
        else:
            st.warning("Please record audio or upload a file first!")

# Tips
st.markdown("---")
with st.expander("💡 Tips for Better Results"):
    st.markdown("""
    **For Text Notes:**
    - Be specific and detailed
    - Mention dates, names, and deadlines
    - Use natural language
    
    **For Audio Notes:**
    - Speak clearly and at a moderate pace
    - Minimize background noise
    - Keep recordings under 2 minutes for best results
    - State key information clearly (dates, names, tasks)
    
    **Example Notes:**
    - "Team meeting scheduled for next Monday at 10 AM to discuss Q4 strategy"
    - "Remember to buy groceries: milk, eggs, bread, and coffee"
    - "Idea for new app: AI-powered habit tracker with personalized insights"
    - "Book flight to Tokyo for April 15th, budget is $1200"
    """)