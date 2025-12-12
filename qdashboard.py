# optimized_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Advanced Data Quality Dashboard", layout="wide")
st.title("Advanced Data Quality Dashboard")

# ----------------------------
# Multi-File Upload
# ----------------------------
uploaded_files = st.file_uploader("Upload CSV file(s)", type=["csv"], accept_multiple_files=True)
if uploaded_files:
    # Merge multiple CSVs
    dfs = [pd.read_csv(f) for f in uploaded_files]
    df = pd.concat(dfs, ignore_index=True)

    filter_df = df.copy()  # No sidebar filters

    # ----------------------------
    # Numeric Columns: safe min/max
    # ----------------------------
    num_cols = df.select_dtypes(include="number").columns.tolist()
    for col in num_cols:
        # Drop NaNs when computing min/max
        col_min = df[col].dropna().min()
        col_max = df[col].dropna().max()
        # Use float always to avoid int conversion errors
        min_val, max_val = float(col_min), float(col_max)

    # ----------------------------
    # Categorical Columns
    # ----------------------------
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    # ----------------------------
    # KPIs
    # ----------------------------
    total_rows = filter_df.shape[0]
    total_cols = filter_df.shape[1]
    missing_total = filter_df.isnull().sum().sum()
    duplicate_rows = filter_df.duplicated().sum()
    missing_percent = round(missing_total / (total_rows * total_cols) * 100, 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", total_rows)
    col2.metric("Columns", total_cols)
    col3.metric("Missing %", f"{missing_percent}%")
    col4.metric("Duplicate Rows", duplicate_rows)

    # ----------------------------
    # Tabs
    # ----------------------------
    tabs = st.tabs(["Summary", "Charts", "Raw Data", "Export"])

    # --------- Summary Tab ---------
    with tabs[0]:
        st.subheader("Data Summary")
        st.write("Column types:")
        st.dataframe(filter_df.dtypes)
        st.write("Missing values per column:")
        missing_per_col = filter_df.isnull().sum()
        st.dataframe(missing_per_col[missing_per_col > 0])
        st.write("Duplicate rows preview:")
        if duplicate_rows > 0:
            st.dataframe(filter_df[filter_df.duplicated()])

    # --------- Charts Tab ---------
    with tabs[1]:
        st.subheader("Interactive Charts")

        # Numeric charts
        for col in num_cols:
            fig_hist = px.histogram(filter_df, x=col, nbins=20, title=f"Histogram of {col}")
            st.plotly_chart(fig_hist, use_container_width=True)

        # Categorical charts
        for col in cat_cols:
            counts = filter_df[col].value_counts().reset_index()
            counts.columns = [col, "count"]
            fig_bar = px.bar(counts, x=col, y="count", title=f"Distribution of {col}")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --------- Raw Data Tab ---------
    with tabs[2]:
        st.subheader("Raw Data")
        st.dataframe(filter_df)

    # --------- Export Tab ---------
    with tabs[3]:
        st.subheader("Export Data")
        cleaned_csv = filter_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=cleaned_csv,
            file_name='filtered_data.csv',
            mime='text/csv'
        )

else:
    st.info("Upload one or more CSV files to get started.")
