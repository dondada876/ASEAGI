#!/usr/bin/env python3
"""
Simple Document Upload Portal
Dedicated web interface for uploading legal documents
Clean, minimal interface optimized for Surface Pro
"""

import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import hashlib

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Document Upload Portal",
    page_icon="📁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Storage setup
UPLOAD_DIR = Path("/home/user/ASEAGI/uploads/web_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        font-size: 18px;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .upload-box {
        border: 3px dashed #4CAF50;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        background-color: #f0f8f0;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📁 Document Upload Portal")
st.markdown("---")

# Upload section
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
st.subheader("📤 Upload Your Documents")
st.write("Supported: PDF, JPG, PNG, TXT, DOCX")
st.markdown('</div>', unsafe_allow_html=True)

# File uploader - MAIN UPLOAD WIDGET
uploaded_files = st.file_uploader(
    "Choose files to upload",
    type=['pdf', 'jpg', 'jpeg', 'png', 'txt', 'docx', 'doc', 'rtf'],
    accept_multiple_files=True,
    help="Click to browse or drag and drop files here"
)

st.markdown("---")

# Process uploads
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")

    if st.button("🚀 UPLOAD NOW", type="primary"):
        st.markdown("### 📊 Upload Progress")

        progress_bar = st.progress(0)
        status_text = st.empty()

        success_count = 0

        for idx, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (idx + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {idx+1}/{len(uploaded_files)}: {uploaded_file.name}")

            try:
                # Save file
                file_path = UPLOAD_DIR / uploaded_file.name
                file_bytes = uploaded_file.getvalue()

                # Write to disk
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)

                # Calculate hash for tracking
                file_hash = hashlib.md5(file_bytes).hexdigest()

                # Show success
                st.success(f"✅ **{uploaded_file.name}**")
                st.write(f"   - Size: {len(file_bytes)/1024:.1f} KB")
                st.write(f"   - Saved to: {file_path}")
                st.write(f"   - Hash: {file_hash[:16]}...")

                success_count += 1

            except Exception as e:
                st.error(f"❌ **{uploaded_file.name}**: {str(e)}")

        # Final summary
        status_text.text("✅ Upload Complete!")
        st.markdown("---")
        st.success(f"### 🎉 Successfully uploaded {success_count}/{len(uploaded_files)} files!")

        if success_count > 0:
            st.info(f"📁 Files saved to: {UPLOAD_DIR}")
            st.balloons()

else:
    st.info("👆 Click above to select files for upload")

# Footer
st.markdown("---")

# Show recent uploads
st.subheader("📋 Recent Uploads")

if UPLOAD_DIR.exists():
    files = sorted(UPLOAD_DIR.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]

    if files:
        for file in files:
            stat = file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            size_kb = stat.st_size / 1024

            col1, col2, col3 = st.columns([3, 1, 2])
            col1.write(f"📄 {file.name}")
            col2.write(f"{size_kb:.1f} KB")
            col3.write(f"{mod_time}")
    else:
        st.write("No uploads yet")
else:
    st.write("Upload directory not found")

st.markdown("---")
st.caption(f"Document Upload Portal v1.0 | Storage: {UPLOAD_DIR}")
