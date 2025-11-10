"""
PROJ344 Master Dashboard - 5W+H Framework
Comprehensive legal intelligence with deep visual analytics
Allows independent querying by: Who, What, When, Where, Why, How
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from supabase import create_client
import os
from datetime import datetime, timedelta
from collections import Counter
import re

# Page configuration
st.set_page_config(
    page_title="PROJ344 Master Dashboard - 5W+H Framework",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visuals
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .smoking-gun {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("⚠️ Supabase credentials not found in environment variables")
        return None
    return create_client(url, key)

# Load all documents
@st.cache_data(ttl=300)
def load_documents():
    """Load all legal documents from Supabase"""
    supabase = init_supabase()
    if not supabase:
        return pd.DataFrame()

    try:
        response = supabase.table('legal_documents').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert dates
            if 'processed_at' in df.columns:
                df['processed_at'] = pd.to_datetime(df['processed_at'])
            if 'document_date' in df.columns:
                df['document_date'] = pd.to_datetime(df['document_date'], errors='coerce')
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading documents: {e}")
        return pd.DataFrame()

# Extract entities from documents
def extract_entities(df):
    """Extract WHO, WHAT, WHEN, WHERE, WHY, HOW from documents"""
    entities = {
        'who': set(),
        'what': set(),
        'when': [],
        'where': set(),
        'why': set(),
        'how': set()
    }

    # WHO: Extract names from key quotes and summaries
    name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'

    for _, row in df.iterrows():
        # WHO
        if pd.notna(row.get('summary')):
            names = re.findall(name_pattern, str(row['summary']))
            entities['who'].update(names)

        # WHAT
        if pd.notna(row.get('document_type')):
            entities['what'].add(row['document_type'])

        # WHEN
        if pd.notna(row.get('document_date')):
            entities['when'].append(row['document_date'])

        # WHERE
        if pd.notna(row.get('docket_number')):
            # Extract jurisdiction from docket
            entities['where'].add(row['docket_number'].split('-')[0] if '-' in row['docket_number'] else 'Unknown')

        # WHY
        if pd.notna(row.get('purpose')):
            entities['why'].add(row['purpose'])

        # HOW
        if pd.notna(row.get('fraud_indicators')):
            if isinstance(row['fraud_indicators'], list):
                entities['how'].update(row['fraud_indicators'])

    return entities

# Main header
st.markdown('<div class="main-header">⚖️ PROJ344 Master Dashboard</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">5W+H Framework: Who • What • When • Where • Why • How</p>', unsafe_allow_html=True)
st.markdown("---")

# Load data
df = load_documents()

if df.empty:
    st.warning("⚠️ No documents found in database")
    st.stop()

# Extract entities
entities = extract_entities(df)

# Sidebar - Framework Selection
st.sidebar.title("🔍 Query Framework")
st.sidebar.markdown("Select dimension to analyze:")

framework_choice = st.sidebar.radio(
    "Analysis Dimension",
    ["🏠 Overview", "👤 WHO", "📄 WHAT", "📅 WHEN", "📍 WHERE", "❓ WHY", "⚙️ HOW", "🎯 Custom Query"],
    index=0
)

# Calculate key metrics
total_docs = len(df)
smoking_guns = len(df[df['relevancy_number'] >= 900]) if 'relevancy_number' in df.columns else 0
perjury_docs = len(df[df['contains_false_statements'] == True]) if 'contains_false_statements' in df.columns else 0
avg_relevancy = df['relevancy_number'].mean() if 'relevancy_number' in df.columns else 0

# ====================
# OVERVIEW DASHBOARD
# ====================
if framework_choice == "🏠 Overview":
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Total Documents", f"{total_docs:,}")
    with col2:
        st.metric("🔥 Smoking Guns", smoking_guns, delta=f"{(smoking_guns/total_docs*100):.1f}%" if total_docs > 0 else "0%")
    with col3:
        st.metric("⚠️ Perjury Indicators", perjury_docs)
    with col4:
        st.metric("📈 Avg Relevancy", f"{avg_relevancy:.0f}")

    st.markdown("---")

    # 5W+H Overview Grid
    st.markdown("### 🗺️ 5W+H Intelligence Map")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 👤 WHO")
        st.info(f"{len(entities['who'])} unique individuals identified")
        if entities['who']:
            top_people = list(entities['who'])[:5]
            for person in top_people:
                st.write(f"• {person}")

    with col2:
        st.markdown("#### 📄 WHAT")
        st.info(f"{len(entities['what'])} document types")
        if entities['what']:
            for doc_type in entities['what']:
                count = len(df[df['document_type'] == doc_type])
                st.write(f"• {doc_type}: {count}")

    with col3:
        st.markdown("#### 📅 WHEN")
        st.info(f"{len(entities['when'])} documents with dates")
        if entities['when']:
            min_date = min(entities['when'])
            max_date = max(entities['when'])
            st.write(f"• Range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📍 WHERE")
        st.info(f"{len(entities['where'])} jurisdictions")
        for loc in entities['where']:
            st.write(f"• {loc}")

    with col2:
        st.markdown("#### ❓ WHY")
        st.info(f"{len(entities['why'])} purposes identified")
        for purpose in list(entities['why'])[:5]:
            st.write(f"• {purpose}")

    with col3:
        st.markdown("#### ⚙️ HOW")
        st.info(f"{len(entities['how'])} methods/indicators")
        for method in list(entities['how'])[:5]:
            st.write(f"• {method}")

    st.markdown("---")

    # Scoring distribution
    st.markdown("### 📊 PROJ344 Scoring Distribution")

    if 'relevancy_number' in df.columns:
        fig = make_subplots(
            rows=1, cols=4,
            subplot_titles=('Relevancy', 'Micro', 'Macro', 'Legal'),
            specs=[[{'type': 'histogram'}, {'type': 'histogram'},
                   {'type': 'histogram'}, {'type': 'histogram'}]]
        )

        fig.add_trace(
            go.Histogram(x=df['relevancy_number'], name='Relevancy', marker_color='#1f77b4'),
            row=1, col=1
        )
        fig.add_trace(
            go.Histogram(x=df['micro_number'], name='Micro', marker_color='#ff7f0e'),
            row=1, col=2
        )
        fig.add_trace(
            go.Histogram(x=df['macro_number'], name='Macro', marker_color='#2ca02c'),
            row=1, col=3
        )
        fig.add_trace(
            go.Histogram(x=df['legal_number'], name='Legal', marker_color='#d62728'),
            row=1, col=4
        )

        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ====================
# WHO ANALYSIS
# ====================
elif framework_choice == "👤 WHO":
    st.markdown("## 👤 WHO: People & Parties Analysis")
    st.markdown("Analyze individuals, attorneys, judges, and parties involved in the case")

    # Extract and count people mentions
    all_people = []
    for _, row in df.iterrows():
        if pd.notna(row.get('summary')):
            names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', str(row['summary']))
            all_people.extend(names)

    if all_people:
        people_counts = Counter(all_people)
        top_people = people_counts.most_common(20)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Bar chart of most mentioned people
            people_df = pd.DataFrame(top_people, columns=['Person', 'Mentions'])
            fig = px.bar(
                people_df,
                x='Mentions',
                y='Person',
                orientation='h',
                title='Most Mentioned Individuals',
                color='Mentions',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📊 People Statistics")
            st.metric("Total Unique Individuals", len(people_counts))
            st.metric("Total Mentions", sum(people_counts.values()))

            st.markdown("### 🔍 Top Individuals")
            for person, count in top_people[:10]:
                st.write(f"**{person}**: {count} mentions")

    # Search for specific person
    st.markdown("---")
    st.markdown("### 🔎 Search for Specific Person")
    search_person = st.text_input("Enter name to search:")

    if search_person:
        matching_docs = df[df['summary'].str.contains(search_person, case=False, na=False)]
        st.write(f"Found **{len(matching_docs)}** documents mentioning '{search_person}'")

        if not matching_docs.empty:
            for _, doc in matching_docs.iterrows():
                with st.expander(f"📄 {doc.get('file_name', 'Unknown')} - Relevancy: {doc.get('relevancy_number', 'N/A')}"):
                    st.write(f"**Summary:** {doc.get('summary', 'No summary')}")
                    st.write(f"**Document Type:** {doc.get('document_type', 'Unknown')}")

# ====================
# WHAT ANALYSIS
# ====================
elif framework_choice == "📄 WHAT":
    st.markdown("## 📄 WHAT: Document Types & Evidence Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Document type distribution
        if 'document_type' in df.columns:
            doc_type_counts = df['document_type'].value_counts()
            fig = px.pie(
                values=doc_type_counts.values,
                names=doc_type_counts.index,
                title='Document Type Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Category distribution
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title='Documents by Category',
                labels={'x': 'Category', 'y': 'Count'},
                color=category_counts.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Document type breakdown with scores
    st.markdown("### 📊 Document Type Analysis")

    if 'document_type' in df.columns and 'relevancy_number' in df.columns:
        type_analysis = df.groupby('document_type').agg({
            'relevancy_number': ['mean', 'max', 'count'],
            'contains_false_statements': 'sum'
        }).round(1)

        type_analysis.columns = ['Avg Relevancy', 'Max Relevancy', 'Count', 'Perjury Indicators']
        type_analysis = type_analysis.sort_values('Avg Relevancy', ascending=False)

        st.dataframe(type_analysis, use_container_width=True)

# ====================
# WHEN ANALYSIS
# ====================
elif framework_choice == "📅 WHEN":
    st.markdown("## 📅 WHEN: Timeline & Chronological Analysis")

    if 'document_date' in df.columns or 'processed_at' in df.columns:
        date_col = 'document_date' if 'document_date' in df.columns else 'processed_at'

        # Timeline of documents
        df_dated = df[df[date_col].notna()].copy()
        df_dated['date'] = pd.to_datetime(df_dated[date_col])
        df_dated = df_dated.sort_values('date')

        # Timeline chart
        fig = px.scatter(
            df_dated,
            x='date',
            y='relevancy_number' if 'relevancy_number' in df.columns else df_dated.index,
            size='relevancy_number' if 'relevancy_number' in df.columns else None,
            color='document_type' if 'document_type' in df.columns else None,
            title='Document Timeline',
            hover_data=['file_name', 'document_type'] if 'file_name' in df.columns else None
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Documents by month
        df_dated['month'] = df_dated['date'].dt.to_period('M').astype(str)
        monthly_counts = df_dated['month'].value_counts().sort_index()

        fig = px.bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            title='Documents by Month',
            labels={'x': 'Month', 'y': 'Document Count'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Date range filter
        st.markdown("### 🔍 Filter by Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min(df_dated['date']))
        with col2:
            end_date = st.date_input("End Date", max(df_dated['date']))

        filtered = df_dated[(df_dated['date'] >= pd.Timestamp(start_date)) &
                           (df_dated['date'] <= pd.Timestamp(end_date))]

        st.write(f"**{len(filtered)}** documents in date range")

        if not filtered.empty:
            st.dataframe(
                filtered[['file_name', 'document_type', 'date', 'relevancy_number']].head(20),
                use_container_width=True
            )

# ====================
# WHERE ANALYSIS
# ====================
elif framework_choice == "📍 WHERE":
    st.markdown("## 📍 WHERE: Jurisdiction & Location Analysis")

    # Jurisdiction breakdown
    if 'docket_number' in df.columns:
        df['jurisdiction'] = df['docket_number'].str.split('-').str[0]
        jurisdiction_counts = df['jurisdiction'].value_counts()

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = px.bar(
                x=jurisdiction_counts.index,
                y=jurisdiction_counts.values,
                title='Documents by Jurisdiction',
                labels={'x': 'Jurisdiction', 'y': 'Document Count'},
                color=jurisdiction_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📊 Jurisdiction Stats")
            st.metric("Total Jurisdictions", len(jurisdiction_counts))
            st.markdown("### Top Jurisdictions")
            for jurisdiction, count in jurisdiction_counts.head(5).items():
                st.write(f"**{jurisdiction}**: {count} documents")

# ====================
# WHY ANALYSIS
# ====================
elif framework_choice == "❓ WHY":
    st.markdown("## ❓ WHY: Purpose & Intent Analysis")

    # Purpose analysis
    if 'purpose' in df.columns:
        purpose_counts = df['purpose'].value_counts().head(15)

        fig = px.treemap(
            names=purpose_counts.index,
            parents=[''] * len(purpose_counts),
            values=purpose_counts.values,
            title='Document Purposes (Treemap)'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    # Fraud/Perjury reasons
    st.markdown("### ⚠️ Fraud & Perjury Indicators")

    if 'fraud_indicators' in df.columns:
        all_indicators = []
        for indicators in df['fraud_indicators'].dropna():
            if isinstance(indicators, list):
                all_indicators.extend(indicators)

        if all_indicators:
            indicator_counts = Counter(all_indicators)
            top_indicators = indicator_counts.most_common(10)

            indicators_df = pd.DataFrame(top_indicators, columns=['Indicator', 'Count'])
            fig = px.bar(
                indicators_df,
                x='Count',
                y='Indicator',
                orientation='h',
                title='Top Fraud/Perjury Indicators',
                color='Count',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

# ====================
# HOW ANALYSIS
# ====================
elif framework_choice == "⚙️ HOW":
    st.markdown("## ⚙️ HOW: Methods & Mechanisms Analysis")

    # Methods of violation
    st.markdown("### 🔍 Methods of Constitutional Violations")

    if 'fraud_indicators' in df.columns or 'perjury_indicators' in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Fraud Methods")
            fraud_methods = []
            for indicators in df['fraud_indicators'].dropna():
                if isinstance(indicators, list):
                    fraud_methods.extend(indicators)

            if fraud_methods:
                fraud_counts = Counter(fraud_methods).most_common(10)
                for method, count in fraud_counts:
                    st.write(f"• {method}: **{count}** occurrences")

        with col2:
            st.markdown("#### Perjury Methods")
            perjury_methods = []
            if 'perjury_indicators' in df.columns:
                for indicators in df['perjury_indicators'].dropna():
                    if isinstance(indicators, list):
                        perjury_methods.extend(indicators)

            if perjury_methods:
                perjury_counts = Counter(perjury_methods).most_common(10)
                for method, count in perjury_counts:
                    st.write(f"• {method}: **{count}** occurrences")

    # Process/workflow analysis
    st.markdown("### 📊 Document Processing Methods")

    if 'api_cost_usd' in df.columns:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total API Cost", f"${df['api_cost_usd'].sum():.2f}")
        with col2:
            st.metric("Avg Cost/Doc", f"${df['api_cost_usd'].mean():.4f}")
        with col3:
            st.metric("Processing Success Rate", f"{(df['relevancy_number'].notna().sum() / len(df) * 100):.1f}%")

# ====================
# CUSTOM QUERY
# ====================
elif framework_choice == "🎯 Custom Query":
    st.markdown("## 🎯 Custom Query Builder")
    st.markdown("Build complex queries combining multiple dimensions")

    # Multi-dimensional filters
    col1, col2 = st.columns(2)

    with col1:
        # WHO filter
        st.markdown("### 👤 WHO")
        search_person = st.text_input("Person/Entity:")

        # WHAT filter
        st.markdown("### 📄 WHAT")
        doc_types = st.multiselect("Document Types:", df['document_type'].unique() if 'document_type' in df.columns else [])

        # WHEN filter
        st.markdown("### 📅 WHEN")
        date_range = st.date_input("Date Range:", [])

    with col2:
        # WHERE filter
        st.markdown("### 📍 WHERE")
        if 'docket_number' in df.columns:
            df['jurisdiction'] = df['docket_number'].str.split('-').str[0]
            jurisdictions = st.multiselect("Jurisdictions:", df['jurisdiction'].unique())

        # WHY filter
        st.markdown("### ❓ WHY")
        min_relevancy = st.slider("Minimum Relevancy:", 0, 999, 700)

        # HOW filter
        st.markdown("### ⚙️ HOW")
        show_perjury_only = st.checkbox("Perjury Indicators Only")

    # Apply filters
    filtered_df = df.copy()

    if search_person:
        filtered_df = filtered_df[filtered_df['summary'].str.contains(search_person, case=False, na=False)]

    if doc_types:
        filtered_df = filtered_df[filtered_df['document_type'].isin(doc_types)]

    if 'relevancy_number' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['relevancy_number'] >= min_relevancy]

    if show_perjury_only and 'contains_false_statements' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['contains_false_statements'] == True]

    # Display results
    st.markdown("---")
    st.markdown(f"### 📊 Query Results: {len(filtered_df)} documents")

    if not filtered_df.empty:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Documents Found", len(filtered_df))
        with col2:
            st.metric("Avg Relevancy", f"{filtered_df['relevancy_number'].mean():.0f}" if 'relevancy_number' in filtered_df.columns else "N/A")
        with col3:
            st.metric("Smoking Guns", len(filtered_df[filtered_df['relevancy_number'] >= 900]) if 'relevancy_number' in filtered_df.columns else 0)
        with col4:
            st.metric("Perjury Docs", len(filtered_df[filtered_df['contains_false_statements'] == True]) if 'contains_false_statements' in filtered_df.columns else 0)

        # Results table
        display_cols = ['file_name', 'document_type', 'relevancy_number', 'summary']
        available_cols = [col for col in display_cols if col in filtered_df.columns]

        st.dataframe(
            filtered_df[available_cols].sort_values('relevancy_number', ascending=False) if 'relevancy_number' in available_cols else filtered_df[available_cols],
            use_container_width=True,
            height=400
        )

        # Export option
        if st.button("📥 Export Results to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"proj344_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>PROJ344 Master Dashboard - Case J24-00478: In re Ashe Bucknor</p>
    <p>For Ashe. For Justice. For All Children. 🛡️</p>
</div>
""", unsafe_allow_html=True)
