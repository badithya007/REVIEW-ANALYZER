import streamlit as st
import pandas as pd

# Set layout configurations
st.set_page_config(
    page_title="Product Review Analyzer", 
    page_icon="📊", 
    layout="wide"
)

st.title("📊 Customer Review Sentiment Analyzer")
st.subheader("Upload your product review spreadsheet to extract qualitative insights")
st.markdown("---")

# Sidebar File Loader
uploaded_file = st.sidebar.file_uploader(
    "Upload your Excel (.xlsx) file", 
    type=["xlsx"]
)

if uploaded_file is not None:
    try:
        # Step 1: Safely load Excel workbook structure
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        # Look for target sheet dynamically (case-insensitive match)
        target_sheet = None
        for sheet in sheet_names:
            if "customer" in sheet.lower() or "review" in sheet.lower():
                target_sheet = sheet
                break
        
        if not target_sheet:
            target_sheet = sheet_names[0]
            
        # Step 2: Read raw data with NO initial row skipping to inspect structure
        raw_df = pd.read_excel(uploaded_file, sheet_name=target_sheet, header=None)
        
        # Step 3: Dynamically locate header row containing data headers
        header_row_idx = 0
        for idx, row in raw_df.iterrows():
            row_str = row.astype(str).str.lower().values
            # Check if this row contains core header indicators
            if any("customer" in s or "rating" in s or "review" in s for s in row_str):
                header_row_idx = idx
                break
                
        # Step 4: Re-read the dataframe cleanly starting from the detected header row
        working_df = pd.read_excel(
            uploaded_file, 
            sheet_name=target_sheet, 
            skiprows=header_row_idx
        )
        
        # Clean out entirely empty buffer rows/columns
        working_df = working_df.dropna(how="all")
        working_df = working_df.loc[:, ~working_df.columns.str.contains('^Unnamed')]
        
        st.success(f"Loaded sheet: **'{target_sheet}'** (Data starts at row {header_row_idx + 1})")
        
        # Step 5: Robust case-insensitive Column Mapping Strategy
        col_mapping = {
            "Customer Name": [c for c in working_df.columns if "name" in c.lower()],
            "Rating (1-5)": [c for c in working_df.columns if "rating" in c.lower() or "star" in c.lower()],
            "Review Title": [c for c in working_df.columns if "title" in c.lower() or "headline" in c.lower()],
            "Review Feedback": [c for c in working_df.columns if "comment" in c.lower() or "feedback" in c.lower() or "written" in c.lower() or "text" in c.lower() and c.lower() != "review title"]
        }
        
        # Remap columns to standardized names if found
        final_display_cols = []
        for canonical_name, matched_list in col_mapping.items():
            if matched_list:
                working_df = working_df.rename(columns={matched_list[0]: canonical_name})
                final_display_cols.append(canonical_name)
                
        # Step 6: Render Dashboard Metrics Ribbon
        if "Rating (1-5)" in working_df.columns:
            # Force numeric evaluation to prevent string type conversion bugs
            working_df["Rating (1-5)"] = pd.to_numeric(working_df["Rating (1-5)"], errors='coerce')
            valid_ratings = working_df["Rating (1-5)"].dropna()
            
            if not valid_ratings.empty:
                total_reviews = len(working_df)
                avg_rating = valid_ratings.mean()
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric(label="Total Reviews Analyzed", value=total_reviews)
                m_col2.metric(label="Average Star Rating", value=f"{avg_rating:.1f} / 5.0")
        
        st.write("---")
        st.subheader("🔍 Mixed Critique Explorer")
        st.caption("Displaying target entries matching mixed/constructive sentiments ('I loved it, but...')")
        
        # Step 7: Filter and Display Data
        if "Rating (1-5)" in working_df.columns and "Review Feedback" in working_df.columns:
            # Look specifically for mixed reviews (2, 3, or 4 stars)
            mixed_reviews = working_df[working_df["Rating (1-5)"].isin([2, 3, 4])]
            
            if not mixed_reviews.empty:
                st.dataframe(
                    mixed_reviews[final_display_cols], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No mixed rating records (2, 3, or 4 stars) found in this file.")
        else:
            # Hard fallback: display raw matching table so the app never goes blank
            st.warning("Could not map columns perfectly. Displaying raw tabular data below:")
            st.dataframe(working_df, use_container_width=True)

    except ImportError as e:
        st.error("🚨 **System Dependency Missing**")
        st.markdown(
            """
            The server framework needs the **`openpyxl`** package installed to decode modern `.xlsx` sheets.
            Make sure your **`requirements.txt`** contains a line reading exactly: `openpyxl`
            """
        )
    except Exception as e:
        st.error(f"🚨 **File Parsing Error:** {e}")
        st.info("Ensure the uploaded file is a valid Excel spreadsheet and contains clear headers.")

else:
    st.info("💡 App Idle: Use the sidebar panel to upload your customer review Excel spreadsheet (.xlsx).")
