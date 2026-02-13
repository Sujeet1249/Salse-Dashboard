import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Shopkeeper Sales Analyzer")
st.caption("Upload a CSV to explore sales performance with filters, KPIs, and trends.")

file = st.file_uploader("Upload CSV file", type=["csv"])


@st.cache_data(show_spinner=False)
def load_csv(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> pd.DataFrame:
    return pd.read_csv(uploaded_file)


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [c.strip() for c in frame.columns]
    return frame


if file:
    raw_df = normalize_columns(load_csv(file))

    st.sidebar.header("Column Mapping")
    columns = raw_df.columns.tolist()

    region_col = st.sidebar.selectbox(
        "Region column",
        columns,
        index=columns.index("Region") if "Region" in columns else 0,
    )
    product_col = st.sidebar.selectbox(
        "Product column",
        columns,
        index=columns.index("Product") if "Product" in columns else 0,
    )
    price_col = st.sidebar.selectbox(
        "Price column",
        columns,
        index=columns.index("Price") if "Price" in columns else 0,
    )
    quantity_col = st.sidebar.selectbox(
        "Quantity column",
        columns,
        index=columns.index("Quantity") if "Quantity" in columns else 0,
    )
    date_col = st.sidebar.selectbox("Date column (optional)", ["(none)"] + columns, index=0)

    df = raw_df.rename(
        columns={
            region_col: "Region",
            product_col: "Product",
            price_col: "Price",
            quantity_col: "Quantity",
        }
    )

    df["Price"] = safe_numeric(df["Price"])
    df["Quantity"] = safe_numeric(df["Quantity"])
    df["Revenue"] = df["Price"] * df["Quantity"]

    has_date = date_col != "(none)"
    if has_date:
        df["Date"] = pd.to_datetime(raw_df[date_col], errors="coerce")

    st.sidebar.header("Filters")
    region_values = sorted(df["Region"].dropna().unique())
    product_values = sorted(df["Product"].dropna().unique())

    region_filter = st.sidebar.multiselect("Select Region", region_values, default=region_values)
    product_filter = st.sidebar.multiselect("Select Product", product_values, default=product_values)

    price_min, price_max = df["Price"].min(), df["Price"].max()
    qty_min, qty_max = df["Quantity"].min(), df["Quantity"].max()
    price_min = float(price_min) if pd.notna(price_min) else 0.0
    price_max = float(price_max) if pd.notna(price_max) else 0.0
    qty_min = float(qty_min) if pd.notna(qty_min) else 0.0
    qty_max = float(qty_max) if pd.notna(qty_max) else 0.0

    price_range = st.sidebar.slider("Price range", price_min, price_max, (price_min, price_max))
    qty_range = st.sidebar.slider("Quantity range", qty_min, qty_max, (qty_min, qty_max))

    filtered_df = df[
        df["Region"].isin(region_filter)
        & df["Product"].isin(product_filter)
        & df["Price"].between(price_range[0], price_range[1], inclusive="both")
        & df["Quantity"].between(qty_range[0], qty_range[1], inclusive="both")
    ]

    if has_date:
        date_min = filtered_df["Date"].min()
        date_max = filtered_df["Date"].max()
        if pd.notna(date_min) and pd.notna(date_max):
            date_range = st.sidebar.date_input("Date range", (date_min.date(), date_max.date()))
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])
                filtered_df = filtered_df[
                    (filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)
                ]

    st.subheader("Key Metrics")
    total_revenue = filtered_df["Revenue"].sum()
    total_units = filtered_df["Quantity"].sum()
    avg_price = filtered_df["Price"].mean()
    avg_units = filtered_df["Quantity"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", f"{total_revenue:,.2f}")
    col2.metric("Units Sold", f"{total_units:,.0f}")
    col3.metric("Avg Price", f"{avg_price:,.2f}")
    col4.metric("Avg Units / Row", f"{avg_units:,.2f}")

    st.markdown("---")
    st.subheader("Data Quality")
    missing = filtered_df.isna().sum().rename("Missing")
    st.dataframe(missing.to_frame(), use_container_width=True)

    st.markdown("---")
    st.subheader("Preview")
    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")
    st.subheader("Revenue by Product")
    top_n = st.slider("Top N products", 5, 30, 10)
    prod_rev = (
        filtered_df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(top_n)
    )
    fig_prod = px.bar(prod_rev, x="Product", y="Revenue", title="Top Products by Revenue")
    st.plotly_chart(fig_prod, use_container_width=True)

    st.subheader("Revenue by Region")
    region_rev = (
        filtered_df.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    fig_region = px.bar(region_rev, x="Region", y="Revenue", title="Revenue by Region")
    st.plotly_chart(fig_region, use_container_width=True)

    if has_date:
        st.subheader("Revenue Trend")
        trend_df = (
            filtered_df.dropna(subset=["Date"])
            .assign(Month=lambda x: x["Date"].dt.to_period("M").dt.to_timestamp())
            .groupby("Month", as_index=False)["Revenue"]
            .sum()
        )
        if not trend_df.empty:
            fig_trend = px.line(
                trend_df,
                x="Month",
                y="Revenue",
                title="Monthly Revenue Trend",
                markers=True,
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")
    st.subheader("Download")
    st.download_button(
        "Download filtered data (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales.csv",
        mime="text/csv",
    )
