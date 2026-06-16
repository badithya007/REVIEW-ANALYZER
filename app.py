import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIGURATION & ENTERPRISE UI THEME
# ==========================================
st.set_page_config(
    page_title="Enterprise Customer Insights Matrix",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS inject for enterprise look and feel
st.markdown("""
    <style>
        /* Global CSS Overrides */
        .stApp {
            background-color: #FDFEFE;
            color: #1E293B;
        }
        /* Custom styling for standard metrics */
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            color: #0F172A !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: #475569 !important;
        }
        /* Tab Polish */
        .stTabs [data-baseweb="tab"] {
            font-weight: 700;
            font-size: 1.05rem;
            color: #64748B;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #2563EB !important;
            border-bottom-color: #2563EB !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DETERMINISTIC CORE NLP ENGINE
# ==========================================
LEXICON = {
    # Positive Identifiers
    "excellent": 0.9, "perfect": 1.0, "great": 0.7, "good": 0.5, "love": 0.8, 
    "amazing": 0.9, "helpful": 0.6, "friendly": 0.6, "fast": 0.7, "clean": 0.5, 
    "smooth": 0.6, "resolved": 0.7, "easy": 0.6, "satisfied": 0.7, "best": 0.8,
    # Negative Identifiers
    "slow": -0.6, "wait": -0.5, "delay": -0.6, "hours": -0.4, "rude": -0.8, 
    "terrible": -0.9, "worst": -1.0, "broken": -0.8, "crash": -0.9, "bug": -0.7, 
    "error": -0.7, "fail": -0.8, "freeze": -0.8, "horrible": -0.9, "useless": -0.8, 
    "hate": -0.8, "frustrated": -0.7, "confusing": -0.5, "messy": -0.5, "expensive": -0.4
}

SERVQUAL_MAP = {
    "Reliability": ["crash", "bug", "error", "fail", "freeze", "broken", "glitch", "downtime", "log", "loss", "load"],
    "Responsiveness": ["slow", "wait", "delay", "time", "hour", "respond", "speed", "latency", "queue", "pending"],
    "Empathy": ["rude", "attitude", "helpful", "friendly", "support", "care", "ignored", "listen", "understand", "polite"],
    "Tangibles": ["ui", "layout", "font", "clean", "look", "screen", "interface", "design", "visual", "buttons", "aesthetic"],
    "Assurance": ["security", "safe", "trust", "privacy", "leak", "hack", "confident", "guarantee", "compliance", "legal"]
}

def analyze_feedback(text):
    """
    100% Deterministic rule-based sentiment and SERVQUAL mapping.
    Eliminates all random variation for auditable compliance reporting.
    """
    if not isinstance(text, str) or text.strip() == "":
        return 0.0, "General", 3.0
    
    tokens = text.lower().split()
    
    # 1. Deterministic Sentiment Polarity Scoring
    score_sum = 0.0
    match_count = 0
    for token in tokens:
        # Clean trailing/leading punctuation
        clean_token = token.strip(".,!?\"'()[]{}")
        if clean_token in LEXICON:
            score_sum += LEXICON[clean_token]
            match_count += 1
            
    sentiment_score = score_sum / match_count if match_count > 0 else 0.0
    
    # 2. SERVQUAL Category Mapping Strategy
    dimension_scores = {dim: 0 for dim in SERVQUAL_MAP}
    for dim, keywords in SERVQUAL_MAP.items():
        for kw in keywords:
            if kw in text.lower():
                dimension_scores[dim] += 1
                
    max_matches = max(dimension_scores.values())
    if max_matches > 0:
        # Tie-breaker handles alphabetically to preserve full determinism
        chosen_dimension = [k for k, v in dimension_scores.items() if v == max_matches][0]
    else:
        chosen_dimension = "General"
        
    # 3. Linear Interpolation to Exact CSAT Scale [1.0, 5.0]
    csat_proxy = round(((sentiment_score + 1.0) * 2.0) + 1.0, 2)
    
    return round(sentiment_score, 2), chosen_dimension, csat_proxy

def process_dataframe(df, text_col):
    """Applies execution engine mapping safely across target records"""
    df = df.copy()
    results = df[text_col].astype(str).apply(analyze_feedback)
    df['Sentiment_Score'] = [r[0] for r in results]
    df['SERVQUAL_Dimension'] = [r[1] for r in results]
    df['CSAT_Proxy'] = [r[2] for r in results]
    return df

# ==========================================
# 3. MOCK DATA INJECTION SYSTEM
# ==========================================
def generate_mock_data():
    samples = [
        ("The platform UI layout looks super clean and modern, but checkout keeps throwing a database execution error.", "2026-06-14 09:12"),
        ("Customer support staff were incredibly friendly and helped me resolve my pipeline access token error within minutes.", "2026-06-14 11:45"),
        ("Extremely slow load performance today. I've been stuck waiting for over an hour for data exports to complete.", "2026-06-15 08:22"),
        ("I feel totally safe using this system. Their data compliance framework and security architecture are outstanding.", "2026-06-15 14:30"),
        ("The interface font options are hard to read and the screen alignment looks broken on small displays.", "2026-06-16 10:02"),
        ("Absolute downtime crash failure during our presentation. Complete application freeze.", "2026-06-16 10:15"),
        ("The technical team was completely rude and ignored my open ticket loops for two full days.", "2026-06-16 10:30")
    ]
    texts, times = zip(*samples)
    return pd.DataFrame({"Review_Text": list(texts), "Timestamp": list(times)})

# ==========================================
# 4. STATE ENGINE SETUP
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = None

# ==========================================
# 5. CONTROL PANEL SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🔐 Intelligence Control Panel")
    st.markdown("---")
    
    bypass_auth = st.checkbox("Demo Override (Bypass Security Token)", value=True)
    
    if not bypass_auth:
        token_input = st.text_input("Workspace Security Token", type="password")
        if token_input == "admin123":
            st.session_state.authenticated = True
            st.success("Authorization Confirmed")
        else:
            st.session_state.authenticated = False
            st.warning("Locked Status Protocol Active")
    else:
        st.session_state.authenticated = True

    st.markdown("---")
    st.subheader("Data Engine Utilities")
    if st.button("Inject High-Fidelity Mock Dataset", use_container_width=True, type="secondary"):
        st.session_state.staged_df = generate_mock_data()
        st.toast("Corporate sample data loaded successfully!", icon="📥")
        
    if st.button("Reset Global App Memory State", use_container_width=True, type="negative"):
        st.session_state.analyzed_data = None
        if "staged_df" in st.session_state:
            del st.session_state.staged_df
        st.rerun()

# ==========================================
# 6. PRIMARY RUNTIME SYSTEM
# ==========================================
if st.session_state.authenticated:
    st.title("📊 Customer Feedback Analytics Engine")
    st.caption("Enterprise-Grade Feedback Vectoring Platform | Linear CSAT Mapping & Academic SERVQUAL Extraction Matrices")
    st.divider()

    tab_ingest, tab_dashboard, tab_actions, tab_docs = st.tabs([
        "📥 Data Hub & Extraction Setup", 
        "📈 Strategic Dashboard", 
        "🎯 Automated Remediation Blueprint",
        "📄 Mathematical Engineering Brief"
    ])

    # --- TAB 1: DATA PIPELINES ---
    with tab_ingest:
        st.subheader("Ingestion Matrix Pipelines")
        input_strategy = st.radio(
            "Select Processing Vector:",
            ["Direct Raw Text Analysis Block", "Enterprise Data File Upload (Bulk Engine)"],
            horizontal=True
        )
        
        active_df = st.session_state.get("staged_df", None)
        
        if input_strategy == "Direct Raw Text Analysis Block":
            user_text = st.text_area(
                "Input Raw Text Feedback String",
                value="The data dashboard layouts look completely clean and crisp, but the database connection keeps crashing out with an unexpected system bug."
            )
            if st.button("Execute Single Sequence Parsing"):
                active_df = pd.DataFrame({
                    "Review_Text": [user_text],
                    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
                })
                st.session_state.staged_df = active_df
                st.success("Single record captured in short-term buffer memory.")
                
        else:
            uploaded_file = st.file_uploader("Upload CSV or Excel Master sheets", type=["csv", "xlsx"])
            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    active_df = pd.read_csv(uploaded_file)
                else:
                    active_df = pd.read_excel(uploaded_file)
                st.session_state.staged_df = active_df
                st.success(f"Staged {len(active_df)} target source rows for ingestion execution.")

        if active_df is not None:
            st.markdown("---")
            st.subheader("Data Schema Validation Mapping")
            columns = list(active_df.columns)
            
            c1, c2 = st.columns(2)
            with c1:
                target_text_col = st.selectbox(
                    "Target Content Column (Unstructured Feedback text)", 
                    options=columns,
                    index=columns.index("Review_Text") if "Review_Text" in columns else 0
                )
            with c2:
                target_time_col = st.selectbox(
                    "Target Temporal Column (Operational Timestamp)", 
                    options=["None - Bypass Temporal Alignment"] + columns,
                    index=columns.index("Timestamp") if "Timestamp" in columns else 0
                )
                
            if st.button("🚀 Fire Core Analytical Analytics Engine", type="primary", use_container_width=True):
                with st.spinner("Processing deep lexicon matrix calculations..."):
                    out_df = process_dataframe(active_df, target_text_col)
                    st.session_state.analyzed_data = out_df
                    st.session_state.text_column_ref = target_text_col
                    st.balloons()
                    st.success("Execution complete. Navigate to the 'Strategic Dashboard' tab to view extracted metrics.")

    # --- TAB 2: ANALYTICS DASHBOARD ---
    with tab_dashboard:
        if st.session_state.analyzed_data is None:
            st.warning("⚠️ Processing Engine Idle. Please stage data inside the Ingestion Matrix tab first.")
        else:
            res_df = st.session_state.analyzed_data
            
            # Mathematical Metrics Compilations
            total_vol = len(res_df)
            avg_csat = res_df['CSAT_Proxy'].mean()
            avg_polarity = res_df['Sentiment_Score'].mean()
            positive_share = (len(res_df[res_df['Sentiment_Score'] > 0]) / total_vol) * 100
            
            # High-Level Metrics Layout Banner
            st.subheader("💡 Strategic Operations Performance Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Feedback Volume", f"{total_vol} Units")
            m2.metric("Aggregated CSAT Proxy Score", f"{avg_csat:.2f} / 5.0")
            m3.metric("Net Sentiment Polarity Index", f"{avg_polarity:+.2f}")
            m4.metric("Positive Sentiment Ratio", f"{positive_share:.1f}%")
            
            st.markdown("---")
            
            # Chart Generation Section
            chart1, chart2 = st.columns(2)
            
            with chart1:
                st.subheader("SERVQUAL Dimensions Performance Density")
                counts = res_df['SERVQUAL_Dimension'].value_counts().reset_index()
                counts.columns = ['Dimension', 'Volume Tracker']
                
                fig_bar = px.bar(
                    counts, x='Dimension', y='Volume Tracker',
                    color='Dimension',
                    color_discrete_sequence=px.colors.qualitative.G10
                )
                fig_bar.update_layout(showlegend=False, margin=dict(t=15, b=15, l=15, r=15), height=380)
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with chart2:
                st.subheader("CSAT Distribution Spread Profile")
                fig_box = px.box(
                    res_df, x='SERVQUAL_Dimension', y='CSAT_Proxy',
                    color='SERVQUAL_Dimension',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_box.update_layout(showlegend=False, margin=dict(t=15, b=15, l=15, r=15), height=380)
                st.plotly_chart(fig_box, use_container_width=True)
                
            st.markdown("---")
            st.subheader("Granular Core Audit Ledger Table Data")
            st.dataframe(res_df, use_container_width=True, hide_index=True)
            
            # CSV Download Pipelines
            csv_payload = res_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Computed Enterprise Insight Datasets",
                data=csv_payload,
                file_name="computed_customer_insights.csv",
                mime="text/csv"
            )

    # --- TAB 3: AUTOMATED REMEDIATION ENGINE ---
    with tab_actions:
        if st.session_state.analyzed_data is None:
            st.warning("⚠️ Action generation vector unavailable. No processed pipeline metrics located.")
        else:
            df_act = st.session_state.analyzed_data
            negative_elements = df_act[df_act['Sentiment_Score'] < 0.0]
            
            st.subheader("🎯 Real-Time Dynamically Extracted Mitigation Strategies")
            st.caption("Strategies are dynamically derived by analyzing critical operational performance vulnerabilities.")
            
            if negative_elements.empty:
                st.success("✅ Operational thresholds within nominal parameters. No systemic risk flags detected.")
            else:
                # Find worst performing dimension
                worst_dim = negative_elements.groupby('SERVQUAL_Dimension')['CSAT_Proxy'].mean().idxmin()
                worst_score = negative_elements.groupby('SERVQUAL_Dimension')['CSAT_Proxy'].mean().min()
                
                st.markdown(f"#### Primary Operational Risk Factor Focus: **{worst_dim}** (CSAT Subset Baseline: `{worst_score:.2f}`)")
                
                # Dynamic action recommendations matrix mapping
                remediation_vault = {
                    "Reliability": {
                        "vulnerability": "Repeated codebase script crashes, operational error returns, or critical software data flow blockages.",
                        "script": ["Deploy automated unit testing arrays targeting recent data transformation logic updates.", "Increase API pipeline failure exceptions handling inside core server nodes."]
                    },
                    "Responsiveness": {
                        "vulnerability": "Noticeable latency delays, queuing process lockups, or customer service response queue breaches.",
                        "script": ["Scale horizontal computing worker loops to lower dataset parsing bottlenecks.", "Enforce immediate tier-2 automated alerts for any user ticket tracking unaddressed beyond 45 minutes."]
                    },
                    "Empathy": {
                        "vulnerability": "Negative user interactions regarding interpersonal communication quality or inadequate manual ticket resolution workflows.",
                        "script": ["Incorporate real-time sentiment loops directly inside target team dashboard displays.", "Reroute negatively flagged customer logs to custom support task priority vectors immediately."]
                    },
                    "Tangibles": {
                        "vulnerability": "UI layout defects, font sizing mismatches, or system display scaling issues across screen profiles.",
                        "script": ["Initiate an end-to-end user experience styling audit to eliminate configuration layout errors.", "Enforce robust responsive viewport regression checks before future codebase production releases."]
                    },
                    "Assurance": {
                        "vulnerability": "User concerns regarding data leaks, workspace token management, or security validation confidence rules.",
                        "script": ["Publish secure audit reports regarding recent environment network encryption upgrades.", "Enforce mandatory multi-factor validation rules across enterprise-level permission accounts."]
                    },
                    "General": {
                        "vulnerability": "Ambiguous negative feedback patterns requiring generalized platform attention.",
                        "script": ["Deploy feedback survey forms to isolate exact user friction vectors.", "Run manual audit sweeps over recent processing log exceptions files."]
                    }
                }
                
                target_strategy = remediation_vault.get(worst_dim, remediation_vault["General"])
                
                with st.container(border=True):
                    c_left, c_right = st.columns(2)
                    with c_left:
                        st.error("🚨 **Identified Vulnerability Layer**")
                        st.write(target_strategy["vulnerability"])
                        
                    with c_right:
                        st.success("⚙️ **Dynamic Remediation Playbook**")
                        for item in target_strategy["script"]:
                            st.write(f"- {item}")
                            
                # Show explicit negative quotes contributing to this problem vector
                with st.expander("🔍 View Raw Negative Quotes Driving This Risk Flag", expanded=False):
                    relevant_quotes = negative_elements[negative_elements['SERVQUAL_Dimension'] == worst_dim]
                    for idx, row in relevant_quotes.iterrows():
                        st.info(f"\"*{row[st.session_state.text_column_ref]}*\" (CSAT Proxy: {row['CSAT_Proxy']})")

    # --- TAB 4: MATHEMATICAL BLUEPRINT ---
    with tab_docs:
        st.subheader("Academic Formulation & Lexical Mapping Blueprint")
        st.markdown(
            "This application uses a fully auditable analytical framework to remove human subjective bias from enterprise customer satisfaction tracking."
        )
        
        with st.container(border=True):
            st.markdown(
                """
                ### Core Mathematical Projections
                
                Raw feedback context structures are processed through localized token arrays to determine total polarity. Sentiment tracking maps raw token patterns into a bounded space of $[-1.0, +1.0]$.
                
                To standardize metrics for traditional management dashboards, this value is linearly projected onto standard corporate tracking scales via an explicit conversion equation:
                
                $$\\text{CSAT Proxy Score} = \\left( \\frac{\\text{Sentiment Polarity Index} + 1.0}{2.0} \\right) \\times 4.0 + 1.0$$
                
                This guarantees a strict, auditable linear correlation:
                * A maximum polarity vector of $+1.0$ converts to a perfect corporate rating score of $5.0$.
                * A completely neutral response of $0.0$ returns a mid-scale rating score of $3.0$.
                * A completely negative polarity vector of $-1.0$ converts to a critical risk rating score of $1.0$.
                
                ### The SERVQUAL Framework Dimensions
                1. **Tangibles:** Digital visual interfaces, frontend architecture, layout structure stability, and system styling elements.
                2. **Reliability:** Platform functionality, data pipelines accuracy, software performance correctness, and runtime operational execution stability.
                3. **Responsiveness:** Speed of communication loops, software execution latency, resolution velocities, and support pipeline accessibility.
                4. **Assurance:** Trust safety standards, data management privacy infrastructure, access token management, and compliance rules.
                5. **Empathy:** Individual human attention delivery metrics, specialized messaging handling, and client care focus patterns.
                """
            )

else:
    st.error("🔒 Workspace Authentication Barrier Active")
    st.info("Please confirm credential settings or enable Demo Mode inside the sidebar control center panel.")
