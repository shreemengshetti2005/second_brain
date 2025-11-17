"""
Main Streamlit app - Home Dashboard
"""

import sys
import os

# Add utils path
sys.path.append(os.path.dirname(__file__))

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

# Check authentication
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Please login to continue")
    st.info("👉 Go to the **Login** page from the sidebar")
    st.stop()


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
st.markdown(f"### Welcome back, {st.session_state.get('user_name', 'User')}! 👋")

# Sidebar with user info
with st.sidebar:
    st.header("👤 Account")
    st.markdown(f"**{st.session_state.get('user_name', 'User')}**")
    st.caption(st.session_state.get('user_email', ''))
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.success("👋 Logged out successfully!")
        st.info("Please navigate to the Login page to sign in again.")
        st.stop()
    
    st.divider()
    
    st.markdown("### 📊 Quick Stats")
    analytics = get_analytics(st.session_state.user_id, days=30)
    
    if analytics:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Notes", analytics.get("total_notes", 0))
        with col2:
            st.metric("Action Items", analytics.get("pending_action_items", 0))
    
    st.divider()
    
    # Quick info
    st.markdown("### ⚡ Quick Tips")
    st.info("""
    **Navigation:**
    - 📝 Add Note - Create notes
    - 🔍 Search - Find notes
    - 💡 Insights - AI analysis
    - ⚙️ Settings - Preferences
    """)

# Main Content
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Recent Notes", "✅ Action Items"])

