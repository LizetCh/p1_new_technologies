"""
Restaurant Analytics Dashboard.

This Streamlit app displays a simple dashboard using data from the
analytics schema for restaurants.
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
    page_icon="🍽️",
    layout="wide"
)

# ============================================================
# Database connection
# ============================================================

engine = get_engine()

# ============================================================
# Data loading
# ============================================================

@st.cache_data(ttl=600)
def load_restaurant_summary() -> pd.DataFrame:
    query = """
        SELECT 
            cuisine,
            city,
            AVG(rating) AS avg_rating,
            COUNT(*) AS total_restaurants
        FROM analytics.vw_restaurants_summary
        GROUP BY cuisine, city
        ORDER BY total_restaurants DESC;
    """
    logger.info("Loading data from analytics.vw_restaurants_summary")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

# ============================================================
# Dashboard layout
# ============================================================

st.title("Restaurant Analytics Dashboard")
st.caption("Dashboard interactivo para el análisis de restaurantes impulsado por PostgreSQL y Streamlit.")

restaurant_summary_df = load_restaurant_summary()

if restaurant_summary_df.empty:
    st.warning("No hay datos disponibles. Ejecuta primero tu pipeline o los scripts de transformación.")
else:
    # Métrica general
    total_rest = restaurant_summary_df["total_restaurants"].sum()
    st.metric(label="Total de Restaurantes Registrados", value=int(total_rest))

    # Gráfico de barras por tipo de cocina y ciudad
    st.subheader("Distribución de Restaurantes por Tipo de Cocina y Ciudad")

    fig = px.bar(
        restaurant_summary_df,
        x="cuisine",
        y="total_restaurants",
        color="city",
        title="Restaurantes por Tipo de Cocina",
        text_auto=True,
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabla de datos
    st.subheader("Detalle de la Información")
    st.dataframe(restaurant_summary_df, use_container_width=True)