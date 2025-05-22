import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📞 Scholarship Duplicate Checker – Phone Number Based")

st.markdown("Upload two Excel files to find and compare students **only by mobile number**. Shows full details from both files side-by-side.")

file1 = st.file_uploader("Upload First Excel File (e.g., Database)", type=["xlsx"], key="file1")
file2 = st.file_uploader("Upload Second Excel File (e.g., Client)", type=["xlsx"], key="file2")

if file1 and file2:
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1.columns = df1.columns.str.strip().str.lower()
        df2.columns = df2.columns.str.strip().str.lower()

        mobile_cols_1 = [col for col in df1.columns if 'mobile' in col or 'phone' in col]
        mobile_cols_2 = [col for col in df2.columns if 'mobile' in col or 'phone' in col]

        if not mobile_cols_1 or not mobile_cols_2:
            st.error("❌ Could not detect mobile number columns in one or both files.")
        else:
            col1_mobile = st.selectbox("Select Mobile Column from First File", mobile_cols_1)
            col2_mobile = st.selectbox("Select Mobile Column from Second File", mobile_cols_2)

            df1['match_key'] = df1[col1_mobile].astype(str).str.replace(r'\D', '', regex=True).str[-10:]
            df2['match_key'] = df2[col2_mobile].astype(str).str.replace(r'\D', '', regex=True).str[-10:]

            merged = pd.merge(
                df1,
                df2,
                how='inner',
                on='match_key',
                suffixes=('_file1', '_file2')
            )

            if merged.empty:
                st.info("✅ No matching students found.")
            else:
                st.success(f"🔍 Found {len(merged)} matching students.")

                display_df = merged.drop(columns=['match_key'])
                st.dataframe(display_df)

                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    display_df.to_excel(writer, index=False, sheet_name="PhoneMatches")
                st.download_button("📥 Download Matches", data=buffer.getvalue(), file_name="phone_matches.xlsx")

    except Exception as e:
        st.error(f"An error occurred while processing the files: {e}")
