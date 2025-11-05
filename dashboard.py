import streamlit as st
import re
import os
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="File Organization Dashboard", layout="wide", page_icon="📊")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-card {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 File Organization Dashboard")
st.markdown("### Analysis of Department Organizer Processing")

# Read log file
log_file = "department_organizer.log"
changes_file = "dept_changes_20251104_000836.txt"

@st.cache_data
def parse_log_file(filename):
    """Parse the log file and extract key information"""
    stats = {
        'total_files': 0,
        'skipped_files': 0,
        'processed_files': 0,
        'warnings': [],
        'departments': defaultdict(int),
        'files_by_status': {'successful': 0, 'failed': 0, 'review': 0},
        'confidence_scores': [],
        'file_types': defaultdict(int),
        'files_details': []
    }

    if not os.path.exists(filename):
        return stats

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

        # Extract summary statistics
        total_match = re.search(r'Processed: (\d+) files', content)
        skipped_match = re.search(r'Skipped: (\d+) files', content)

        if total_match:
            stats['total_files'] = int(total_match.group(1))
            stats['processed_files'] = int(total_match.group(1))
        if skipped_match:
            stats['skipped_files'] = int(skipped_match.group(1))

        # Extract department distribution
        dept_pattern = r'CH\d+\.\d+: (\d+) file\(s\)'
        for match in re.finditer(dept_pattern, content):
            dept_name = match.group(0).split(':')[0].strip()
            count = int(match.group(1))
            stats['departments'][dept_name] = count

        # Extract warnings
        warning_pattern = r'WARNING - (.*?)$'
        stats['warnings'] = re.findall(warning_pattern, content, re.MULTILINE)

    return stats

@st.cache_data
def parse_changes_file(filename):
    """Parse the changes file for detailed file information"""
    files_data = []

    if not os.path.exists(filename):
        return files_data

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_file = {}
    for line in lines:
        line = line.strip()

        if line.startswith('Original:'):
            if current_file:
                files_data.append(current_file)
            current_file = {'original': line.replace('Original:', '').strip()}
        elif line.startswith('New:'):
            current_file['new'] = line.replace('New:', '').strip()
        elif line.startswith('Department:'):
            current_file['department'] = line.replace('Department:', '').strip()
        elif line.startswith('Confidence:'):
            conf_str = line.replace('Confidence:', '').strip()
            try:
                current_file['confidence'] = float(conf_str)
            except:
                current_file['confidence'] = 0.0

    if current_file:
        files_data.append(current_file)

    return files_data

# Load data
log_stats = parse_log_file(log_file)
files_data = parse_changes_file(changes_file)

# Calculate additional statistics
successful_files = [f for f in files_data if f.get('department', '') != 'Review' and f.get('confidence', 0) > 0]
failed_files = [f for f in files_data if f.get('department', '') == 'Review' or f.get('confidence', 0) == 0]
confidence_scores = [f.get('confidence', 0) for f in files_data if f.get('confidence', 0) > 0]

# Extract file types
file_types = defaultdict(int)
for f in files_data:
    original = f.get('original', '')
    ext = os.path.splitext(original)[1].lower()
    if ext:
        file_types[ext] = file_types.get(ext, 0) + 1

# Department distribution
dept_dist = defaultdict(int)
for f in files_data:
    dept = f.get('department', 'Unknown')
    dept_dist[dept] = dept_dist.get(dept, 0) + 1

# Overview Metrics
st.markdown("## 📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📁 Total Files",
        value=len(files_data),
        delta=None
    )

with col2:
    success_rate = (len(successful_files) / len(files_data) * 100) if files_data else 0
    st.metric(
        label="✅ Successfully Categorized",
        value=len(successful_files),
        delta=f"{success_rate:.1f}%"
    )

with col3:
    st.metric(
        label="⚠️ Needs Review",
        value=len(failed_files),
        delta=f"{len(failed_files)/len(files_data)*100:.1f}%" if files_data else "0%",
        delta_color="inverse"
    )

with col4:
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    st.metric(
        label="📊 Avg Confidence",
        value=f"{avg_confidence:.1f}",
        delta=None
    )

st.divider()

# Charts Section
st.markdown("## 📊 Visualizations")

col1, col2 = st.columns(2)

with col1:
    # Success vs Failed pie chart
    fig_status = go.Figure(data=[go.Pie(
        labels=['Successfully Categorized', 'Needs Review'],
        values=[len(successful_files), len(failed_files)],
        hole=0.4,
        marker_colors=['#28a745', '#dc3545']
    )])
    fig_status.update_layout(
        title="Processing Status",
        height=400
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    # Department distribution
    dept_names = list(dept_dist.keys())
    dept_counts = list(dept_dist.values())

    fig_dept = go.Figure(data=[go.Bar(
        x=dept_names,
        y=dept_counts,
        marker_color='#007bff',
        text=dept_counts,
        textposition='auto',
    )])
    fig_dept.update_layout(
        title="Files by Department",
        xaxis_title="Department",
        yaxis_title="Number of Files",
        height=400
    )
    st.plotly_chart(fig_dept, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # File types distribution
    if file_types:
        fig_types = go.Figure(data=[go.Pie(
            labels=list(file_types.keys()),
            values=list(file_types.values()),
            hole=0.3
        )])
        fig_types.update_layout(
            title="File Types Distribution",
            height=400
        )
        st.plotly_chart(fig_types, use_container_width=True)

with col4:
    # Confidence score distribution
    if confidence_scores:
        fig_conf = go.Figure(data=[go.Histogram(
            x=confidence_scores,
            nbinsx=20,
            marker_color='#17a2b8'
        )])
        fig_conf.update_layout(
            title="Confidence Score Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig_conf, use_container_width=True)

st.divider()

# Warnings Section
if log_stats['warnings']:
    st.markdown("## ⚠️ Processing Warnings")
    warning_counts = defaultdict(int)
    for warning in log_stats['warnings']:
        warning_counts[warning] = warning_counts.get(warning, 0) + 1

    for warning, count in warning_counts.items():
        st.warning(f"**{warning}** (occurred {count} time{'s' if count > 1 else ''})")

st.divider()

# Detailed File List
st.markdown("## 📋 Detailed File Analysis")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    filter_status = st.selectbox(
        "Filter by Status",
        ["All", "Successfully Categorized", "Needs Review"]
    )

with col2:
    departments = ["All"] + sorted(list(dept_dist.keys()))
    filter_dept = st.selectbox("Filter by Department", departments)

with col3:
    min_confidence = st.slider("Minimum Confidence", 0.0, 1000.0, 0.0, 1.0)

# Apply filters
filtered_files = files_data.copy()

if filter_status == "Successfully Categorized":
    filtered_files = [f for f in filtered_files if f.get('department', '') != 'Review' and f.get('confidence', 0) > 0]
elif filter_status == "Needs Review":
    filtered_files = [f for f in filtered_files if f.get('department', '') == 'Review' or f.get('confidence', 0) == 0]

if filter_dept != "All":
    filtered_files = [f for f in filtered_files if f.get('department', '') == filter_dept]

filtered_files = [f for f in filtered_files if f.get('confidence', 0) >= min_confidence]

st.info(f"Showing {len(filtered_files)} of {len(files_data)} files")

# Display files in a table
if filtered_files:
    for idx, file_info in enumerate(filtered_files, 1):
        original = file_info.get('original', 'N/A')
        new_path = file_info.get('new', 'N/A')
        dept = file_info.get('department', 'N/A')
        confidence = file_info.get('confidence', 0)

        # Determine card style
        if dept == 'Review' or confidence == 0:
            card_class = "danger-card"
            status_icon = "❌"
        elif confidence > 50:
            card_class = "success-card"
            status_icon = "✅"
        else:
            card_class = "warning-card"
            status_icon = "⚠️"

        with st.expander(f"{status_icon} File {idx}: {os.path.basename(original)}"):
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Original Path:**")
                st.code(original, language="")

            with col2:
                st.markdown("**New Path:**")
                st.code(new_path, language="")

            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"**Department:** `{dept}`")
            with col4:
                st.markdown(f"**Confidence Score:** `{confidence:.2f}`")
else:
    st.info("No files match the current filters")

# Export functionality
st.divider()
st.markdown("## 📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Export Successful Files CSV"):
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Original', 'New Path', 'Department', 'Confidence'])

        for f in successful_files:
            writer.writerow([
                f.get('original', ''),
                f.get('new', ''),
                f.get('department', ''),
                f.get('confidence', 0)
            ])

        st.download_button(
            label="⬇️ Download CSV",
            data=output.getvalue(),
            file_name="successful_files.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📄 Export Failed Files CSV"):
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Original', 'New Path', 'Department', 'Confidence'])

        for f in failed_files:
            writer.writerow([
                f.get('original', ''),
                f.get('new', ''),
                f.get('department', ''),
                f.get('confidence', 0)
            ])

        st.download_button(
            label="⬇️ Download CSV",
            data=output.getvalue(),
            file_name="failed_files.csv",
            mime="text/csv"
        )

# Footer
st.divider()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"Dashboard generated on {timestamp} | Data from: {log_file} & {changes_file}")
