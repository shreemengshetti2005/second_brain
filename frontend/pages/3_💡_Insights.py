"""
Insights page - AI-powered insights and analytics
"""
# Add to: 1_Add_Note.py, 2_Search.py, 3_Insights.py, 4_Settings.py, 5_Google_Drive.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import require_login, render_sidebar_user_info

# Check authentication
require_login()

# Then in the sidebar section, add:
render_sidebar_user_info()

import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Insights", page_icon="💡", layout="wide")

API_BASE_URL = "http://localhost:8000/api"

if 'user_id' not in st.session_state:
    st.session_state.user_id = "test_user_001"

st.title("💡 AI-Powered Insights")
st.markdown("Get intelligent summaries and insights from your notes")

# Query form
st.subheader("Ask a Question")

with st.form("insight_form"):
    query = st.text_area(
        "What would you like to know?",
        placeholder="Examples:\n- Summarize all Work notes from last week\n- What are my pending action items?\n- Show me my travel ideas\n- What projects am I working on?",
        height=100
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        primary_tag = st.selectbox(
            "Filter by Category (optional)",
            ["All", "Work", "Personal", "Travel", "Ideas", "Projects", "Health", "Learning", "Finance", "Shopping"]
        )
    
    with col2:
        date_range = st.selectbox(
            "Time Period",
            ["Last 7 days", "Last 30 days", "Last 3 months", "All time"]
        )
    
    with col3:
        max_notes = st.slider(
            "Max notes to analyze",
            min_value=10,
            max_value=100,
            value=50,
            step=10
        )
    
    generate_button = st.form_submit_button("🔮 Generate Insights", use_container_width=True)

# Process insights
if generate_button:
    if not query.strip():
        st.error("Please enter a question!")
    else:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = None
        
        if date_range == "Last 7 days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "Last 30 days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "Last 3 months":
            start_date = end_date - timedelta(days=90)
        
        insight_request = {
            "query": query,
            "primary_tag": primary_tag if primary_tag != "All" else None,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat(),
            "max_notes": max_notes
        }
        
        # Remove None values
        insight_request = {k: v for k, v in insight_request.items() if v is not None}
        
        with st.spinner("🤔 Analyzing your notes... This may take a moment."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/insights/generate",
                    params={"user_id": st.session_state.user_id},
                    json=insight_request
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success(f"✅ Analyzed {result['notes_analyzed']} notes")
                    
                    # Display insight
                    st.markdown("---")
                    st.subheader("🎯 Insight")
                    st.markdown(result['insight'])
                    
                    # Summary points
                    if result.get('summary_points'):
                        st.markdown("---")
                        st.subheader("📝 Key Points")
                        for point in result['summary_points']:
                            st.markdown(f"- {point}")
                    
                    # Action items
                    if result.get('action_items'):
                        st.markdown("---")
                        st.subheader("📌 Action Items")
                        for item in result['action_items']:
                            st.markdown(f"- [ ] {item}")
                    
                    # Related notes
                    if result.get('related_notes'):
                        st.markdown("---")
                        with st.expander(f"📚 Related Notes ({len(result['related_notes'])})"):
                            st.markdown("The following notes were analyzed:")
                            for note_id in result['related_notes']:
                                st.markdown(f"- Note ID: `{note_id}`")
                
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")

# Predefined queries
st.markdown("---")
st.subheader("💡 Quick Queries")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Weekly Summary", use_container_width=True):
        st.session_state.quick_query = "Summarize all my notes from the past week"
        st.rerun()

with col2:
    if st.button("✅ Action Items", use_container_width=True):
        st.session_state.quick_query = "List all my pending action items and tasks"
        st.rerun()

with col3:
    if st.button("🎯 Work Focus", use_container_width=True):
        st.session_state.quick_query = "What are the main work-related topics I've been focusing on?"
        st.rerun()

# Sample queries
st.markdown("---")
with st.expander("📖 Example Queries"):
    st.markdown("""
    **General Summaries:**
    - "Summarize all Work notes from last week"
    - "What have I been thinking about lately?"
    - "Give me highlights from this month"
    
    **Action Items:**
    - "What are my pending action items?"
    - "Show me high priority tasks"
    - "What deadlines do I have coming up?"
    
    **Category-Specific:**
    - "What are my travel ideas?"
    - "Summarize my learning progress"
    - "What personal goals have I set?"
    
    **People & Relationships:**
    - "Who have I been meeting with?"
    - "Show me notes mentioning Sarah"
    
    **Projects & Ideas:**
    - "What projects am I working on?"
    - "Show me all my app ideas"
    - "Summarize project discussions"
    """)