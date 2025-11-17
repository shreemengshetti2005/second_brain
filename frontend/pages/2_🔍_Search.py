"""
Search page - Search and filter notes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import require_login, render_sidebar_user_info

import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Search Notes", page_icon="🔍", layout="wide")

# Check authentication
require_login()

API_BASE_URL = "http://localhost:8000/api"

st.title("🔍 Search Notes")
st.markdown("Find your notes using filters and semantic search")

# Render sidebar
render_sidebar_user_info()

# Initialize search state
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# Search Form
with st.form("search_form", clear_on_submit=False):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search query",
            placeholder="Enter keywords or ask a question... (e.g., 'meeting notes' or 'work tasks')",
            help="Leave empty to show all notes",
            key="search_query"
        )
    
    with col2:
        use_semantic = st.checkbox(
            "🧠 Semantic Search",
            value=False,
            help="Use AI-powered semantic search for better results"
        )
    
    # Filters
    st.markdown("**Filters:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        primary_tag = st.selectbox(
            "Category",
            ["All", "Work", "Personal", "Travel", "Ideas", "Projects", "Health", "Learning", "Finance", "Shopping", "Other"]
        )
    
    with col2:
        source = st.selectbox(
            "Source",
            ["All", "web", "telegram", "api"]
        )
    
    with col3:
        date_filter = st.selectbox(
            "Time Period",
            ["All time", "Today", "Last 7 days", "Last 30 days", "Custom"]
        )
    
    with col4:
        page_size = st.selectbox(
            "Results per page",
            [10, 20, 50, 100],
            index=0
        )
    
    # Custom date range
    start_date = None
    end_date = None
    if date_filter == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From")
        with col2:
            end_date = st.date_input("To")
    
    search_button = st.form_submit_button("🔍 Search", use_container_width=True)

# Perform search when button is clicked OR when page loads for the first time
if search_button or not st.session_state.search_performed:
    st.session_state.search_performed = True
    
    # Calculate date range
    end_dt = datetime.utcnow()
    start_dt = None
    
    if date_filter == "Today":
        start_dt = end_dt.replace(hour=0, minute=0, second=0)
    elif date_filter == "Last 7 days":
        start_dt = end_dt - timedelta(days=7)
    elif date_filter == "Last 30 days":
        start_dt = end_dt - timedelta(days=30)
    elif date_filter == "Custom" and start_date and end_date:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
    
    # Prepare search request
    search_params = {
        "query": query if query else None,
        "primary_tag": primary_tag if primary_tag != "All" else None,
        "source": source if source != "All" else None,
        "start_date": start_dt.isoformat() if start_dt else None,
        "end_date": end_dt.isoformat() if end_dt else None,
        "page": 1,
        "page_size": page_size,
        "use_semantic_search": use_semantic
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    with st.spinner("Searching..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/query/search",
                params={"user_id": st.session_state.user_id},
                json=search_params
            )
            
            if response.status_code == 200:
                results = response.json()
                notes = results.get('notes', [])
                total = results.get('total', 0)
                
                # Store results in session state
                st.session_state.search_results = notes
                st.session_state.total_results = total
            else:
                st.error(f"Search failed: {response.json().get('detail', 'Unknown error')}")
                st.session_state.search_results = []
                st.session_state.total_results = 0
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.search_results = []
            st.session_state.total_results = 0

# Display results from session state
if 'search_results' in st.session_state:
    notes = st.session_state.search_results
    total = st.session_state.total_results
    
    # Display results count
    if total > 0:
        st.markdown(f"### Found {total} notes")
    else:
        st.info("No notes found. Try adjusting your search filters or add some notes first!")
    
    if notes:
        # Remove duplicates based on note ID
        unique_notes = {}
        for note in notes:
            note_id = note.get('id')
            if note_id not in unique_notes:
                unique_notes[note_id] = note
        
        notes = list(unique_notes.values())
        
        # Display each note
        for idx, note in enumerate(notes):
            with st.container():
                # Header row
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    # Title with icon
                    icon = "🎤" if note['input_type'] == 'audio' else "💬"
                    st.markdown(f"### {icon} {note['title']}")
                
                with col2:
                    # Category badge with color
                    tag = note['primary_tag']
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
                    emoji = tag_colors.get(tag, "🏷️")
                    st.markdown(f"**{emoji} {tag}**")
                
                with col3:
                    # Priority
                    priority = note.get('priority', 'medium')
                    priority_emoji = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                    st.markdown(f"{priority_emoji} {priority.title()}")
                
                with col4:
                    # Date
                    created = datetime.fromisoformat(note['created_at'].replace('Z', '+00:00'))
                    st.markdown(f"📅 {created.strftime('%m/%d/%y')}")
                
                # Summary
                st.markdown(f"**Summary:** {note['summary']}")
                
                # Tags
                if note.get('secondary_tags'):
                    tags_str = " ".join([f"`{tag}`" for tag in note['secondary_tags'][:5]])
                    st.markdown(f"**Tags:** {tags_str}")
                
                # Expandable details
                with st.expander("📄 View Details"):
                    # Full content
                    content = note.get('transcription') or note.get('original_text', '')
                    if content:
                        st.markdown("**Full Content:**")
                        st.text_area("", content, height=100, key=f"content_{note['id']}_{idx}", disabled=True)
                    
                    # Action items
                    if note.get('actionable_items'):
                        st.markdown("**📌 Action Items:**")
                        for item in note['actionable_items']:
                            priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🟢"
                            deadline = f" (Due: {item['deadline']})" if item.get('deadline') else ""
                            st.markdown(f"{priority_emoji} {item['task']}{deadline}")
                    
                    # Entities
                    if note.get('key_entities'):
                        entities = note['key_entities']
                        if any(entities.values()):
                            st.markdown("**🔍 Key Entities:**")
                            
                            entity_parts = []
                            if entities.get('people'):
                                entity_parts.append(f"👥 {', '.join(entities['people'][:3])}")
                            if entities.get('places'):
                                entity_parts.append(f"📍 {', '.join(entities['places'][:3])}")
                            if entities.get('companies'):
                                entity_parts.append(f"🏢 {', '.join(entities['companies'][:3])}")
                            
                            for part in entity_parts:
                                st.markdown(f"- {part}")
                    
                    # Metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"Source: {note['source']}")
                    with col2:
                        st.caption(f"Sentiment: {note.get('sentiment', 'neutral')}")
                    with col3:
                        st.caption(f"Note ID: {note['id'][:8]}...")
                
                st.markdown("---")

# Quick search buttons
st.markdown("---")
st.subheader("🔎 Quick Searches")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔵 Work Notes", use_container_width=True):
        # Trigger search with Work filter
        st.session_state.search_performed = False
        st.rerun()

with col2:
    if st.button("🟢 Personal Notes", use_container_width=True):
        st.session_state.search_performed = False
        st.rerun()

with col3:
    if st.button("📅 Today's Notes", use_container_width=True):
        st.session_state.search_performed = False
        st.rerun()

with col4:
    if st.button("⭐ High Priority", use_container_width=True):
        st.session_state.search_performed = False
        st.rerun()

# Tips
st.markdown("---")
with st.expander("💡 Search Tips"):
    st.markdown("""
    **Search Techniques:**
    - Leave search empty to show all notes
    - Use specific keywords: "meeting", "project", "budget"
    - Try semantic search for similar meaning: "team discussion" finds "meeting notes"
    
    **Filters:**
    - Combine category + date filters for precise results
    - Use "Today" or "Last 7 days" for recent notes
    - Filter by source to find telegram or web notes
    
    **Quick Searches:**
    - Click the quick search buttons below for common searches
    - Results update immediately
    """)