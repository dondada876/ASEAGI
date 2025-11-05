"""
Error Log Uploader and Analyzer Dashboard
Upload, analyze, and visualize error logs with advanced filtering and statistics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import re
import os
from collections import Counter
from proj344_style import inject_custom_css, render_header, render_alert

# Page configuration
st.set_page_config(
    page_title="Error Log Uploader & Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()

# Custom CSS for error log specific styling
st.markdown("""
<style>
.error-critical {
    background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
    color: white;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 5px solid #7F1D1D;
}

.error-error {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    color: white;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 5px solid #92400E;
}

.error-warning {
    background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%);
    color: #78350F;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 5px solid #B45309;
}

.error-info {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
    color: white;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 5px solid #1D4ED8;
}

.log-entry {
    font-family: 'Courier New', monospace;
    background: #1E293B;
    color: #E2E8F0;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    overflow-x: auto;
    font-size: 0.875rem;
}

.stat-card {
    background: white;
    border-radius: 0.75rem;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    border: 2px solid #E2E8F0;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
    border-color: #3B82F6;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0.5rem 0;
}

.stat-label {
    font-size: 0.875rem;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def parse_log_file(content, file_type):
    """Parse different log file formats"""
    errors = []

    if file_type == "json":
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
        except json.JSONDecodeError:
            st.error("Invalid JSON format")
            return []

    elif file_type == "csv":
        try:
            import io
            df = pd.read_csv(io.StringIO(content))
            return df.to_dict('records')
        except Exception as e:
            st.error(f"Error parsing CSV: {e}")
            return []

    else:  # Plain text/log files
        lines = content.split('\n')

        # Common log patterns
        patterns = {
            'timestamp': r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}',
            'level': r'(CRITICAL|ERROR|WARNING|WARN|INFO|DEBUG|FATAL|SEVERE)',
            'ip': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            'exception': r'Exception|Error|Traceback'
        }

        for line in lines:
            if line.strip():
                error_entry = {'raw': line}

                # Extract timestamp
                timestamp_match = re.search(patterns['timestamp'], line)
                if timestamp_match:
                    error_entry['timestamp'] = timestamp_match.group()

                # Extract log level
                level_match = re.search(patterns['level'], line, re.IGNORECASE)
                if level_match:
                    error_entry['level'] = level_match.group().upper()
                else:
                    # Try to infer from keywords
                    line_lower = line.lower()
                    if any(word in line_lower for word in ['critical', 'fatal', 'severe']):
                        error_entry['level'] = 'CRITICAL'
                    elif any(word in line_lower for word in ['error', 'exception', 'fail']):
                        error_entry['level'] = 'ERROR'
                    elif any(word in line_lower for word in ['warning', 'warn']):
                        error_entry['level'] = 'WARNING'
                    else:
                        error_entry['level'] = 'INFO'

                # Extract IP address
                ip_match = re.search(patterns['ip'], line)
                if ip_match:
                    error_entry['ip'] = ip_match.group()

                # Check for exception
                if re.search(patterns['exception'], line, re.IGNORECASE):
                    error_entry['has_exception'] = True

                # Extract message (simplified)
                error_entry['message'] = line.strip()

                errors.append(error_entry)

        return errors


def classify_severity(level):
    """Classify error severity"""
    level = str(level).upper()
    if level in ['CRITICAL', 'FATAL', 'SEVERE']:
        return 'Critical', '#DC2626'
    elif level in ['ERROR']:
        return 'Error', '#F59E0B'
    elif level in ['WARNING', 'WARN']:
        return 'Warning', '#FBBF24'
    else:
        return 'Info', '#3B82F6'


