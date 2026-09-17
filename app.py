"""
Food App Analytics Dashboard.

This Streamlit app displays a simple dashboard using data from the
analytics schema.

For this first version, the app uses one analytics view:

    analytics.vw_customer signups by month
    analytics.vw_load_bills_by_payment_status
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
    page_title="Food App Analytics Dashboard",
    page_icon="🦃",
    layout="wide"
)




# ============================================================
# Database connection
# ============================================================

engine = get_engine()

# ============================================================
# Data loading
# ============================================================

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

st.title("Food App Analytics Dashboard")
st.caption("Simple analytics dashboard powered by PostgreSQL and Streamlit.")

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

#___Customer signups by month__
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