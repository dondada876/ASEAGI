#!/usr/bin/env python3
"""
Supabase File Cross-Reference Dashboard
Real-time file search, analysis, and cross-referencing with Supabase backend
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter
import sys

# Add API-Integration to path
sys.path.insert(0, str(Path.home() / "Downloads" / "Resources" / "CH16_Technology" / "API-Integration"))

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Supabase library not installed. Run: pip3 install supabase")
    st.stop()

st.set_page_config(
    page_title="Supabase File Cross-Reference Dashboard",
    page_icon="🔍",
    layout="wide"
)

# ===== SUPABASE CONNECTION =====

@st.cache_resource
def init_supabase():
    """Initialize Supabase client with credentials"""
    # Try Streamlit secrets first, then environment variables
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
        key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

    if not url or not key:
        return None, "Missing SUPABASE_URL or SUPABASE_KEY in secrets.toml or environment variables"

    try:
        client = create_client(url, key)
        # Test connection
        client.table('file_metadata').select('file_id', count='exact').limit(1).execute()
        return client, None
    except Exception as e:
        return None, str(e)

# ===== DATA QUERIES =====

@st.cache_data(ttl=60)
def get_statistics(_client):
    """Get file system statistics from Supabase"""
    try:
        # Total files
        total_response = _client.table('file_metadata').select('file_id', count='exact').execute()
        total = total_response.count if hasattr(total_response, 'count') else len(total_response.data)

        # By PARA
        para_stats = {}
        for para in ['Projects', 'Areas', 'Resources', 'Archive']:
            response = _client.table('file_metadata').select('file_id', count='exact').eq('para_category', para).execute()
            count = response.count if hasattr(response, 'count') else len(response.data)
            para_stats[para] = count

        # By department
        dept_response = _client.table('file_metadata').select('dept_code, dept_name').execute()
        dept_counter = Counter()
        for file in dept_response.data:
            dept = file.get('dept_code', 'Unknown')
            dept_name = file.get('dept_name', '')
            dept_counter[f"{dept} - {dept_name}"] += 1

        # Naming compliance
        compliant_response = _client.table('file_metadata').select('file_id', count='exact').eq('naming_compliant', True).execute()
        compliant = compliant_response.count if hasattr(compliant_response, 'count') else len(compliant_response.data)

        # File types
        type_response = _client.table('file_metadata').select('file_type_category').execute()
        type_counter = Counter()
        for file in type_response.data:
            ftype = file.get('file_type_category', 'Unknown')
            type_counter[ftype] += 1

        # Total size
        size_response = _client.table('file_metadata').select('size_mb').execute()
        total_size_mb = sum(f.get('size_mb', 0) for f in size_response.data if f.get('size_mb'))

        return {
            'total_files': total,
            'para_distribution': para_stats,
            'dept_distribution': dept_counter.most_common(20),
            'file_type_distribution': type_counter.most_common(10),
            'naming_compliant': compliant,
            'compliance_rate': (compliant/total*100) if total > 0 else 0,
            'total_size_mb': total_size_mb,
            'total_size_gb': total_size_mb / 1024
        }
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return None

@st.cache_data(ttl=30)
def search_files(_client, search_term, limit=50):
    """Search files by text"""
    try:
        response = _client.table('file_metadata')\
            .select('file_id, filename, dept_code, dept_name, para_category, company, size_mb, modified_date, file_path')\
            .ilike('search_text', f'%{search_term.lower()}%')\
            .order('modified_date', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

@st.cache_data(ttl=30)
def get_files_by_department(_client, dept_code, limit=100):
    """Get files for specific department"""
    try:
        response = _client.table('file_metadata')\
            .select('file_id, filename, para_category, size_mb, modified_date, naming_compliant, file_path')\
            .eq('dept_code', dept_code)\
            .order('modified_date', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Department query error: {e}")
        return []

@st.cache_data(ttl=30)
def get_files_by_para(_client, para_category, limit=100):
    """Get files in PARA category"""
    try:
        response = _client.table('file_metadata')\
            .select('file_id, filename, dept_code, dept_name, size_mb, modified_date, file_type_category, file_path')\
            .eq('para_category', para_category)\
            .order('modified_date', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"PARA query error: {e}")
        return []

@st.cache_data(ttl=60)
def get_duplicates(_client):
    """Find duplicate files"""
    try:
        response = _client.table('file_metadata')\
            .select('content_hash, filename, file_path, size_mb, file_id')\
            .execute()

        # Group by hash
        hash_map = {}
        for file in response.data:
            if file['content_hash']:
                h = file['content_hash']
                if h not in hash_map:
                    hash_map[h] = []
                hash_map[h].append(file)

        # Return only duplicates
        duplicates = []
        for h, files in hash_map.items():
            if len(files) > 1:
                duplicates.append({
                    'hash': h,
                    'count': len(files),
                    'total_size_mb': sum(f.get('size_mb', 0) for f in files),
                    'files': files
                })

        return sorted(duplicates, key=lambda x: x['total_size_mb'], reverse=True)
    except Exception as e:
        st.error(f"Duplicate query error: {e}")
        return []

@st.cache_data(ttl=30)
def get_file_by_id(_client, file_id):
    """Get complete file metadata by UUID"""
    try:
        response = _client.table('file_metadata')\
            .select('*')\
            .eq('file_id', file_id)\
            .execute()

        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"File lookup error: {e}")
        return None

@st.cache_data(ttl=30)
def get_recent_files(_client, days=7, limit=50):
    """Get recently modified files"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        response = _client.table('file_metadata')\
            .select('file_id, filename, dept_code, para_category, size_mb, modified_date, file_path')\
            .gte('modified_date', cutoff.isoformat())\
            .order('modified_date', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Recent files error: {e}")
        return []

