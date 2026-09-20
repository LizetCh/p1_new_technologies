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
        ORDER BY SUM(is_late)::numeric/(SUM(is_delivered) + SUM(is_late)) DESC
        LIMIT 10;
    """

    logger.info("Loading data from analytics.vw_delivery_performance")

    with engine.connect() as conn:
        return pd.read_sql(query,conn)


# ============================================================
# Dashboard layout
# ============================================================

st.title("Restaurant Analytics Dashboard")
st.caption("Simple analytics dashboard powered by PostgreSQL and Streamlit.")

# ---- 1. Peak Days of the Week by total orders ----
st.subheader("Top Days of the Week by Total Orders")

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
st.subheader("Top 10 Restaurants: Late vs Delivered Orders")

cancelled_delivered_orders_df = load_cancelled_delivered_orders()

if cancelled_delivered_orders_df.empty:
    st.warning("No data available. Run the pipeline first.")
else:
    # stacked bar
    fig = px.bar(
        cancelled_delivered_orders_df,
        y="restaurant_id",
        x=["late", "delivered"],
        title="Top 10 Restaurants: Late vs Delivered Orders",
        orientation="h",
        text_auto=True,
        color_discrete_map={"delivered": "#1f77b4", "late": "#ff7f0e"},
    )

    # Force 100% stacked bar layout (0.0 to 1.0)
    fig.update_layout(
        barmode="stack",
        barnorm="fraction",  # Use 'percent' for 0% - 100% axis scale
        xaxis_title="Proportion",
        yaxis_title="Restaurant ID",
        legend_title_text="Status",
        xaxis_tickformat=".0%"
    )

    fig.update_yaxes(autorange="reversed")  #highest late ratio on top

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(cancelled_delivered_orders_df, use_container_width=True)
