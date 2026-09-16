"""
Philippine Labor Force Dashboard
---------------------------------
Streamlit app that visualizes trends in Labor Force Participation Rate,
Employment Rate, Unemployment Rate, and Underemployment Rate over time,
sourced from PSA OpenStat (Table 1B3ALFS0).

NOTE: Column names below are placeholders based on the typical OpenStat
export structure (Period, Indicator, Value). Once you download your actual
CSV, open it and adjust COLUMN NAMES in the CONFIG section below to match.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# CONFIG — adjust to match your actual CSV columns
# ----------------------------
DATA_PATH = "data/labor_force_data.csv"
PERIOD_COL = "Period"          # e.g. "2023 Q1", "January 2023", or "Year"
INDICATOR_COL = "Indicator"    # e.g. "Employment Rate", "Unemployment Rate"
VALUE_COL = "Value"            # the numeric rate itself

st.set_page_config(
    page_title="PH Labor Force Dashboard",
    page_icon="📊",
    layout="wide",
)

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]  # clean up stray whitespace
    return df

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Couldn't find {DATA_PATH}. Make sure your CSV is placed in the "
        "data/ folder and the filename matches DATA_PATH above."
    )
    st.stop()

# ----------------------------
# SIDEBAR — FILTERS
# ----------------------------
st.sidebar.title("Filters")

if INDICATOR_COL in df.columns:
    all_indicators = sorted(df[INDICATOR_COL].dropna().unique().tolist())
    selected_indicators = st.sidebar.multiselect(
        "Select indicator(s)",
        options=all_indicators,
        default=all_indicators,
    )
else:
    selected_indicators = None
    st.sidebar.info(
        "INDICATOR_COL not found in data — showing all columns as separate lines instead."
    )

# ----------------------------
# MAIN PAGE
# ----------------------------
st.title("📊 Philippine Labor Force Trends")
st.caption("Source: PSA OpenStat — Labor Force Survey (Table 1B3ALFS0)")

st.markdown(
    """
    This dashboard tracks the **Labor Force Participation Rate**,
    **Employment Rate**, **Unemployment Rate**, and **Underemployment Rate**
    in the Philippines over time — viewed through the lens of someone
    entering the job market as a fresh graduate.
    """
)

# ----------------------------
# CHART: Trend over time
# ----------------------------
st.subheader("Trend Over Time")

if selected_indicators is not None:
    filtered = df[df[INDICATOR_COL].isin(selected_indicators)]
    fig = px.line(
        filtered,
        x=PERIOD_COL,
        y=VALUE_COL,
        color=INDICATOR_COL,
        markers=True,
        labels={VALUE_COL: "Rate (%)", PERIOD_COL: "Period"},
    )
else:
    # Fallback: assume wide format (one column per indicator)
    fig = px.line(df, x=df.columns[0], y=df.columns[1:], markers=True)

fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# TABLE: Raw data preview
# ----------------------------
with st.expander("View raw data"):
    st.dataframe(df, use_container_width=True)

# ----------------------------
# KEY STATS (example — adjust once real data is loaded)
# ----------------------------
st.subheader("Snapshot")
col1, col2, col3, col4 = st.columns(4)

if selected_indicators is not None:
    latest_period = df[PERIOD_COL].iloc[-1]
    latest = df[df[PERIOD_COL] == latest_period]
    for i, indicator in enumerate(selected_indicators[:4]):
        row = latest[latest[INDICATOR_COL] == indicator]
        if not row.empty:
            value = row[VALUE_COL].values[0]
            [col1, col2, col3, col4][i].metric(indicator, f"{value:.1f}%")

st.markdown("---")
st.caption(
    "Built as a data analyst portfolio project | "
    "Data: Philippine Statistics Authority (PSA) OpenStat"
)