# ===== MAIN APP =====

def main():
    # Header
    st.title("🔍 Supabase File Cross-Reference Dashboard")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize Supabase
    client, error = init_supabase()

    if error:
        st.error(f"❌ **Supabase Connection Failed**")
        st.code(error)
        st.info("💡 **Fix:** Run `source ~/.supabase_file_system` to load credentials")
        st.stop()

    st.success("✅ Connected to Supabase")
    st.markdown("---")

    # ===== SIDEBAR: FILTERS & SEARCH =====
    st.sidebar.header("🔎 Search & Filter")

    search_mode = st.sidebar.radio(
        "Search Mode",
        ["Quick Stats", "Text Search", "UUID Lookup", "Department", "PARA Category", "Recent Files", "Duplicates"],
        help="Choose how to find files"
    )

    # ===== MAIN CONTENT BASED ON SEARCH MODE =====

    if search_mode == "Quick Stats":
        st.header("📊 System Overview")

        stats = get_statistics(client)

        if stats:
            # Top metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Files", f"{stats['total_files']:,}")

            with col2:
                st.metric("Total Size", f"{stats['total_size_gb']:.1f} GB")

            with col3:
                st.metric("Naming Compliance", f"{stats['compliance_rate']:.1f}%")

            with col4:
                non_compliant = stats['total_files'] - stats['naming_compliant']
                st.metric("Need Renaming", f"{non_compliant:,}")

            st.markdown("---")

            # PARA Distribution
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📁 PARA Distribution")
                para_data = []
                for para in ['Projects', 'Areas', 'Resources', 'Archive']:
                    count = stats['para_distribution'].get(para, 0)
                    pct = (count / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
                    icon = {'Projects': '🎯', 'Areas': '📋', 'Resources': '📚', 'Archive': '🗄️'}[para]
                    para_data.append({
                        'Category': f"{icon} {para}",
                        'Files': count,
                        'Percentage': f"{pct:.1f}%"
                    })
                st.dataframe(pd.DataFrame(para_data), use_container_width=True, hide_index=True)

            with col2:
                st.subheader("🏢 Top Departments")
                dept_data = []
                for dept, count in stats['dept_distribution'][:10]:
                    pct = (count / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
                    dept_data.append({
                        'Department': dept,
                        'Files': count,
                        'Percentage': f"{pct:.1f}%"
                    })
                st.dataframe(pd.DataFrame(dept_data), use_container_width=True, hide_index=True)

            st.markdown("---")

            # File Types
            st.subheader("📄 File Type Distribution")
            type_data = []
            for ftype, count in stats['file_type_distribution']:
                pct = (count / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
                type_data.append({
                    'Type': ftype,
                    'Files': count,
                    'Percentage': f"{pct:.1f}%"
                })
            st.dataframe(pd.DataFrame(type_data), use_container_width=True, hide_index=True)

    elif search_mode == "Text Search":
        st.header("🔎 Full-Text Search")

        search_term = st.text_input("Search for files", placeholder="e.g., custody, police report, contract")
        search_limit = st.slider("Max results", 10, 200, 50)

        if search_term:
            with st.spinner(f"Searching for '{search_term}'..."):
                results = search_files(client, search_term, limit=search_limit)

            if results:
                st.success(f"Found {len(results)} files matching '{search_term}'")

                # Display results
                for i, file in enumerate(results, 1):
                    with st.expander(f"{i}. {file['filename']} ({file['size_mb']:.2f} MB)"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**UUID:** `{file['file_id']}`")
                            st.write(f"**Department:** {file['dept_code']} - {file.get('dept_name', 'N/A')}")
                            st.write(f"**PARA:** {file['para_category']}")
                            st.write(f"**Company:** {file.get('company', 'N/A')}")

                        with col2:
                            st.write(f"**Modified:** {file['modified_date']}")
                            st.write(f"**Size:** {file['size_mb']:.2f} MB")
                            st.write(f"**Path:** `{file['file_path']}`")

                # Export option
                if st.button("📥 Export Results to CSV"):
                    df = pd.DataFrame(results)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"search_results_{search_term}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning(f"No files found matching '{search_term}'")

    elif search_mode == "UUID Lookup":
        st.header("🔑 File Lookup by UUID")

        file_id = st.text_input("Enter File UUID", placeholder="e.g., 12345678-1234-1234-1234-123456789abc")

        if file_id:
            with st.spinner("Looking up file..."):
                file_data = get_file_by_id(client, file_id)

            if file_data:
                st.success("✅ File Found")

                # Display full details
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📋 File Information")
                    st.write(f"**Filename:** {file_data['filename']}")
                    st.write(f"**Path:** `{file_data['file_path']}`")
                    st.write(f"**Absolute Path:** `{file_data.get('absolute_path', 'N/A')}`")
                    st.write(f"**Parent Folder:** {file_data.get('parent_folder', 'N/A')}")

                    st.subheader("🏷️ Classification")
                    st.write(f"**Department:** {file_data['dept_code']} - {file_data.get('dept_name', 'N/A')}")
                    st.write(f"**PARA:** {file_data['para_category']}")
                    st.write(f"**Company:** {file_data.get('company', 'N/A')}")
                    st.write(f"**File Type:** {file_data.get('file_type_category', 'N/A')}")

                with col2:
                    st.subheader("📊 Properties")
                    st.write(f"**Size:** {file_data.get('size_mb', 0):.2f} MB")
                    st.write(f"**Extension:** {file_data.get('extension', 'N/A')}")
                    st.write(f"**Created:** {file_data.get('created_at', 'N/A')}")
                    st.write(f"**Modified:** {file_data.get('modified_date', 'N/A')}")
                    st.write(f"**Indexed:** {file_data.get('indexed_at', 'N/A')}")

                    st.subheader("✅ Compliance")
                    compliant = file_data.get('naming_compliant', False)
                    st.write(f"**Naming:** {'✅ Compliant' if compliant else '❌ Non-compliant'}")
                    if file_data.get('date'):
                        st.write(f"**Date:** {file_data['date']}")
                    if file_data.get('description'):
                        st.write(f"**Description:** {file_data['description']}")

                st.subheader("🔐 Identifiers")
                st.code(f"File ID: {file_data['file_id']}")
                st.code(f"Content Hash: {file_data.get('content_hash', 'N/A')}")
            else:
                st.error(f"❌ No file found with UUID: {file_id}")

    elif search_mode == "Department":
        st.header("🏢 Files by Department")

        # Get all departments
        stats = get_statistics(client)
        dept_list = [dept.split(' - ')[0] for dept, _ in stats['dept_distribution']]

        dept_code = st.selectbox("Select Department", dept_list)
        dept_limit = st.slider("Max results", 10, 200, 100)

        if dept_code:
            with st.spinner(f"Loading {dept_code} files..."):
                results = get_files_by_department(client, dept_code, limit=dept_limit)

            if results:
                st.success(f"Found {len(results)} files in {dept_code}")

                # Summary metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    total_size = sum(f.get('size_mb', 0) for f in results)
                    st.metric("Total Size", f"{total_size:.1f} MB")

                with col2:
                    compliant = sum(1 for f in results if f.get('naming_compliant'))
                    compliance_pct = (compliant / len(results) * 100) if results else 0
                    st.metric("Naming Compliance", f"{compliance_pct:.1f}%")

                with col3:
                    para_counter = Counter(f['para_category'] for f in results if f.get('para_category'))
                    most_common_para = para_counter.most_common(1)[0][0] if para_counter else 'N/A'
                    st.metric("Most Common PARA", most_common_para)

                st.markdown("---")

                # Display results table
                df_data = []
                for f in results:
                    df_data.append({
                        'Filename': f['filename'],
                        'UUID': f['file_id'][:13] + '...',
                        'PARA': f.get('para_category', 'N/A'),
                        'Size (MB)': f'{f.get("size_mb", 0):.2f}',
                        'Modified': f.get('modified_date', 'N/A')[:10],
                        'Compliant': '✅' if f.get('naming_compliant') else '❌'
                    })

                st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

                # Export option
                if st.button("📥 Export to CSV"):
                    df = pd.DataFrame(results)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"dept_{dept_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning(f"No files found in {dept_code}")

    elif search_mode == "PARA Category":
        st.header("📁 Files by PARA Category")

        para_category = st.selectbox("Select PARA Category", ['Projects', 'Areas', 'Resources', 'Archive'])
        para_limit = st.slider("Max results", 10, 200, 100)

        with st.spinner(f"Loading {para_category} files..."):
            results = get_files_by_para(client, para_category, limit=para_limit)

        if results:
            st.success(f"Found {len(results)} files in {para_category}")

            # Summary metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                total_size = sum(f.get('size_mb', 0) for f in results)
                st.metric("Total Size", f"{total_size:.1f} MB")

            with col2:
                dept_counter = Counter(f.get('dept_code') for f in results if f.get('dept_code'))
                unique_depts = len(dept_counter)
                st.metric("Unique Departments", unique_depts)

            with col3:
                type_counter = Counter(f.get('file_type_category') for f in results if f.get('file_type_category'))
                most_common_type = type_counter.most_common(1)[0][0] if type_counter else 'N/A'
                st.metric("Most Common Type", most_common_type)

            st.markdown("---")

            # Display results table
            df_data = []
            for f in results:
                df_data.append({
                    'Filename': f['filename'],
                    'UUID': f['file_id'][:13] + '...',
                    'Department': f.get('dept_code', 'N/A'),
                    'Type': f.get('file_type_category', 'N/A'),
                    'Size (MB)': f'{f.get("size_mb", 0):.2f}',
                    'Modified': f.get('modified_date', 'N/A')[:10]
                })

            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

            # Export option
            if st.button("📥 Export to CSV"):
                df = pd.DataFrame(results)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"para_{para_category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning(f"No files found in {para_category}")

    elif search_mode == "Recent Files":
        st.header("🕒 Recently Modified Files")

        days = st.slider("Days to look back", 1, 90, 7)
        recent_limit = st.slider("Max results", 10, 200, 50)

        with st.spinner(f"Loading files from last {days} days..."):
            results = get_recent_files(client, days=days, limit=recent_limit)

        if results:
            st.success(f"Found {len(results)} files modified in last {days} days")

            # Display results
            df_data = []
            for f in results:
                df_data.append({
                    'Filename': f['filename'],
                    'UUID': f['file_id'][:13] + '...',
                    'Department': f.get('dept_code', 'N/A'),
                    'PARA': f.get('para_category', 'N/A'),
                    'Size (MB)': f'{f.get("size_mb", 0):.2f}',
                    'Modified': f.get('modified_date', 'N/A')
                })

            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
        else:
            st.warning(f"No files modified in last {days} days")

    elif search_mode == "Duplicates":
        st.header("🔄 Duplicate Files")

        with st.spinner("Finding duplicates..."):
            duplicates = get_duplicates(client)

        if duplicates:
            st.warning(f"⚠️ Found {len(duplicates)} duplicate groups")

            # Calculate total wasted space
            total_wasted_mb = sum(dup['total_size_mb'] - (dup['total_size_mb'] / dup['count']) for dup in duplicates)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Duplicate Groups", len(duplicates))

            with col2:
                total_dup_files = sum(dup['count'] for dup in duplicates)
                st.metric("Total Duplicate Files", total_dup_files)

            with col3:
                st.metric("Wasted Space", f"{total_wasted_mb:.1f} MB")

            st.markdown("---")

            # Display each duplicate group
            for i, dup in enumerate(duplicates, 1):
                with st.expander(f"Group {i}: {dup['count']} copies ({dup['total_size_mb']:.2f} MB total)"):
                    st.write(f"**Content Hash:** `{dup['hash'][:16]}...`")
                    st.write(f"**Can save:** {dup['total_size_mb'] - (dup['total_size_mb'] / dup['count']):.2f} MB by keeping 1 copy")

                    st.write("**Files:**")
                    for file in dup['files']:
                        st.write(f"- `{file['filename']}` ({file['size_mb']:.2f} MB)")
                        st.write(f"  UUID: `{file['file_id']}`")
                        st.write(f"  Path: `{file['file_path']}`")
                        st.write("")
        else:
            st.success("✅ No duplicate files found!")

    # Footer
    st.markdown("---")
    st.caption(f"🔗 Connected to: {os.environ.get('SUPABASE_URL', 'N/A')[:30]}... • Dashboard refresh: Use browser refresh or change filters")

if __name__ == "__main__":
    main()
