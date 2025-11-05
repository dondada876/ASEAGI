#!/usr/bin/env python3
"""
Comprehensive CEO Dashboard - Complete File Organization System Overview
Combines inventory, classification, PARA structure, and cost analysis
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter
import pandas as pd

st.set_page_config(
    page_title="CEO File Organization Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_inventory():
    """Load file inventory data"""
    inventory_path = Path.home() / "Downloads" / "file_inventory.json"
    if not inventory_path.exists():
        return None
    with open(inventory_path, 'r') as f:
        return json.load(f)

@st.cache_data
def load_classification_results():
    """Load hybrid classification results"""
    downloads = Path.home() / "Downloads"
    results_files = sorted(downloads.glob("hybrid_results_*.json"))
    if not results_files:
        return None
    with open(results_files[-1], 'r') as f:
        return json.load(f)

@st.cache_data
def scan_para_structure():
    """Scan actual PARA folder structure"""
    downloads = Path.home() / "Downloads"
    para_folders = ['Projects', 'Areas', 'Resources', 'Archive']

    structure = {}
    for para in para_folders:
        para_path = downloads / para
        if not para_path.exists():
            continue

        # Find department folders
        dept_folders = sorted(para_path.glob("CH*_*"))
        structure[para] = {}

        for dept_folder in dept_folders:
            # Count files
            file_count = len([f for f in dept_folder.rglob("*") if f.is_file()])
            structure[para][dept_folder.name] = file_count

    return structure

def main():
    # Header
    st.title("📊 CEO File Organization Dashboard")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # Load data
    inventory = load_inventory()
    classification = load_classification_results()
    para_structure = scan_para_structure()

    # === TOP-LEVEL METRICS ===
    st.header("🎯 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    if inventory:
        stats = inventory.get('statistics', {})

        with col1:
            st.metric(
                "Total Files",
                f"{stats.get('total_files', 0):,}",
                help="All files in system"
            )

        with col2:
            size_gb = stats.get('total_size_mb', 0) / 1024
            st.metric(
                "Total Size",
                f"{size_gb:.1f} GB",
                help="Total storage used"
            )

        with col3:
            compliance = stats.get('naming_compliant', 0)
            total = stats.get('total_files', 1)
            compliance_pct = (compliance / total * 100) if total > 0 else 0
            st.metric(
                "Naming Compliance",
                f"{compliance_pct:.1f}%",
                help="Files following YYYY-MM-DD-CH##.# format"
            )

        with col4:
            dupes = stats.get('duplicate_groups', 0)
            st.metric(
                "Duplicate Groups",
                dupes,
                help="Sets of duplicate files"
            )

    st.markdown("---")

    # === PARA STRUCTURE ===
    st.header("📁 PARA Organization Structure")

    if para_structure:
        # Calculate totals
        para_totals = {}
        all_depts = {}

        for para, depts in para_structure.items():
            para_totals[para] = sum(depts.values())
            for dept, count in depts.items():
                if dept not in all_depts:
                    all_depts[dept] = 0
                all_depts[dept] += count

        # PARA category breakdown
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Category Distribution")
            for para in ['Projects', 'Areas', 'Resources', 'Archive']:
                count = para_totals.get(para, 0)
                if count > 0:
                    icon = {
                        'Projects': '🎯',
                        'Areas': '📋',
                        'Resources': '📚',
                        'Archive': '🗄️'
                    }[para]
                    st.metric(f"{icon} {para}", f"{count} files")

        with col2:
            st.subheader("Department Breakdown")

            # Sort departments by file count
            sorted_depts = sorted(all_depts.items(), key=lambda x: -x[1])

            if sorted_depts:
                df_data = []
                for dept, count in sorted_depts[:15]:  # Top 15
                    # Extract CH code and name
                    parts = dept.split('_', 1)
                    ch_code = parts[0] if len(parts) > 0 else dept
                    dept_name = parts[1] if len(parts) > 1 else ""

                    # Find which PARA categories this dept is in
                    para_list = []
                    for para, depts_dict in para_structure.items():
                        if dept in depts_dict and depts_dict[dept] > 0:
                            para_list.append(f"{para[0]}")  # Just first letter

                    df_data.append({
                        'Department': ch_code,
                        'Name': dept_name,
                        'Files': count,
                        'PARA': ','.join(para_list)
                    })

                df = pd.DataFrame(df_data)
                st.dataframe(df, width='stretch', hide_index=True)

    st.markdown("---")

    # === CLASSIFICATION RESULTS ===
    if classification:
        st.header("🤖 Hybrid Classification Performance")

        stats = classification.get('statistics', {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            processed = stats.get('total_files', 0)
            st.metric("Files Classified", f"{processed:,}")

        with col2:
            tier1 = stats.get('tier1_success', 0)
            tier1_pct = (tier1 / processed * 100) if processed > 0 else 0
            st.metric(
                "FREE Processing",
                f"{tier1_pct:.1f}%",
                delta=f"{tier1} files",
                help="Classified via keyword matching (no cost)"
            )

        with col3:
            tier2 = stats.get('tier2_needed', 0)
            tier2_pct = (tier2 / processed * 100) if processed > 0 else 0
            st.metric(
                "API Processing",
                f"{tier2_pct:.1f}%",
                delta=f"{tier2} files",
                help="Classified via Claude API"
            )

        with col4:
            cost = stats.get('api_cost_estimate', 0)
            st.metric(
                "Total Cost",
                f"${cost:.2f}",
                help="Claude API cost"
            )

        # Classification details
        st.subheader("Classification Quality")

        results = classification.get('results', [])

        # Calculate confidence distribution
        confidences = [r.get('confidence', 0) for r in results if r.get('tier') not in ['error', 'failed']]

        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            high_conf = len([c for c in confidences if c >= 90])
            med_conf = len([c for c in confidences if 70 <= c < 90])
            low_conf = len([c for c in confidences if c < 70])

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%")

            with col2:
                high_pct = (high_conf / len(confidences) * 100)
                st.metric("High (≥90%)", f"{high_pct:.1f}%", delta=f"{high_conf} files")

            with col3:
                med_pct = (med_conf / len(confidences) * 100)
                st.metric("Medium (70-89%)", f"{med_pct:.1f}%", delta=f"{med_conf} files")

            with col4:
                low_pct = (low_conf / len(confidences) * 100)
                st.metric("Low (<70%)", f"{low_pct:.1f}%", delta=f"{low_conf} files")

        # Department classification breakdown
        st.subheader("Top Classified Departments")

        dept_counter = Counter()
        for r in results:
            if r.get('tier') not in ['error', 'failed']:
                dept_code = r.get('dept_code')
                dept_name = r.get('dept_name')
                if dept_code:
                    dept_counter[f"{dept_code} - {dept_name}"] += 1

        if dept_counter:
            top_depts = dept_counter.most_common(10)
            df_data = []
            for dept, count in top_depts:
                pct = (count / len([r for r in results if r.get('tier') not in ['error', 'failed']]) * 100)
                df_data.append({
                    'Department': dept,
                    'Files': count,
                    'Percentage': f"{pct:.1f}%"
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, width='stretch', hide_index=True)

        # Errors
        errors = stats.get('errors', 0)
        if errors > 0:
            st.warning(f"⚠️ {errors} files had classification errors (insufficient content)")

    st.markdown("---")

    # === ACTION ITEMS ===
    st.header("🎯 Action Items")

    if inventory:
        stats = inventory.get('statistics', {})
        total_files = stats.get('total_files', 0)

        issues = []

        # Naming issues
        naming_issues = stats.get('naming_issues', 0)
        if naming_issues > 0:
            pct = (naming_issues / total_files * 100) if total_files > 0 else 0
            if pct > 50:
                st.error(f"🔴 **Critical:** {naming_issues:,} files need renaming ({pct:.0f}% non-compliant)")
            elif pct > 20:
                st.warning(f"🟡 **Action Needed:** {naming_issues:,} files need renaming ({pct:.0f}% non-compliant)")
            else:
                st.info(f"🔵 **Minor:** {naming_issues:,} files need renaming ({pct:.0f}% non-compliant)")
        else:
            st.success("✅ All files follow naming convention")

        # Duplicates
        dupes = stats.get('duplicate_groups', 0)
        if dupes > 0:
            st.warning(f"🟡 **Storage Optimization:** {dupes} duplicate file groups can be reviewed")

        # Classification errors
        if classification:
            errors = classification['statistics'].get('errors', 0)
            if errors > 0:
                st.info(f"🔵 **Review Needed:** {errors} files failed classification (OCR issues)")

    st.markdown("---")

    # === SYSTEM HEALTH ===
    st.header("💚 System Health")

    health_score = 0
    max_score = 4

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Checklist")

        # Check 1: Naming compliance
        if inventory:
            compliance_pct = (stats.get('naming_compliant', 0) / stats.get('total_files', 1) * 100)
            if compliance_pct >= 50:
                st.success("✅ Naming compliance ≥ 50%")
                health_score += 1
            else:
                st.error(f"❌ Naming compliance: {compliance_pct:.1f}%")

        # Check 2: PARA structure exists
        if para_structure and any(para_structure.values()):
            st.success("✅ PARA structure implemented")
            health_score += 1
        else:
            st.error("❌ PARA structure not set up")

        # Check 3: Classification system working
        if classification:
            avg_conf = classification['statistics'].get('tier1_success', 0) + classification['statistics'].get('tier2_needed', 0)
            if avg_conf > 0:
                st.success("✅ Classification system operational")
                health_score += 1
            else:
                st.error("❌ No classifications run")

        # Check 4: Cost efficiency
        if classification:
            tier1_pct = (classification['statistics'].get('tier1_success', 0) /
                        classification['statistics'].get('total_files', 1) * 100)
            if tier1_pct >= 25:
                st.success(f"✅ Cost efficient ({tier1_pct:.0f}% FREE)")
                health_score += 1
            else:
                st.warning(f"⚠️ Low FREE processing: {tier1_pct:.0f}%")

    with col2:
        st.subheader("Overall Score")

        score_pct = (health_score / max_score * 100)

        if score_pct >= 75:
            st.success(f"## {score_pct:.0f}% 💚")
            st.write("**Status:** System is healthy and operating efficiently")
        elif score_pct >= 50:
            st.warning(f"## {score_pct:.0f}% 🟡")
            st.write("**Status:** System functional but needs attention")
        else:
            st.error(f"## {score_pct:.0f}% 🔴")
            st.write("**Status:** System needs immediate attention")

    # Footer
    st.markdown("---")
    st.caption("Dashboard refresh: Use browser refresh • Data sources: file_inventory.json, hybrid_results_*.json, PARA folders")

if __name__ == "__main__":
    main()
