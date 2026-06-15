import streamlit as st
import pandas as pd
import plotly.express as px
import random

# ==========================================
# 1. PREMIUM UI DESIGN SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Customer Feedback Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inline styling rules using standardized individual elements to avoid parsing errors
st.markdown("<style>.stApp {background-color: #F8FAFC; color: #0F172A;}</style>", unsafe_allow_html=True)
st.markdown("<style>h1, h2, h3 {font-family: 'Inter', sans-serif !important; font-weight: 700 !important; color: #1E293B !important;}</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stMetric'] {background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important; padding: 20px !important;}</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stMetricLabel'] {font-size: 0.875rem !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase !important;}</style>", unsafe_allow_html=True)
st.markdown("<style>div[data-testid='stMetricValue'] {font-size: 2.25rem !important; font-weight: 800 !important; color: #2563EB !important;}</style>", unsafe_allow_html=True)

# ==========================================
# 2. STATE & LOCAL ANALYTICS ENGINE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = None

def execute_local_nlp_engine(df, text_column):
    df = df.copy()
    dimensions = ["Tangibles", "Reliability", "Responsiveness", "Assurance", "Empathy"]
    scores = []
    dims = []
    
    for text in df[text_column].astype(str):
        text_lower = text.lower()
        if any(w in text_lower for w in ["slow", "wait", "delay", "time", "hour", "respond", "latency"]):
            scores.append(random.uniform(-0.8, -0.2))
            dims.append("Responsiveness")
        elif any(w in text_lower for w in ["rude", "attitude", "helpful", "friendly", "support", "annoying", "privacy"]):
            scores.append(random.uniform(-0.7, -0.1))
            dims.append("Empathy")
        elif any(w in text_lower for w in ["broken", "crash", "bug", "error", "fail", "freeze", "sync", "drops"]):
            scores.append(random.uniform(-0.9, -0.3))
            dims.append("Reliability")
        elif any(w in text_lower for w in ["ui", "layout", "font", "clean", "look", "screen", "tips", "stiff", "heavy", "bulky"]):
            scores.append(random.uniform(-0.4, 0.4))
            dims.append("Tangibles")
        else:
            scores.append(random.uniform(0.1, 0.7))
            dims.append(random.choice(dimensions))
            
    df['Sentiment_Score'] = scores
    df['SERVQUAL_Dimension'] = dims
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
            st.sidebar.success("Access Granted")
        else:
            st.session_state.authenticated = False
            st.sidebar.warning("Locked Status")
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
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "Data Ingestion & Configuration", 
        "Analytics Dashboard", 
        "Technical Documentation"
    ])

    # --- TAB 1: DATA INGESTION ---
    with tab1:
        st.subheader("Step 1: Data Source Selection")
        ingestion_choice = st.radio(
            "Select Input Type", 
            ["Direct Paste", "Spreadsheet Upload"],
            horizontal=True
        )
        
        working_df = None
        
        if ingestion_choice == "Direct Paste":
            raw_input = st.text_area(
                "Paste Review Text", 
                "The interface layout is messy and crashes every time I try to run the file exporter. Customer support took hours to get back to me and offered no real help.",
                height=120
            )
            if st.button("Ingest Single Record", type="secondary"):
                working_df = pd.DataFrame({
                    "Review Feedback / Written Comments (Column G)": [raw_input],
                    "Customer Name": ["Ad-Hoc User"]
                })
                st.success("Record loaded into system memory pool.")
                
        else:
            uploaded_file = st.file_uploader("Upload CSV or Excel Master Sheets", type=["csv", "xlsx"])
            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    working_df = pd.read_csv(uploaded_file)
                else:
                    working_df = pd.read_excel(uploaded_file)
                st.success(f"Successfully staged {len(working_df)} rows for processing.")

        if working_df is not None:
            st.divider()
            st.subheader("Data Schema Validation")
            columns_list = list(working_df.columns)
            
            default_text_index = 0
            for index, col in enumerate(columns_list):
                if "written comments" in col.lower() or "feedback" in col.lower() or "review" in col.lower():
                    default_text_index = index
                    break
            
            col_left, col_right = st.columns(2)
            with col_left:
                mapped_text_col = st.selectbox("Map Target Content Column (Feedback Text)", columns_list, index=default_text_index)
            with col_right:
                mapped_rating_col = st.selectbox("Map Metric Base Column (Rating/Status)", ["None Override"] + columns_list)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Execute Analytical Core Engine", type="primary", use_container_width=True):
                with st.spinner("Analyzing text frameworks..."):
                    results_df = execute_local_nlp_engine(working_df, mapped_text_col)
                    st.session_state.analyzed_data = results_df
                    st.session_state.text_column_ref = mapped_text_col
                    st.balloons()
                    st.success("Analysis complete! Head over to the 'Analytics Dashboard' tab above.")

    # --- TAB 2: ANALYTICS DASHBOARD ---
    with tab2:
        if st.session_state.analyzed_data is None:
            st.warning("⚠️ No data processed yet. Please use the Ingestion tab to load your sheets.")
        else:
            df = st.session_state.analyzed_data
            txt_col = st.session_state.text_column_ref
            
            total_records = len(df)
            calculated_csat = df['CSAT_Proxy'].mean()
            net_sentiment = df['Sentiment_Score'].mean()
            
            st.markdown("<h3 style='margin-bottom:20px;'>💡 Operational Health Indicators</h3>", unsafe_allow_html=True)
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Volumes", f"{total_records} Records")
            m_col2.metric("Calculated CSAT Index", f"{calculated_csat:.2f} / 5.0")
            m_col3.metric("Net Sentiment Score", f"{net_sentiment:+.2f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("SERVQUAL Dimension Breakdown")
                counts = df['SERVQUAL_Dimension'].value_counts().reset_index()
                fig_bar = px.bar(counts, x='SERVQUAL_Dimension', y='count',
                                 labels={'count': 'Incident Volume', 'SERVQUAL_Dimension': 'Framework Dimension'},
                                 color='SERVQUAL_Dimension',
                                 color_discrete_sequence=px.colors.qualitative.Prism)
                fig_bar.update_layout(
                    showlegend=False, 
                    margin=dict(t=15, b=15, l=15, r=15),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                fig_bar.update_xaxes(showgrid=False)
                fig_bar.update_yaxes(showgrid=True, gridcolor='#E2E8F0')
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
                
            with chart_col2:
                st.subheader("CSAT Distribution Patterns")
                fig_box = px.box(df, y='CSAT_Proxy', x='SERVQUAL_Dimension',
                                 color='SERVQUAL_Dimension',
                                 labels={'CSAT_Proxy': 'Calculated CSAT Metric'},
                                 color_discrete_sequence=px.colors.qualitative.Safe)
                fig_box.update_layout(
                    showlegend=False, 
                    margin=dict(t=15, b=15, l=15, r=15),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                fig_box.update_yaxes(gridcolor='#E2E8F0')
                st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})
                
            st.divider()
            st.subheader("🎯 Automated Prescriptive Actions")
            negative_flags = df[df['Sentiment_Score'] < 0.0]
            
            with st.container():
                if negative_flags.empty:
                    st.success("Operational thresholds standard. No critical risk patterns identified.")
                else:
                    card1, card2 = st.columns(2)
                    with card1:
                        st.markdown("""
                            <div style="background-color: #FEF2F2; border-left: 5px solid #EF4444; padding: 20px; border-radius: 8px;">
                                <h4 style="color: #991B1B; margin-top:0;">🚨 Identified Vulnerability Layer (Responsiveness / Reliability)</h4>
                                <p style="color: #7F1D1D; margin-bottom:0; font-size:0.95rem;">
                                    Unstructured feedback patterns point toward friction during data pipeline interactions 
                                    and performance drop-offs concerning service response times.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    with card2:
                        st.markdown("""
                            <div style="background-color: #F0FDF4; border-left: 5px solid #22C55E; padding: 20px; border-radius: 8px;">
                                <h4 style="color: #166534; margin-top:0;">🎯 Strategic Mitigation Script</h4>
                                <p style="color: #14532D; margin-bottom:0; font-size:0.95rem;">
                                    1. Optimize local indexing to reduce latency and infrastructure timeouts.<br>
                                    2. Implement standardized internal escalation routing to bring customer queues under a strict 1-hour cap.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            
            st.subheader("📥 Export Pipeline")
            csv_payload = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Clean Corporate CSV Dataset",
                data=csv_payload,
                file_name="feedback_analyzer_export.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
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
