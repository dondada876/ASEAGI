"""
CEO Dashboard - Quick Access to Your Priority Tasks
Run: streamlit run ceo_dashboard.py
Access from any device on your network: http://YOUR_MAC_IP:8501
"""

import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="CEO Command Center",
    page_icon="🎯",
    layout="wide"
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

# Title
st.title("🎯 CEO Command Center")
st.markdown(f"**Don's Mission Dashboard** | {datetime.now().strftime('%A, %B %d, %Y')}")

# Sidebar
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select View", [
    "🔥 Urgent Items",
    "👨‍👧 Family & Legal",
    "💼 Business Priorities",
    "⏱️ Pomodoro Tracker",
    "➕ Add New Task"
])

# Helper function to get data
def get_urgent_items():
    result = supabase.rpc('get_ceo_urgent_items').execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame()

def get_all_tasks():
    result = supabase.table('files').select('*').is_('deleted_at', 'null').execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame()

def get_family_tasks():
    result = supabase.table('files').select('*').like('department_code', '#CH29%').is_('deleted_at', 'null').execute()
    return pd.DataFrame(result.data) if result.data else pd.DataFrame()

# URGENT ITEMS VIEW
if view == "🔥 Urgent Items":
    st.header("Today's Critical Priorities")
    
    df = get_urgent_items()
    
    if not df.empty:
        # Show summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Urgent", len(df))
        with col2:
            p1_count = len(df[df['priority'] == '#P1']) if 'priority' in df.columns else 0
            st.metric("#P1 Priority", p1_count)
        with col3:
            total_pomos = df['pomodoro_estimate'].sum() if 'pomodoro_estimate' in df.columns else 0
            st.metric("Est. Pomodoros", int(total_pomos))
        
        st.markdown("---")
        
        # Display tasks
        for _, row in df.iterrows():
            with st.expander(f"{row['priority']} - {row['filename']}", expanded=True):
                st.write(f"**Department:** {row['department']}")
                st.write(f"**Status:** {row['status']}")
                st.write(f"**Description:** {row['description']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Start Working", key=f"start_{row['id']}"):
                        supabase.table('files').update({
                            'status': '#S2',
                            'last_accessed': datetime.now().isoformat()
                        }).eq('id', row['id']).execute()
                        st.success("Task started!")
                        st.rerun()
                
                with col2:
                    if st.button(f"Complete Pomodoro", key=f"pomo_{row['id']}"):
                        current = row.get('pomodoro_completed', 0)
                        supabase.table('files').update({
                            'pomodoro_completed': current + 1,
                            'actual_minutes': (row.get('actual_minutes', 0) or 0) + 25,
                            'last_accessed': datetime.now().isoformat()
                        }).eq('id', row['id']).execute()
                        st.success("Pomodoro logged!")
                        st.rerun()
    else:
        st.info("No urgent items found. Great job!")

# FAMILY & LEGAL VIEW
elif view == "👨‍👧 Family & Legal":
    st.header("Father's Mission: Ashe Priorities")
    
    df = get_family_tasks()
    
    if not df.empty:
        # Filter by subdepartment
        dept_filter = st.selectbox("Filter by:", [
            "All",
            "#CH29.5 - Legal Affairs",
            "#CH29.6 - Child Development",
            "#CH29.7 - Childcare",
            "#CH29.8 - Family Events"
        ])
        
        if dept_filter != "All":
            dept_code = dept_filter.split(" - ")[0]
            df = df[df['department_code'] == dept_code]
        
        st.markdown(f"**{len(df)} tasks** | All automatically private & secure 🔒")
        
        for _, row in df.iterrows():
            is_legal = row['department_code'] == '#CH29.5'
            icon = "⚖️" if is_legal else "👧"
            
            with st.expander(f"{icon} {row['priority']} - {row['filename']}"):
                st.write(f"**Description:** {row['description']}")
                st.write(f"**Status:** {row['status']}")
                
                if row.get('pomodoro_estimate'):
                    completed = row.get('pomodoro_completed', 0)
                    total = row['pomodoro_estimate']
                    progress = (completed / total) * 100 if total > 0 else 0
                    st.progress(progress / 100)
                    st.write(f"Progress: {completed}/{total} Pomodoros ({progress:.0f}%)")
    else:
        st.warning("No family/legal tasks found. Add some priorities!")

