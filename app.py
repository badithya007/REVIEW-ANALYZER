import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Product Review Analyzer", 
    page_icon="📊", 
    layout="wide"
)

# 2. App Branding / Header
st.title("📊 Customer Review Sentiment Analyzer")
st.subheader("Upload your product review spreadsheet to extract qualitative insights")
st.markdown("---")

# 3. Sidebar File Upload Control
uploaded_file = st.sidebar.file_uploader(
    "Upload your Excel (.xlsx) file", 
    type=["xlsx"]
)

# 4. Main Application Logic
if uploaded_file is not None:
    try:
        # Load the workbook structure to inspect sheet names safely
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        # Look for the target sheet dynamically (case-insensitive match)
        target_sheet = None
        for sheet in sheet_names:
            if "customer" in sheet.lower() or "review" in sheet.lower():
                target_sheet = sheet
                break
        
        # Fallback to the first sheet if a specific name isn't found
        if not target_sheet:
            target_sheet = sheet_names[0]

        # Read the Excel data 
        # skiprows=3 bypasses decorative titles and positions the header correctly
        working_df = pd.read_excel(
            uploaded_file, 
            sheet_name=target_sheet, 
            skiprows=3
        )
        
        # Clean up empty rows or padding columns if they exist
        working_df = working_df.dropna(how="all")
        
        st.success(f"Successfully loaded sheet: **'{target_sheet}'**")
        
        # 5. Dynamic Column Mapping (Prevents crashes if headers differ slightly)
        col_mapping = {
            "Customer Name": [c for c in working_df.columns if "name" in c.lower()],
            "Rating (1-5)": [c for c in working_df.columns if "rating" in c.lower() or "star" in c.lower()],
            "Review Title": [c for c in working_df.columns if "title" in c.lower() or "headline" in c.lower()],
            "Review Feedback": [c for c in working_df.columns if "comment" in c.lower() or "feedback" in c.lower() or "written" in c.lower() or "text" in c.lower()]
        }
        
        # Resolve names or fall back to native columns
        rating_col = col_mapping["Rating (1-5)"][0] if col_mapping["Rating (1-5)"] else None
        
        # Build display table structure dynamically based on what was matched
        final_display_cols = []
        for canonical_name, matched_list in col_mapping.items():
            if matched_list:
                # Rename the column visually for clean layout presentation
                working_df = working_df.rename(columns={matched_list[0]: canonical_name})
                final_display_cols.append(canonical_name)
        
        # 6. Executive Metrics Ribbon
        if "Rating (1-5)" in working_df.columns:
            total_reviews = len(working_df)
            avg_rating = working_df["Rating (1-5)"].dropna().mean()
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric(label="Total Reviews Analyzed", value=total_reviews)
            m_col2.metric(label="Average Star Rating", value=f"{avg_rating:.1f} / 5.0")
        
        st.write("---")
        st.subheader("🔍 Mixed Critique Explorer")
        st.caption("Displaying targeted entries containing constructive sentiments ('I loved it, but...')")
        
        # 7. Sentiment Filtering Core Engine
        if "Rating (1-5)" in working_df.columns:
            # Filter for reviews that reflect mixed sentiments (2, 3, or 4 stars)
            mixed_reviews = working_df[working_df["Rating (1-5)"].isin([2, 3, 4])]
            
            if not mixed_reviews.empty:
                st.dataframe(
                    mixed_reviews[final_display_cols], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No mixed reviews (2, 3, or 4 stars) found in this dataset.")
        else:
            # Fallback layout if parsing rating scales failed
            st.warning("Could not establish rating column metrics. Displaying raw records instead:")
            st.dataframe(working_df, use_container_width=True)

    except ImportError as e:
        # Handles missing openpyxl engine dependency gracefully on Streamlit Cloud
        st.error("🚨 **System Dependency Missing**")
        st.markdown(
            """
            The server framework needs the **`openpyxl`** package installed to decode modern `.xlsx` sheets.
            
            ### 🛠️ Immediate Resolution Steps:
            1. Create a file in your GitHub root folder named exactly **`requirements.txt`**.
            2. Paste these three configurations into it:
               ```text
               streamlit
               pandas
               openpyxl
               ```
            3. Push the changes. (If deployment stalls, click **Manage App** -> **Reboot App** in Streamlit Cloud).
            """
        )
    except Exception as e:
        st.error(f"An unexpected operational error occurred while reading the layout: {e}")

else:
    st.info("💡 App Idle: Please upload your generated Excel spreadsheet template using the sidebar to begin analysis.")
