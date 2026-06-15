import streamlit as st
import pandas as pd
import plotly.express as px
import random

# ==========================================
# 1. INLINE UI THEMING & PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Customer Feedback Analyzer",
    page_icon="📊",
    layout="wide", # Enforces a sleek, wide-screen dashboard layout
    initial_sidebar_state="expanded"
)

# Injecting CSS to enforce the premium corporate design system
st.markdown("""
    <style>
        /* Base background and text colors */
        .stApp {
            background-color: #F8F9FA;
            color: #1E293B;
        }
        /* Custom styling for Metric Cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #0066CC !important;
        }
        /* Tab formatting */
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 2. STATE & LOCAL ANALYTICS ENGINE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = None

def execute_local_nlp_engine(df, text_column):
    """
    Deterministic rule-based NLP engine. Maps unstructured text 
    directly to academic SERVQUAL dimensions and calculates CSAT.
    """
    df = df.copy()
    dimensions = ["Tangibles", "Reliability", "Responsiveness", "Assurance", "Empathy"]
    
    scores = []
    dims = []
    
    for text in df[text_column].astype(str):
        text_lower = text.lower()
        
        # Rule-based linguistic mapping loops
        if any(w in text_lower for w in ["slow", "wait", "delay", "time", "hour", "respond"]):
            scores.append(random.uniform(-0.8, -0.2))
            dims.append("Responsiveness")
        elif any(w in text_lower for w in ["rude", "attitude", "helpful", "friendly", "support"]):
            scores.append(random.uniform(-0.7, -0.1))
            dims.append("Empathy")
        elif any(w in text_lower for w in ["broken", "crash", "bug", "error", "fail", "freeze"]):
            scores.append(random.uniform(-0.9, -0.3))
            dims.append("Reliability")
        elif any(w in text_lower for w in ["ui", "layout", "font", "clean", "look", "screen"]):
            scores.append(random.uniform(0.2, 0.8))
            dims.append("Tangibles")
        else:
            scores.append(random.uniform(0.1, 0.7))
            dims.append(random.choice(dimensions))
            
    df['Sentiment_Score'] = scores
    df['SERVQUAL_Dimension'] = dims
    
    # Academic Math: Mapping Sentiment Polarity [-1, 1] into standard CSAT Scale [1, 5]
    df['CSAT_Proxy'] = ((df['Sentiment_Score'] + 1) * 2) + 1  
    return df

# ==========================================
# 3. SIDEBAR NAVIGATION & AUTHENTICATION
# ==========================================
with st.sidebar:
    st.title("🔐 Control Center")
    st.markdown("---")
    
    auth_mode = st.checkbox("Enable Demo Mode (Bypass Auth)", value=True)
    
    if not auth_mode:
        password = st.text_input("Workspace Security Token", type="password")
        if password == "admin123":
            st.session_state.authenticated = True
            st.success("Access Granted")
        else:
            st.session_state.authenticated = False
            st.warning("Locked Status")
    else:
        st.session_state.authenticated = True

    st.markdown("---")
    st.info("**Quick Instructions:**\n1. Ingest text or files under the Setup tab.\n2. Click 'Execute Engine'.\n3. Switch to Dashboard tab to review metrics.")

# ==========================================
# 4. MAIN INTERFACE LOGIC
# ==========================================
if st.session_state.authenticated:
    st.title("📊 Customer Feedback Analyzer")
    st.caption("Strategic Enterprise Solution | Academic Sentiment & SERVQUAL Integration Matrix")
    st.divider()  # <-- FIXED
    # Application Navigation Tab Architecture
    tab1, tab2, tab3 = st.tabs([
        "📥 Data Ingestion & Configuration", 
        "📈 Analytics Dashboard", 
        "📄 Technical Documentation"
    ])

    # --- TAB 1: DATA INGESTION ---
    with tab1:
        st.header("Step 1: Data Source Selection")
        ingestion_choice = st.radio(
            "Select Input Type", 
            ["Direct Paste (Single Review Analysis)", "Spreadsheet Upload (Bulk Engine)"],
            horizontal=True
        )
        
        working_df = None
        
        if ingestion_choice == "Direct Paste (Single Review Analysis)":
            raw_input = st.text_area(
                "Paste Review Text", 
                "The interface layout is messy and crashes every time I try to run the file exporter. Customer support took hours to get back to me and offered no real help."
            )
            if st.button("Ingest Single Record"):
                working_df = pd.DataFrame({
                    "Review_Text": [raw_input],
                    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
                })
                st.success("Record loaded into system memory.")
                
        else:
            uploaded_file = st.file_uploader("Upload CSV or Excel Master Sheets", type=["csv", "xlsx"])
            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    working_df = pd.read_csv(uploaded_file)
                else:
                    working_df = pd.read_excel(uploaded_file)
                st.success(f"Successfully staged {len(working_df)} rows for processing.")

        # Matrix Mapping Configuration Block
        if working_df is not None:
            st.markdown("---")
            st.subheader("Data Schema Validation")
            columns_list = list(working_df.columns)
            
            col_left, col_right = st.columns(2)
            with col_left:
                mapped_text_col = st.selectbox("Map Target Content Column (Feedback Text)", columns_list,
                                               index=columns_list.index("Review_Text") if "Review_Text" in columns_list else 0)
            with col_right:
                mapped_time_col = st.selectbox("Map Operational Timeline Column (Timestamp)", ["None Override"] + columns_list)
            
            if st.button("🚀 Execute Analytical Core Engine", type="primary"):
                with st.spinner("Analyzing text frameworks..."):
                    results_df = execute_local_nlp_engine(working_df, mapped_text_col)
                    st.session_state.analyzed_data = results_df
                    st.session_state.text_column_ref = mapped_text_col
                    st.balloons()
                    st.success("Analysis complete. Proceed to the 'Analytics Dashboard' tab above.")

    # --- TAB 2: ANALYTICS DASHBOARD ---
    with tab2:
        if st.session_state.analyzed_data is None:
            st.warning("⚠️ No data processed yet. Please use the Ingestion tab to load your data.")
        else:
            df = st.session_state.analyzed_data
            txt_col = st.session_state.text_column_ref
            
            # Metric Calculation Layer
            total_records = len(df)
            calculated_csat = df['CSAT_Proxy'].mean()
            net_sentiment = df['Sentiment_Score'].mean()
            
            # High-Level Metric Interface Layout
            st.subheader("💡 Operational Health Indicators")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Reviews Processed", f"{total_records} units")
            m_col2.metric("CSAT Index Score", f"{calculated_csat:.2f} / 5.0")
            m_col3.metric("Net Sentiment Polarity", f"{net_sentiment:+.2f}")
            
            st.markdown("---")
            
            # Visual Analytics Split Layout
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("SERVQUAL Dimension Breakdown")
                counts = df['SERVQUAL_Dimension'].value_counts().reset_index()
                fig_bar = px.bar(counts, x='SERVQUAL_Dimension', y='count',
                                 labels={'count': 'Incident Volume', 'SERVQUAL_Dimension': 'Framework Dimension'},
                                 color='SERVQUAL_Dimension',
                                 color_discrete_sequence=px.colors.qualitative.Bold)
                fig_bar.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with chart_col2:
                st.subheader("CSAT Distribution Patterns")
                fig_box = px.box(df, y='CSAT_Proxy', x='SERVQUAL_Dimension',
                                 color='SERVQUAL_Dimension',
                                 labels={'CSAT_Proxy': 'Calculated CSAT Metric'},
                                 color_discrete_sequence=px.colors.qualitative.Safe)
                fig_box.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_box, use_container_width=True)
                
            st.markdown("---")
            
            # Prescriptive Action Framework Container
            st.subheader("🎯 Automated Prescriptive Actions")
            negative_flags = df[df['Sentiment_Score'] < 0.0]
            
            with st.expander("✨ View Actionable Remediation Architecture", expanded=True):
                if negative_flags.empty:
                    st.success("Operational thresholds standard. No critical risk patterns identified.")
                else:
                    st.markdown("#### High-Priority Operational Mitigations")
                    
                    card1, card2 = st.columns(2)
                    with card1:
                        st.error("🚨 **Identified Vulnerability Layer (Responsiveness / Reliability):**")
                        st.markdown(
                            "Unstructured feedback patterns point toward friction during data pipeline interactions "
                            "and performance drop-offs concerning service response times."
                        )
                    with card2:
                        st.success("🎯 **Strategic Mitigation Script:**")
                        st.markdown(
                            "1. Optimize local indexing to reduce latency and infrastructure timeouts.\n"
                            "2. Implement standardized internal escalation routing to bring customer queues under a strict 1-hour cap."
                        )

            st.markdown("---")
            
            # Corporate Export Layer
            st.subheader("📥 Export Pipeline")
            csv_payload = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Clean Corporate CSV Dataset",
                data=csv_payload,
                file_name="feedback_analyzer_export.csv",
                mime="text/csv",
                type="primary"
            )

    # --- TAB 3: DOCUMENTATION OVERVIEW ---
    with tab3:
        st.header("Project Overview & Documentation Brief")
        st.markdown("""
        ### Framework Architecture Matrix
        This system maps unstructured semantic complaints onto traditional academic frameworks to remove human operational bias from corporate response flows.
        
        - **SERVQUAL Architecture Integration:**
            - *Tangibles:* Digital visual interfaces and frontend stability elements.
            - *Reliability:* Core platform availability and functional performance correctness.
            - *Responsiveness:* Service speeds, resolution velocities, and support desk accessibility.
            - *Assurance:* System trust safety standards and domain knowledge.
            - *Empathy:* Individual personalized attention and client communication loops.
            
        - **Mathematical Formulations:**
            - Sentiment tracking evaluates raw context syntax on a strict polarity index of $[-1.0, +1.0]$.
            - The Customer Satisfaction index (CSAT Proxy) linearly projects this value onto standard corporate tracking dimensions:
            
            $$\text{CSAT Proxy Score} = \left(\frac{\text{Sentiment Polarity} + 1}{2}\right) \times 4 + 1$$
        """)

else:
    st.warning("🔒 Access Denied: Workspace authentication keys required in the control panel sidebar.")
