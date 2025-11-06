"""
PROJ344 Dashboard Styling Module
Consistent UI/UX across all dashboards with professional legal theme
"""

import streamlit as st

def inject_custom_css():
    """Inject custom CSS for professional legal case intelligence dashboard"""
    st.markdown("""
    <style>
    /* ============================================
       PROJ344 Professional Legal Theme
       ============================================ */

    /* Main container styling */
    .main {
        background-color: #F8FAFC;
        padding: 2rem;
    }

    /* Header styling */
    h1 {
        color: #1E3A8A;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.5rem;
    }

    h2 {
        color: #1E40AF;
        font-weight: 600;
        margin-top: 2rem;
    }

    h3 {
        color: #1E293B;
        font-weight: 500;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
    }

    /* High priority alert styling */
    .priority-high {
        background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #991B1B;
        box-shadow: 0 4px 6px rgba(220, 38, 38, 0.2);
    }

    .priority-medium {
        background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
        color: #78350F;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #92400E;
        box-shadow: 0 4px 6px rgba(245, 158, 11, 0.2);
    }

    .priority-low {
        background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #047857;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }

    /* Document cards */
    .document-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }

    .document-card:hover {
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
        border-color: #3B82F6;
    }

    /* Timeline styling */
    .timeline-event {
        position: relative;
        padding-left: 2rem;
        margin-bottom: 2rem;
        border-left: 3px solid #3B82F6;
    }

    .timeline-event::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 0;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #3B82F6;
        border: 3px solid white;
        box-shadow: 0 0 0 2px #3B82F6;
    }

    .timeline-date {
        font-weight: 600;
        color: #3B82F6;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Fraud/perjury indicators */
    .fraud-indicator {
        background: #FEF2F2;
        border: 2px solid #DC2626;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }

    .fraud-indicator-title {
        color: #DC2626;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    /* Score badges */
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }

    .score-critical {
        background: #DC2626;
        color: white;
    }

    .score-high {
        background: #F59E0B;
        color: white;
    }

    .score-medium {
        background: #3B82F6;
        color: white;
    }

    .score-low {
        background: #64748B;
        color: white;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #E2E8F0 !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        box-shadow: 0 6px 8px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }

    /* Data table styling */
    .dataframe {
        border: 1px solid #E2E8F0 !important;
        border-radius: 0.5rem;
        overflow: hidden;
    }

    .dataframe th {
        background: #1E3A8A !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.875rem;
        letter-spacing: 0.05em;
        padding: 1rem !important;
    }

    .dataframe td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid #F1F5F9 !important;
    }

    .dataframe tr:hover {
        background: #F8FAFC !important;
    }

    /* Alert boxes */
    .alert-success {
        background: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .alert-warning {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .alert-error {
        background: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .alert-info {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #64748B;
        font-size: 0.875rem;
        border-top: 1px solid #E2E8F0;
        margin-top: 4rem;
    }

    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #3B82F6 !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 0.5rem;
        font-weight: 600;
        color: #1E3A8A;
    }

    .streamlit-expanderHeader:hover {
        background: #F8FAFC;
        border-color: #3B82F6;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }

    ::-webkit-scrollbar-thumb {
        background: #94A3B8;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #64748B;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }

        .document-card {
            padding: 1rem;
        }

        .timeline-event {
            padding-left: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(title, subtitle=None, icon=None):
    """Render styled dashboard header"""
    icon_html = f'<span style="margin-right: 1rem;">{icon}</span>' if icon else ''

    html = f"""
    <div style="margin-bottom: 2rem;">
        <h1>{icon_html}{title}</h1>
        {f'<p style="color: #64748B; font-size: 1.1rem; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label, value, delta=None, priority="normal"):
    """Render styled metric card with priority indicator"""
    priority_colors = {
        "critical": "#DC2626",
        "high": "#F59E0B",
        "medium": "#3B82F6",
        "normal": "#64748B"
    }

    color = priority_colors.get(priority, "#64748B")
    delta_html = f'<div style="color: {color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>' if delta else ''

    html = f"""
    <div class="document-card">
        <div style="color: #64748B; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
            {label}
        </div>
        <div style="color: {color}; font-size: 2rem; font-weight: 700;">
            {value}
        </div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_document_card(title, date, rel_score, doc_type, summary, file_link=None):
    """Render document card with all metadata"""

    # Score badge color
    if rel_score >= 900:
        badge_class = "score-critical"
    elif rel_score >= 700:
        badge_class = "score-high"
    elif rel_score >= 500:
        badge_class = "score-medium"
    else:
        badge_class = "score-low"

    link_html = f'<a href="{file_link}" target="_blank" style="color: #3B82F6; text-decoration: none; font-weight: 600;">📄 View Document</a>' if file_link else ''

    html = f"""
    <div class="document-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #1E3A8A;">{title}</h3>
                <div style="color: #64748B; font-size: 0.875rem; margin-top: 0.25rem;">
                    {date} • {doc_type}
                </div>
            </div>
            <span class="score-badge {badge_class}">REL-{rel_score}</span>
        </div>
        <p style="color: #475569; margin: 1rem 0;">{summary}</p>
        {link_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_timeline_event(date, title, description, event_type="default"):
    """Render timeline event with styling"""
    html = f"""
    <div class="timeline-event">
        <div class="timeline-date">{date}</div>
        <h4 style="margin: 0.5rem 0; color: #1E3A8A;">{title}</h4>
        <p style="color: #475569; margin: 0.5rem 0 0 0;">{description}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_fraud_indicator(title, description, evidence):
    """Render fraud/perjury indicator"""
    html = f"""
    <div class="fraud-indicator">
        <div class="fraud-indicator-title">⚠️ {title}</div>
        <p style="color: #7F1D1D; margin: 0.5rem 0;">{description}</p>
        <div style="background: white; padding: 0.75rem; border-radius: 0.375rem; margin-top: 0.75rem;">
            <strong style="color: #991B1B;">Evidence:</strong>
            <p style="color: #1E293B; margin: 0.5rem 0 0 0;">{evidence}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_alert(message, alert_type="info"):
    """Render styled alert box"""
    html = f"""
    <div class="alert-{alert_type}">
        {message}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_footer():
    """Render dashboard footer"""
    html = """
    <div class="footer">
        <strong>PROJ344: Legal Case Intelligence Dashboard</strong><br>
        Powered by Claude AI • Supabase • n8n • Streamlit<br>
        <em>Confidential - Attorney Work Product</em>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
