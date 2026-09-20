"""
Restaurant Analytics Dashboard.

This Streamlit app displays a simple dashboard using data from the
analytics schema.

"""

from pathlib import Path
import sys
import logging

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# Import project modules
# ============================================================

# app.py is located at the project root.
# db_connection.py is located inside the src folder.
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

sys.path.append(str(SRC_DIR))

from db_connection import get_engine

# ============================================================
# Logging configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ============================================================
# Streamlit page configuration
# ============================================================

st.set_page_config(
    page_title="Restaurant Analytics Dashboard",
    page_icon="🍛",
    layout="wide"
)

# ============================================================
# Database connection
# ============================================================

engine = get_engine()

# ============================================================
# Data loading
# ============================================================

# --------- 1. Show peak days of the week based on total orders --------
@st.cache_data(ttl=600)
def load_peak_days_of_week() -> pd.DataFrame:

    query = """
        SELECT 
            order_day_of_week,
            COUNT(order_id) AS total_orders
        FROM analytics.vw_delivery_performance
        GROUP BY order_day_of_week 
        ORDER BY total_orders DESC;
    """

    logger.info("Loading data from analytics.vw_delivery_performance")

    with engine.connect() as conn:
        return pd.read_sql(query,conn)


# --------- 2. Show ratio of cancelled-delivered orders per restaurant --------
@st.cache_data(ttl=600)
def load_cancelled_delivered_orders() -> pd.DataFrame:
    query = """
        SELECT 
            restaurant_id,
            SUM(is_delivered) AS delivered,
            SUM(is_late) AS late
        FROM analytics.vw_delivery_performance
        GROUP BY restaurant_id
        HAVING (SUM(is_delivered) + SUM(is_late)) >= 10
        LIMIT 10;
    """

    logger.info("Loading data from analytics.vw_delivery_performance")

    with engine.connect() as conn:
        return pd.read_sql(query,conn)
    
# --------- 3. Customers by city --------
@st.cache_data(ttl=600)
def load_customers_by_city() -> pd.DataFrame:
    query = """
        SELECT 
            city,
            total_customers
        FROM analytics.vw_customers_by_city;
    """
    logger.info("Loading data from analytics.vw_customers_by_city")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

# --------- 4. Customer signups by month --------
@st.cache_data(ttl=600)
def load_customer_signups_by_month() -> pd.DataFrame:
    query = """
        SELECT 
            signup_year,
            signup_month_number,
            signup_month_name,
            total_signups
        FROM analytics.vw_customer_signups_by_month
        ORDER BY signup_year, signup_month_number;
    """
    logger.info("Loading data from analytics.vw_customer_signups_by_month")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# Dashboard layout
# ============================================================

st.title("Restaurant Analytics Dashboard")
st.caption("Simple analytics dashboard powered by PostgreSQL and Streamlit.")

# ---- 1. Peak Days of the Week by total orders ----
st.subheader("Peak Days of the Week by total orders")

peak_days_of_week_df = load_peak_days_of_week()

if peak_days_of_week_df.empty:
    st.warning("No data available.Run the pipeline first.")
else:
    total_orders = peak_days_of_week_df["total_orders"].sum()

    st.metric(
        label="Total orders",
        value=int(total_orders)
    )

    fig = px.bar(
        peak_days_of_week_df,
        x="order_day_of_week",
        y="total_orders",
        text="total_orders",
        title="Peak Days of the Week"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(peak_days_of_week_df, use_container_width=True)


# ------ 2. Delivered and Late Orders per Restaurant ----
st.subheader("Delivered and Late Orders per Restaurant")

cancelled_delivered_orders_df = load_cancelled_delivered_orders()

if cancelled_delivered_orders_df.empty:
    st.warning("No data available. Run the pipeline first.")
else:
    # stacked bar
    fig = px.bar(
    cancelled_delivered_orders_df,
    y="restaurant_id",
    x=["delivered", "late"],
    title="Delivered vs. Late Orders Ratio per Restaurant",
    orientation="h",
    color_discrete_map={"delivered": "#1f77b4", "late": "#ff7f0e"},
    )

    # Force 100% stacked bar layout (0.0 to 1.0)
    fig.update_layout(
        barmode="stack",
        barnorm="fraction",  # Use 'percent' for 0% - 100% axis scale
        xaxis_title="Proportion",
        yaxis_title="Restaurant ID",
        legend_title_text="Status",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(cancelled_delivered_orders_df, use_container_width=True)


# ------ 3. Customer by City ----
st.subheader("Customers by City")

customers_by_city_df = load_customers_by_city()

if customers_by_city_df.empty:
    st.warning("No data available. Run the pipeline first.")

else:
    total_customers = customers_by_city_df["total_customers"].sum()

    st.metric(
        label="Total customers",
        value=int(total_customers)
    )

    fig = px.bar(
        customers_by_city_df,
        x="city",
        y="total_customers",
        text="total_customers",
        title="Customers by city"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(customers_by_city_df, use_container_width=True)

# ------ 4. Customer signups by month ----
st.subheader("Customer Signups by Month")

signups_by_month_df = load_customer_signups_by_month()

if signups_by_month_df.empty:
    st.warning("No data available. Run the pipeline first.")

else:
    signups_by_month_df["month_label"] = (
        signups_by_month_df["signup_month_name"]
        + " "
        + signups_by_month_df["signup_year"].astype(str)
    )

    fig_line = px.line(
        signups_by_month_df,
        x="month_label",
        y="total_signups",
        markers=True,
        title="Customer signups by month"
    )

    fig_line.update_xaxes(
        categoryorder="array",
        categoryarray=signups_by_month_df["month_label"]
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.dataframe(signups_by_month_df, use_container_width=True)
