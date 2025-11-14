#!/usr/bin/env python3
"""
Simple test dashboard to verify file upload works
"""

import streamlit as st

st.title("🧪 File Upload Test")

st.write("If you can see an upload button below, Streamlit file uploads are working.")

uploaded_file = st.file_uploader("Choose a file", type=['jpg', 'png', 'pdf', 'txt'])

if uploaded_file is not None:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.write(f"Size: {len(uploaded_file.getvalue())} bytes")
else:
    st.info("No file uploaded yet")

st.write("---")
st.write("**Test Info:**")
st.write(f"- Streamlit version: {st.__version__}")
st.write(f"- Python version: 3.x")
