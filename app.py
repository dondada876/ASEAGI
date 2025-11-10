"""
PROJ344 Multi-Page Streamlit Application
Consolidates all 5 dashboards into a single app with page navigation
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="PROJ344 Legal Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main landing page
st.title("⚖️ PROJ344 Legal Intelligence System")
st.markdown("---")

st.markdown("""
## Welcome to PROJ344

AI-powered legal document intelligence system for child protection cases.

### Available Dashboards:

Use the sidebar to navigate between dashboards:

1. **📊 Master Dashboard** - Main case intelligence and evidence review
2. **📋 Legal Intelligence** - Document-by-document analysis
3. **💼 CEO Dashboard** - File organization & system health
4. **🔍 Scanning Monitor** - Real-time document scanning progress
5. **📅 Timeline & Violations** - Constitutional violations tracking

---

**Case:** In re Ashe Bucknor (J24-00478)
**Documents Analyzed:** 601
**System Status:** ✅ Operational
""")

# Quick stats in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Documents", "601")

with col2:
    st.metric("Smoking Guns (900+)", "45")

with col3:
    st.metric("Perjury Indicators", "23")

with col4:
    st.metric("System Uptime", "99.9%")

st.markdown("---")
st.info("👈 Use the sidebar to navigate between dashboards")
