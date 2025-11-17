"""
Search page - Search and filter notes
"""

import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Search Notes", page_icon="🔍", layout="wide")

API_BASE_URL = "http://localhost:8000/api"

if 'user_id' not in st.session_state:
    st.session_state.user_id = "test_user_001"

st.title("🔍 Search Notes")
st.markdown("Find your notes using filters and semantic search")

# Search Form
with st.form("search_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search query",
            placeholder="Enter keywords or ask a question... (e.g., 'meeting notes' or 'work tasks')",
            help="Leave empty to show all notes"
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

# Process search
if search_button or 'search_results' not in st.session_state:
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
                st.session_state.search_results = results
            else:
                st.error(f"Search failed: {response.json().get('detail', 'Unknown error')}")
                st.session_state.search_results = None
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.search_results = None

# Display results
if 'search_results' in st.session_state and st.session_state.search_results:
    results = st.session_state.search_results
    notes = results.get('notes', [])
    total = results.get('total', 0)
    
    st.markdown(f"### Found {total} notes")
    
    if notes:
        for note in notes:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Title with icon
                    icon = "🎤" if note['input_type'] == 'audio' else "💬"
                    st.markdown(f"### {icon} {note['title']}")
                
                with col2:
                    # Category badge
                    st.markdown(f"**🏷️ {note['primary_tag']}**")
                
                with col3:
                    # Date
                    created = datetime.fromisoformat(note['created_at'].replace('Z', '+00:00'))
                    st.markdown(f"📅 {created.strftime('%Y-%m-%d')}")
                
                # Summary
                st.markdown(note['summary'])
                
                # Tags
                if note.get('secondary_tags'):
                    tags_str = " ".join([f"`{tag}`" for tag in note['secondary_tags']])
                    st.markdown(f"**Tags:** {tags_str}")
                
                # Action items
                if note.get('actionable_items'):
                    with st.expander("📌 Action Items"):
                        for item in note['actionable_items']:
                            priority_emoji = "🔴" if item['priority'] == 'high' else "🟡" if item['priority'] == 'medium' else "🟢"
                            deadline = f" (Due: {item['deadline']})" if item.get('deadline') else ""
                            st.markdown(f"{priority_emoji} {item['task']}{deadline}")
                
                # Full content
                with st.expander("📄 Full Content"):
                    content = note.get('transcription') or note.get('original_text', '')
                    st.text(content)
                    
                    # Entities
                    if note.get('key_entities'):
                        entities = note['key_entities']
                        if any(entities.values()):
                            st.markdown("**🔍 Key Entities:**")
                            
                            entity_parts = []
                            if entities.get('people'):
                                entity_parts.append(f"👥 {', '.join(entities['people'])}")
                            if entities.get('places'):
                                entity_parts.append(f"📍 {', '.join(entities['places'])}")
                            if entities.get('companies'):
                                entity_parts.append(f"🏢 {', '.join(entities['companies'])}")
                            
                            for part in entity_parts:
                                st.markdown(f"- {part}")
                
                st.markdown("---")
    else:
        st.info("No notes found matching your search criteria.")
else:
    st.info("👆 Use the search form above to find your notes")