# BUSINESS PRIORITIES VIEW
elif view == "💼 Business Priorities":
    st.header("Revenue Generation & Operations")
    
    df = get_all_tasks()
    
    if not df.empty:
        # Filter out family/personal
        df = df[~df['department_code'].str.startswith('#CH28')]
        df = df[~df['department_code'].str.startswith('#CH29')]
        
        # Show by priority
        priority_filter = st.selectbox("Filter by Priority:", ["All", "#P1", "#P2", "#P3", "#P4"])
        
        if priority_filter != "All":
            df = df[df['priority'] == priority_filter]
        
        st.markdown(f"**{len(df)} business tasks**")
        
        # Group by department
        for dept in df['department_code'].unique():
            dept_tasks = df[df['department_code'] == dept]
            
            with st.expander(f"{dept} ({len(dept_tasks)} tasks)"):
                for _, row in dept_tasks.iterrows():
                    st.markdown(f"**{row['filename']}** - {row['priority']}")
                    st.write(row['description'])
                    st.write(f"Status: {row['status']} | Energy: {row.get('energy_level', 'N/A')}")
                    st.markdown("---")
    else:
        st.info("No business tasks found.")

# POMODORO TRACKER VIEW
elif view == "⏱️ Pomodoro Tracker":
    st.header("Pomodoro Productivity Tracking")
    
    df = get_all_tasks()
    
    if not df.empty and 'pomodoro_estimate' in df.columns:
        # Summary stats
        total_estimated = df['pomodoro_estimate'].sum()
        total_completed = df['pomodoro_completed'].sum()
        total_time = df['actual_minutes'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Estimated", f"{int(total_estimated)} 🍅")
        with col2:
            st.metric("Completed", f"{int(total_completed)} 🍅")
        with col3:
            completion_pct = (total_completed / total_estimated * 100) if total_estimated > 0 else 0
            st.metric("Progress", f"{completion_pct:.1f}%")
        with col4:
            hours = total_time / 60 if total_time else 0
            st.metric("Time Spent", f"{hours:.1f}h")
        
        st.markdown("---")
        
        # Show tasks with progress bars
        active_tasks = df[df['status'].isin(['#S1', '#S2', '#S3'])]
        
        st.subheader("Active Tasks")
        for _, row in active_tasks.iterrows():
            completed = row.get('pomodoro_completed', 0)
            total = row.get('pomodoro_estimate', 1)
            progress = (completed / total) if total > 0 else 0
            
            st.write(f"**{row['filename']}** ({row['department_code']})")
            st.progress(progress)
            st.write(f"{completed}/{total} Pomodoros - {row.get('actual_minutes', 0)} minutes")
            st.markdown("---")
    else:
        st.info("No Pomodoro data yet. Start tracking!")

# ADD NEW TASK VIEW
elif view == "➕ Add New Task":
    st.header("Quick Task Capture")
    
    with st.form("new_task_form"):
        filename = st.text_input("Task Name", placeholder="Call_Attorney_Smith.txt")
        
        col1, col2 = st.columns(2)
        with col1:
            dept = st.selectbox("Department", [
                "#CH29.5 - Legal Affairs",
                "#CH29.6 - Child Development",
                "#CH02.1 - Market Analysis",
                "#CH03.1 - Sales Strategy",
                "#CH01.1 - Strategic Planning"
            ])
        with col2:
            priority = st.selectbox("Priority", ["#P1", "#P2", "#P3", "#P4"])
        
        description = st.text_area("Description", placeholder="What needs to be done?")
        
        col1, col2 = st.columns(2)
        with col1:
            energy = st.selectbox("Energy Level", ["#E1", "#E2", "#E3", "#E4", "#E5"])
        with col2:
            pomodoros = st.number_input("Estimated Pomodoros", min_value=1, max_value=20, value=2)
        
        submitted = st.form_submit_button("Add Task")
        
        if submitted and filename and description:
            dept_code = dept.split(" - ")[0]
            dept_name = dept.split(" - ")[1]
            
            data = {
                'filename': filename,
                'filepath': f'/quick/{filename}',
                'department_code': dept_code,
                'department_name': dept_name,
                'priority': priority,
                'status': '#S1',
                'energy_level': energy,
                'task_identifier': f'#TASK{datetime.now().strftime("%m%d%H%M")}',
                'pomodoro_estimate': pomodoros,
                'estimated_minutes': pomodoros * 25,
                'description': description,
                'category': 'Quick Capture'
            }
            
            result = supabase.table('files').insert(data).execute()
            
            if result.data:
                st.success(f"✅ Task '{filename}' added successfully!")
                st.balloons()
            else:
                st.error("Failed to add task. Check console for errors.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**CEO Dashboard v1.0**")
st.sidebar.markdown("*Execute with precision.*")
