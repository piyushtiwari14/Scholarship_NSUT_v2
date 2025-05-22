import streamlit as st
import pandas as pd
from io import BytesIO

# Simple login function
def login():
    st.sidebar.title("Login - NSUT Administration")
    user_id = st.sidebar.text_input("User ID")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if user_id == "CVPSK" and password == "NSUTdsw@2025":
            st.session_state['logged_in'] = True
        else:
            st.sidebar.error("Invalid ID or Password")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
    st.stop()  # Stop the app here if not logged in

# After login, show the main app content
st.title("🎓 Scholarship Duplicate Checker – NSUT Administration")

st.markdown("""
Welcome to the Scholarship Duplicate Checker.
Please follow instructions below to upload and compare Excel files.

**Column Naming Guidelines:**

- For Name matching: Ensure columns have 'name' in their header, e.g., "Full Name", "Student Name"
- For Phone matching: Ensure columns have 'mobile' or 'phone' in their header, e.g., "Mobile Number", "Phone No"
- You can select which columns to use for matching after uploading files.
""")

option = st.selectbox(
    "Select Comparison Method",
    ("Compare by Name", "Compare by Phone Number", "Compare by Name + Phone Number")
)

file1 = st.file_uploader("Upload First Excel File (e.g., Database)", type=["xlsx"], key="file1")
file2 = st.file_uploader("Upload Second Excel File (e.g., Client)", type=["xlsx"], key="file2")

def preview_file(file, label):
    if file:
        try:
            df = pd.read_excel(file)
            st.write(f"Preview of {label} (first 5 rows):")
            st.dataframe(df.head())
            return df
        except Exception as e:
            st.error(f"Error loading {label}: {e}")
            return None
    return None

if file1 and file2:
    df1 = preview_file(file1, "First File")
    df2 = preview_file(file2, "Second File")

    if df1 is not None and df2 is not None:
        df1.columns = df1.columns.str.strip().str.lower()
        df2.columns = df2.columns.str.strip().str.lower()

        if option == "Compare by Name":
            name_cols_1 = [col for col in df1.columns if 'name' in col]
            name_cols_2 = [col for col in df2.columns if 'name' in col]

            if not name_cols_1 or not name_cols_2:
                st.error("❌ Could not detect a name-like column in one or both files.")
            else:
                col1 = st.selectbox("Select Name Column from First File", name_cols_1)
                col2 = st.selectbox("Select Name Column from Second File", name_cols_2)

                df1['match_key'] = df1[col1].astype(str).str.strip().str.lower()
                df2['match_key'] = df2[col2].astype(str).str.strip().str.lower()

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
                        display_df.to_excel(writer, index=False, sheet_name="SideBySideMatches")
                    st.download_button("📥 Download Side-by-Side Matches", data=buffer.getvalue(), file_name="side_by_side_matches.xlsx")

        elif option == "Compare by Phone Number":
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

        elif option == "Compare by Name + Phone Number":
            name_cols_1 = [col for col in df1.columns if 'name' in col]
            name_cols_2 = [col for col in df2.columns if 'name' in col]
            mobile_cols_1 = [col for col in df1.columns if 'mobile' in col or 'phone' in col]
            mobile_cols_2 = [col for col in df2.columns if 'mobile' in col or 'phone' in col]

            if not name_cols_1 or not name_cols_2 or not mobile_cols_1 or not mobile_cols_2:
                st.error("❌ Could not detect name or mobile number columns in one or both files.")
            else:
                col1_name = st.selectbox("Select Name Column from First File", name_cols_1)
                col2_name = st.selectbox("Select Name Column from Second File", name_cols_2)
                col1_mobile = st.selectbox("Select Mobile Column from First File", mobile_cols_1)
                col2_mobile = st.selectbox("Select Mobile Column from Second File", mobile_cols_2)

                df1['match_key'] = (
                    df1[col1_name].astype(str).str.strip().str.lower() + "__" +
                    df1[col1_mobile].astype(str).str.replace(r'\D', '', regex=True).str[-10:]
                )
                df2['match_key'] = (
                    df2[col2_name].astype(str).str.strip().str.lower() + "__" +
                    df2[col2_mobile].astype(str).str.replace(r'\D', '', regex=True).str[-10:]
                )

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
                        display_df.to_excel(writer, index=False, sheet_name="SideBySideMatches")
                    st.download_button("📥 Download Side-by-Side Matches", data=buffer.getvalue(), file_name="side_by_side_matches.xlsx")
else:
    st.info("Please upload both Excel files to proceed.")
