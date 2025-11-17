"""
Main Streamlit app - Home Dashboard
"""

import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Second Brain Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = "test_user_001"


def get_analytics(user_id: str, days: int = 30):
    """Get analytics data from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/insights/analytics",
            params={"user_id": user_id, "days": days}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching analytics: {e}")
        return None


def get_recent_notes(user_id: str, limit: int = 5):
    """Get recent notes from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/query/recent",
            params={"user_id": user_id, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching recent notes: {e}")
        return []


def get_action_items(user_id: str):
    """Get action items from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/insights/action-items",
            params={"user_id": user_id, "limit": 10}
        )
        if response.status_code == 200:
            return response.json().get("action_items", [])
        return []
    except Exception as e:
        st.error(f"Error fetching action items: {e}")
        return []


# Main App
st.title("🧠 Second Brain Agent")
st.markdown("### Your AI-Powered Note-Taking System")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.user_id = st.text_input(
        "User ID",
        value=st.session_state.user_id,
        help="Enter your user ID"
    )
    
    st.divider()
    
    st.markdown("### 📊 Quick Stats")
    analytics = get_analytics(st.session_state.user_id, days=30)
    
    if analytics:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Notes", analytics.get("total_notes", 0))
        with col2:
            st.metric("Action Items", analytics.get("pending_action_items", 0))

# Main Content
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Recent Notes", "✅ Action Items"])

with tab1:
    st.header("Dashboard")
    
    analytics = get_analytics(st.session_state.user_id, days=30)
    
    if analytics:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📝 Total Notes",
                analytics.get("total_notes", 0),
                help="Total notes in the last 30 days"
            )
        
        with col2:
            notes_by_type = analytics.get("notes_by_type", {})
            audio_count = notes_by_type.get("audio", 0)
            st.metric(
                "🎤 Audio Notes",
                audio_count
            )
        
        with col3:
            text_count = notes_by_type.get("text", 0)
            st.metric(
                "💬 Text Notes",
                text_count
            )
        
        with col4:
            st.metric(
                "⚡ Action Items",
                analytics.get("pending_action_items", 0)
            )
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Notes by Category")
            tag_dist = analytics.get("tag_distribution", [])
            
            if tag_dist:
                tags = [item["tag"] for item in tag_dist]
                counts = [item["count"] for item in tag_dist]
                
                fig = px.pie(
                    values=counts,
                    names=tags,
                    title="Category Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No notes yet")
        
        with col2:
            st.subheader("⏰ Activity by Hour")
            activity = analytics.get("activity_by_hour", [])
            
            if activity:
                hours = [item["hour"] for item in activity]
                counts = [item["count"] for item in activity]
                
                fig = go.Figure(data=[
                    go.Bar(x=hours, y=counts)
                ])
                fig.update_layout(
                    title="Notes Created by Hour",
                    xaxis_title="Hour of Day",
                    yaxis_title="Number of Notes"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No activity data yet")
        
        # Top entities
        st.subheader("🔍 Top Mentioned")
        top_entities = analytics.get("top_entities", [])
        
        if top_entities:
            entity_col1, entity_col2, entity_col3 = st.columns(3)
            
            people = [e for e in top_entities if e["type"] == "people"]
            places = [e for e in top_entities if e["type"] == "places"]
            companies = [e for e in top_entities if e["type"] == "companies"]
            
            with entity_col1:
                st.markdown("**👥 People**")
                for entity in people[:5]:
                    st.markdown(f"- {entity['name']} ({entity['count']})")
            
            with entity_col2:
                st.markdown("**📍 Places**")
                for entity in places[:5]:
                    st.markdown(f"- {entity['name']} ({entity['count']})")
            
            with entity_col3:
                st.markdown("**🏢 Companies**")
                for entity in companies[:5]:
                    st.markdown(f"- {entity['name']} ({entity['count']})")
    else:
        st.info("No analytics data available yet. Start adding notes!")

with tab2:
    st.header("Recent Notes")
    
    recent_notes = get_recent_notes(st.session_state.user_id, limit=10)
    
    if recent_notes:
        for note in recent_notes:
            with st.expander(
                f"{'🎤' if note['input_type'] == 'audio' else '💬'} {note['title']}"
            ):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Category:** {note['primary_tag']}")
                
                with col2:
                    st.markdown(f"**Source:** {note['source']}")
                
                with col3:
                    created = datetime.fromisoformat(note['created_at'].replace('Z', '+00:00'))
                    st.markdown(f"**Date:** {created.strftime('%Y-%m-%d')}")
                
                st.markdown(f"**Summary:** {note['summary']}")
                
                if note.get('actionable_items'):
                    st.markdown("**Action Items:**")
                    for item in note['actionable_items']:
                        priority = item.get('priority', 'medium')
                        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                        st.markdown(f"{emoji} {item['task']}")
    else:
        st.info("No notes yet. Go to 'Add Note' page to create your first note!")

with tab3:
    st.header("Action Items")
    
    action_items = get_action_items(st.session_state.user_id)
    
    if action_items:
        # Group by priority
        high_priority = [item for item in action_items if item.get('priority') == 'high']
        medium_priority = [item for item in action_items if item.get('priority') == 'medium']
        low_priority = [item for item in action_items if item.get('priority') == 'low']
        
        if high_priority:
            st.subheader("🔴 High Priority")
            for item in high_priority:
                st.markdown(f"- **{item['task']}**")
                st.caption(f"From: {item['note_title']} | Deadline: {item.get('deadline', 'No deadline')}")
        
        if medium_priority:
            st.subheader("🟡 Medium Priority")
            for item in medium_priority:
                st.markdown(f"- {item['task']}")
                st.caption(f"From: {item['note_title']}")
        
        if low_priority:
            st.subheader("🟢 Low Priority")
            for item in low_priority:
                st.markdown(f"- {item['task']}")
                st.caption(f"From: {item['note_title']}")
    else:
        st.success("🎉 No pending action items!")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center'>
        <p>🧠 Second Brain Agent | Built with FastAPI, Streamlit & Google Cloud AI</p>
    </div>
    """,
    unsafe_allow_html=True
)