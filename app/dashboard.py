"""Streamlit dashboard for USGS earthquake data.

Reads the `earthquakes` table from PostgreSQL and renders an interactive
map, metrics, and charts. Run from the repo root with:

    streamlit run app/dashboard.py
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env by absolute path so CWD never matters (app/ when running under Streamlit)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def database_url() -> str:
    """Build the Postgres connection string from environment variables."""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "scientific_data")
    # +psycopg → SQLAlchemy uses psycopg v3 (its default, psycopg2, is not installed)
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"


QUERY = """
    SELECT event_id, mag, place, time, lat, lon, depth_km, url
    FROM earthquakes
    WHERE mag >= :min_mag
      AND time BETWEEN :start_time AND :end_time
    ORDER BY time DESC
"""


@st.cache_data(ttl=60, show_spinner="Loading earthquakes from Postgres…")
def load_events(min_mag: float, start_time: str, end_time: str) -> pd.DataFrame:
    engine = create_engine(database_url())
    with engine.connect() as conn:
        return pd.read_sql(
            text(QUERY),
            conn,
            params={"min_mag": min_mag, "start_time": start_time, "end_time": end_time},
        )


def main() -> None:
    st.set_page_config(page_title="USGS Earthquakes", page_icon="🌍", layout="wide")
    st.title("🌍 USGS Earthquakes")
    st.caption("USGS FDSN Event API → PostgreSQL → this dashboard")

    with st.sidebar:
        st.header("Filters")
        min_mag = st.slider("Minimum magnitude", 0.0, 9.0, 2.5, 0.1)
        start_date = st.date_input("Start date", value=date.today() - timedelta(days=30))
        end_date = st.date_input("End date", value=date.today())

    if end_date < start_date:
        st.error("End date must be on or after the start date.")
        st.stop()

    start_time = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
    end_time = datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc)

    df = load_events(min_mag, start_time.isoformat(), end_time.isoformat())

    if df.empty:
        st.info("No earthquakes match the current filters. Try a lower magnitude or a wider date range.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Earthquakes", f"{len(df):,}")
    col2.metric("Max magnitude", f"{df['mag'].max():.1f}")
    col3.metric("Average depth (km)", f"{df['depth_km'].mean():.1f}")

    st.subheader("Map")
    st.map(df[["lat", "lon"]])

    st.subheader("Events per day")
    daily = df.set_index("time").resample("D").size()
    st.bar_chart(daily, x_label="Date", y_label="Earthquakes")

    st.subheader("Magnitude distribution")
    buckets = df["mag"].round(0).astype(int)
    st.bar_chart(buckets.value_counts().sort_index(), x_label="Magnitude (rounded)", y_label="Earthquakes")

    st.subheader("Latest events")
    st.dataframe(
        df[["time", "mag", "place", "depth_km", "url"]],
        hide_index=True,
        column_config={
            "time": st.column_config.DatetimeColumn("Time (UTC)", format="YYYY-MM-DD HH:mm"),
            "mag": st.column_config.NumberColumn("Magnitude", format="%.1f"),
            "depth_km": st.column_config.NumberColumn("Depth (km)", format="%.1f"),
            "url": st.column_config.LinkColumn("USGS link"),
        },
    )


if __name__ == "__main__":
    main()