with tab1:
    st.header("Dashboard Overview")
    
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
                    title="Category Distribution",
                    hole=0.3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📝 No notes yet. Start by adding your first note!")
        
        with col2:
            st.subheader("⏰ Activity by Hour")
            activity = analytics.get("activity_by_hour", [])
            
            if activity:
                hours = [item["hour"] for item in activity]
                counts = [item["count"] for item in activity]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=hours, 
                        y=counts,
                        marker_color='rgb(55, 83, 109)'
                    )
                ])
                fig.update_layout(
                    title="Notes Created by Hour",
                    xaxis_title="Hour of Day",
                    yaxis_title="Number of Notes",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⏰ No activity data yet")
        
        # Top entities
        st.subheader("🔍 Top Mentioned Entities")
        top_entities = analytics.get("top_entities", [])
        
        if top_entities:
            entity_col1, entity_col2, entity_col3 = st.columns(3)
            
            people = [e for e in top_entities if e["type"] == "people"]
            places = [e for e in top_entities if e["type"] == "places"]
            companies = [e for e in top_entities if e["type"] == "companies"]
            
            with entity_col1:
                st.markdown("**👥 People**")
                if people:
                    for entity in people[:5]:
                        st.markdown(f"- {entity['name']} ({entity['count']})")
                else:
                    st.caption("No people mentioned yet")
            
            with entity_col2:
                st.markdown("**📍 Places**")
                if places:
                    for entity in places[:5]:
                        st.markdown(f"- {entity['name']} ({entity['count']})")
                else:
                    st.caption("No places mentioned yet")
            
            with entity_col3:
                st.markdown("**🏢 Companies**")
                if companies:
                    for entity in companies[:5]:
                        st.markdown(f"- {entity['name']} ({entity['count']})")
                else:
                    st.caption("No companies mentioned yet")
        else:
            st.info("🔍 No entities extracted yet. Add more detailed notes to see insights!")
    else:
        # Welcome message for new users
        st.info("""
        ### 👋 Welcome to Second Brain Agent!
        
        You don't have any notes yet. Let's get started:
        
        1. 📝 **Add a Note** - Create your first text or voice note
        2. 🏷️ **AI Categories** - Watch as AI automatically organizes your thoughts
        3. 🔍 **Search & Discover** - Find your notes using semantic search
        4. 💡 **Get Insights** - Ask questions about your notes
        
        Navigate to "Add Note" page from the sidebar to begin! 🚀
        """)
        
        # Show quick start guide
        with st.expander("📖 Quick Start Guide"):
            st.markdown("""
            **How to use Second Brain Agent:**
            
            **1. Adding Notes**
            - Go to **Add Note** page
            - Choose text or audio input
            - AI will automatically categorize and extract insights
            
            **2. Searching Notes**
            - Go to **Search** page
            - Use filters or semantic search
            - Find notes by category, date, or content
            
            **3. Getting Insights**
            - Go to **Insights** page
            - Ask questions about your notes
            - Get AI-powered summaries and analysis
            
            **4. Integrations**
            - Connect Telegram for voice messages
            - Export to Google Drive
            - Configure in Settings
            """)

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
                
                if note.get('secondary_tags'):
                    tags_str = " ".join([f"`{tag}`" for tag in note['secondary_tags']])
                    st.markdown(f"**Tags:** {tags_str}")
                
                if note.get('actionable_items'):
                    st.markdown("**📌 Action Items:**")
                    for item in note['actionable_items']:
                        priority = item.get('priority', 'medium')
                        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                        st.markdown(f"{emoji} {item['task']}")
                
                # Show sentiment and priority
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Sentiment: {note.get('sentiment', 'N/A')}")
                with col2:
                    st.caption(f"Priority: {note.get('priority', 'N/A')}")
    else:
        st.info("📝 No notes yet. Go to 'Add Note' page to create your first note!")
        
        st.markdown("### 💡 Tips for your first note:")
        st.markdown("""
        - Try: "Team meeting tomorrow at 10 AM to discuss Q4 goals"
        - Or: "Buy groceries: milk, eggs, bread"
        - Or: Record a voice note about your day
        """)

with tab3:
    st.header("Action Items")
    
    action_items = get_action_items(st.session_state.user_id)
    
    if action_items:
        # Summary stats
        total_items = len(action_items)
        high_count = len([i for i in action_items if i.get('priority') == 'high'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", total_items)
        with col2:
            st.metric("High Priority", high_count)
        with col3:
            st.metric("Completion", "0%")
        
        st.divider()
        
        # Group by priority
        high_priority = [item for item in action_items if item.get('priority') == 'high']
        medium_priority = [item for item in action_items if item.get('priority') == 'medium']
        low_priority = [item for item in action_items if item.get('priority') == 'low']
        
        if high_priority:
            st.subheader("🔴 High Priority")
            for idx, item in enumerate(high_priority):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{idx+1}. {item['task']}**")
                    st.caption(f"From: {item['note_title']} | Deadline: {item.get('deadline', 'No deadline')}")
                with col2:
                    st.checkbox("Done", key=f"high_{item['note_id']}_{idx}")
            st.divider()
        
        if medium_priority:
            st.subheader("🟡 Medium Priority")
            for idx, item in enumerate(medium_priority):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{idx+1}. {item['task']}")
                    st.caption(f"From: {item['note_title']}")
                with col2:
                    st.checkbox("Done", key=f"med_{item['note_id']}_{idx}")
            st.divider()
        
        if low_priority:
            st.subheader("🟢 Low Priority")
            for idx, item in enumerate(low_priority):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{idx+1}. {item['task']}")
                    st.caption(f"From: {item['note_title']}")
                with col2:
                    st.checkbox("Done", key=f"low_{item['note_id']}_{idx}")
    else:
        st.success("🎉 No pending action items! You're all caught up!")
        
        st.markdown("### 💡 Action items are automatically extracted from:")
        st.markdown("""
        - Notes with tasks or to-dos
        - Meeting notes with action points
        - Project plans with deliverables
        - Any note mentioning deadlines or responsibilities
        """)

# Footer
st.divider()
st.markdown(
    f"""
    <div style='text-align: center; color: #666;'>
        <p>🧠 Second Brain Agent | Built with FastAPI, Streamlit & Google Cloud AI</p>
        <p style='font-size: 0.8em;'>Logged in as: {st.session_state.get('user_email', 'Unknown')}</p>
    </div>
    """,
    unsafe_allow_html=True
)