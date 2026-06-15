import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Product Review Analyzer", page_icon="📊", layout="wide")

st.title("📊 Customer Review Sentiment Analyzer")
st.subheader("Python 3.14 Stabilized Build Engine")
st.markdown("---")

# Sidebar
uploaded_file = st.sidebar.file_uploader("Upload your Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # PYLX ENGINE FALLBACK BYPASS: We route directly through the Rust 'calamine' compiler
        # This completely fixes the 'ImportError' from openpyxl on experimental python builds
        excel_file = pd.ExcelFile(uploaded_file, engine="calamine")
        sheet_names = excel_file.sheet_names
        
        target_sheet = None
        for sheet in sheet_names:
            if "customer" in sheet.lower() or "review" in sheet.lower():
                target_sheet = sheet
                break
        if not target_sheet:
            target_sheet = sheet_names[0]
            
        # Inspect sheet structure dynamically without row skipping
        raw_df = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None, engine="calamine")
        
        header_row_idx = 0
        for idx, row in raw_df.iterrows():
            row_str = row.astype(str).str.lower().values
            if any("customer" in s or "rating" in s or "review" in s for s in row_str):
                header_row_idx = idx
                break
                
        # Parse cleanly using Calamine compilation layer
        working_df = pd.read_excel(
            uploaded_file, 
            sheet_name=target_sheet, 
            skiprows=header_row_idx,
            engine="calamine"
        )
        
        # Strip structural noise rows
        working_df = working_df.dropna(how="all")
        working_df = working_df.loc[:, ~working_df.columns.str.contains('^Unnamed')]
        
        st.success(f"Successfully processed sheet via Calamine Engine!")
        
        # Case-insensitive column identification mapping
        col_mapping = {
            "Customer Name": [c for c in working_df.columns if "name" in c.lower()],
            "Rating (1-5)": [c for c in working_df.columns if "rating" in c.lower() or "star" in c.lower()],
            "Review Title": [c for c in working_df.columns if "title" in c.lower() or "headline" in c.lower()],
            "Review Feedback": [c for c in working_df.columns if "comment" in c.lower() or "feedback" in c.lower() or "written" in c.lower() or "text" in c.lower() and c.lower() != "review title"]
        }
        
        final_display_cols = []
        for canonical_name, matched_list in col_mapping.items():
            if matched_list:
                working_df = working_df.rename(columns={matched_list[0]: canonical_name})
                final_display_cols.append(canonical_name)
                
        # Render Metrics
        if "Rating (1-5)" in working_df.columns:
            working_df["Rating (1-5)"] = pd.to_numeric(working_df["Rating (1-5)"], errors='coerce')
            valid_ratings = working_df["Rating (1-5)"].dropna()
            
            if not valid_ratings.empty:
                st.columns(2)[0].metric(label="Total Reviews Analyzed", value=len(working_df))
                st.columns(2)[1].metric(label="Average Star Rating", value=f"{valid_ratings.mean():.1f} / 5.0")
        
        st.write("---")
        st.subheader("🔍 Mixed Critique Explorer ('I loved it, but...')")
        
        if "Rating (1-5)" in working_df.columns and "Review Feedback" in working_df.columns:
            mixed_reviews = working_df[working_df["Rating (1-5)"].isin([2, 3, 4])]
            if not mixed_reviews.empty:
                st.dataframe(mixed_reviews[final_display_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No mixed reviews (2-4 stars) identified in data arrays.")
        else:
            st.dataframe(working_df, use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Operational Engine Breakdown: {e}")
        st.info("If dependencies just changed, reboot the server via the Streamlit configuration panel.")
else:
    st.info("💡 Drop your review tracker file (.xlsx) into the sidebar block to calculate review trends.")