def render_statistics(errors_df):
    """Render error statistics"""
    st.subheader("📊 Error Statistics Overview")

    # Calculate statistics
    total_errors = len(errors_df)

    if 'level' in errors_df.columns:
        critical = len(errors_df[errors_df['level'].str.upper().isin(['CRITICAL', 'FATAL', 'SEVERE'])])
        errors = len(errors_df[errors_df['level'].str.upper() == 'ERROR'])
        warnings = len(errors_df[errors_df['level'].str.upper().isin(['WARNING', 'WARN'])])
    else:
        critical = errors = warnings = 0

    info = total_errors - critical - errors - warnings

    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #3B82F6;">
            <div class="stat-label">Total Logs</div>
            <div class="stat-number" style="color: #3B82F6;">{total_errors:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #DC2626;">
            <div class="stat-label">Critical</div>
            <div class="stat-number" style="color: #DC2626;">{critical:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #F59E0B;">
            <div class="stat-label">Errors</div>
            <div class="stat-number" style="color: #F59E0B;">{errors:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card" style="border-color: #FBBF24;">
            <div class="stat-label">Warnings</div>
            <div class="stat-number" style="color: #FBBF24;">{warnings:,}</div>
        </div>
        """, unsafe_allow_html=True)


def render_visualizations(errors_df):
    """Render error visualizations"""
    st.subheader("📈 Error Analysis Charts")

    if 'level' not in errors_df.columns:
        st.warning("No level information available for visualization")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Error distribution pie chart
        level_counts = errors_df['level'].value_counts()

        colors = []
        for level in level_counts.index:
            _, color = classify_severity(level)
            colors.append(color)

        fig_pie = go.Figure(data=[go.Pie(
            labels=level_counts.index,
            values=level_counts.values,
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent',
            textfont=dict(size=14, color='white')
        )])

        fig_pie.update_layout(
            title="Error Distribution by Severity",
            showlegend=True,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1E3A8A', size=12)
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart
        fig_bar = go.Figure(data=[go.Bar(
            x=level_counts.index,
            y=level_counts.values,
            marker=dict(color=colors),
            text=level_counts.values,
            textposition='auto',
        )])

        fig_bar.update_layout(
            title="Error Count by Level",
            xaxis_title="Log Level",
            yaxis_title="Count",
            showlegend=False,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1E3A8A', size=12)
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # Timeline chart if timestamps are available
    if 'timestamp' in errors_df.columns:
        try:
            errors_df['parsed_time'] = pd.to_datetime(errors_df['timestamp'], errors=True)

            if errors_df['parsed_time'].notna().any():
                st.subheader("⏱️ Error Timeline")

                timeline_df = errors_df.groupby([errors_df['parsed_time'].dt.date, 'level']).size().reset_index(name='count')
                timeline_df.columns = ['date', 'level', 'count']

                fig_timeline = px.line(
                    timeline_df,
                    x='date',
                    y='count',
                    color='level',
                    title='Errors Over Time',
                    markers=True
                )

                fig_timeline.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Number of Errors",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#1E3A8A', size=12)
                )

                st.plotly_chart(fig_timeline, use_container_width=True)
        except:
            pass


def render_error_details(errors_df, filters):
    """Render detailed error log entries"""
    st.subheader("🔍 Detailed Error Logs")

    # Apply filters
    filtered_df = errors_df.copy()

    if filters['level'] and 'level' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['level'].isin(filters['level'])]

    if filters['search'] and 'message' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['message'].str.contains(filters['search'], case=False, na=False)
        ]

    st.write(f"Showing {len(filtered_df)} of {len(errors_df)} log entries")

    # Pagination
    items_per_page = filters['items_per_page']
    total_pages = max(1, (len(filtered_df) - 1) // items_per_page + 1)

    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_df))

    page_df = filtered_df.iloc[start_idx:end_idx]

    # Display logs
    for idx, row in page_df.iterrows():
        level = row.get('level', 'INFO')
        severity, color = classify_severity(level)

        timestamp = row.get('timestamp', 'N/A')
        message = row.get('message', row.get('raw', 'No message'))

        # Truncate long messages
        if len(message) > 500 and not filters['show_full']:
            message = message[:500] + "..."

        with st.expander(f"**{level}** - {timestamp[:19] if len(timestamp) > 19 else timestamp}", expanded=False):
            st.markdown(f"""
            <div class="log-entry">
                <strong>Level:</strong> <span style="color: {color}; font-weight: 700;">{level}</span><br>
                <strong>Time:</strong> {timestamp}<br>
                <strong>Message:</strong><br>
                {message}
            </div>
            """, unsafe_allow_html=True)

            # Show raw entry if available
            if 'raw' in row and filters['show_full']:
                st.code(row['raw'], language="text")


# Main application
def main():
    # Header
    render_header(
        "🔍 Error Log Uploader & Analyzer",
        "Upload, analyze, and visualize application error logs",
        "🛠️"
    )

    # Sidebar - Upload and Settings
    with st.sidebar:
        st.header("⚙️ Configuration")

        # File upload
        st.subheader("📤 Upload Log File")
        uploaded_file = st.file_uploader(
            "Choose a log file",
            type=['log', 'txt', 'json', 'csv'],
            help="Upload error logs in LOG, TXT, JSON, or CSV format"
        )

        st.divider()

        # Sample data option
        if st.button("📋 Load Sample Data"):
            st.session_state['use_sample'] = True

        st.divider()

        # Filters
        st.subheader("🔧 Filters & Options")

        level_filter = st.multiselect(
            "Log Level",
            ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
            default=[]
        )

        search_filter = st.text_input("🔍 Search in messages", "")

        items_per_page = st.slider("Items per page", 10, 100, 25, 5)

        show_full = st.checkbox("Show full messages", False)

        st.divider()

        # Export options
        st.subheader("💾 Export Options")

        export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])

    # Main content
    errors_data = None

    # Handle sample data
    if st.session_state.get('use_sample', False):
        # Generate sample error data
        sample_errors = []
        base_time = datetime.now()

        for i in range(150):
            levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO']
            weights = [5, 20, 40, 35]
            level = pd.np.random.choice(levels, p=[w/100 for w in weights])

            timestamp = (base_time - timedelta(hours=i//10, minutes=i%60)).strftime("%Y-%m-%d %H:%M:%S")

            messages = {
                'CRITICAL': [
                    "Database connection pool exhausted",
                    "System memory critically low",
                    "Service unavailable - upstream timeout"
                ],
                'ERROR': [
                    "Failed to process transaction",
                    "API endpoint returned 500",
                    "File not found exception",
                    "Authentication failed"
                ],
                'WARNING': [
                    "Response time exceeding threshold",
                    "Deprecated API method called",
                    "Cache miss rate high"
                ],
                'INFO': [
                    "Request processed successfully",
                    "User logged in",
                    "Cache refreshed"
                ]
            }

            message = pd.np.random.choice(messages[level])

            sample_errors.append({
                'timestamp': timestamp,
                'level': level,
                'message': f"{message} [ID: {i+1000}]",
                'raw': f"{timestamp} [{level}] {message} [ID: {i+1000}]"
            })

        errors_data = sample_errors
        st.session_state['use_sample'] = False
        render_alert("Sample data loaded successfully!", "success")

    # Handle file upload
    elif uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            file_type = uploaded_file.name.split('.')[-1].lower()

            errors_data = parse_log_file(content, file_type)

            if errors_data:
                render_alert(f"Successfully loaded {len(errors_data)} log entries from {uploaded_file.name}", "success")
            else:
                render_alert("No valid log entries found", "warning")

        except Exception as e:
            render_alert(f"Error processing file: {str(e)}", "error")

    # Display analysis if data is available
    if errors_data:
        errors_df = pd.DataFrame(errors_data)

        # Store in session state
        st.session_state['errors_df'] = errors_df

        # Render sections
        st.divider()
        render_statistics(errors_df)

        st.divider()
        render_visualizations(errors_df)

        st.divider()
        filters = {
            'level': level_filter,
            'search': search_filter,
            'items_per_page': items_per_page,
            'show_full': show_full
        }
        render_error_details(errors_df, filters)

        # Export functionality
        st.divider()
        st.subheader("💾 Export Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            if export_format == "CSV":
                csv = errors_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"error_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col2:
            if export_format == "JSON":
                json_str = errors_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_str,
                    file_name=f"error_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col3:
            if export_format == "Excel":
                from io import BytesIO
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    errors_df.to_excel(writer, sheet_name='Error Logs', index=False)

                st.download_button(
                    label="⬇️ Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"error_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    else:
        # Welcome screen
        st.markdown("""
        ### Welcome to the Error Log Analyzer! 👋

        This dashboard helps you:
        - 📤 **Upload** error logs in various formats (LOG, TXT, JSON, CSV)
        - 📊 **Analyze** error patterns and statistics
        - 🔍 **Search** and filter through log entries
        - 📈 **Visualize** error trends over time
        - 💾 **Export** analyzed data for further processing

        **Get started:**
        1. Upload a log file using the sidebar
        2. Or click "Load Sample Data" to try out the features

        ---
        """)

        # Feature highlights
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            #### 🎯 Smart Parsing
            Automatically detects and parses common log formats including:
            - Timestamps
            - Log levels (CRITICAL, ERROR, WARNING, INFO)
            - Error messages
            - Stack traces
            """)

        with col2:
            st.markdown("""
            #### 📊 Rich Analytics
            Get instant insights:
            - Error distribution charts
            - Severity classification
            - Timeline analysis
            - Statistical summaries
            """)

        with col3:
            st.markdown("""
            #### 🔧 Powerful Tools
            Advanced features:
            - Multi-level filtering
            - Full-text search
            - Pagination support
            - Multiple export formats
            """)


if __name__ == "__main__":
    main()
