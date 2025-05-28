import streamlit as st
import pandas as pd
import datetime

from utils import (
    get_players_for_date,
    evaluate_projection,
    METRICS_BY_SPORT
)
from supabase_client import (
    get_projections,
    add_projection,
    remove_projection
)

st.set_page_config(page_title="Player Projection Tracker", layout="wide")
st.title("📊 Player Projection Tracker")

# Session State Defaults
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()
if "projections" not in st.session_state:
    st.session_state.projections = []

# Sidebar Inputs
st.sidebar.header("Add New Projection")
sport = st.sidebar.selectbox("Select Sport", ["NBA", "MLB"])
selected_date = st.sidebar.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

players = get_players_for_date(sport, selected_date)
player_name = st.sidebar.selectbox("Select Player", players)
metric = st.sidebar.selectbox("Select Metric", METRICS_BY_SPORT[sport])
target = st.sidebar.number_input("Set Target", min_value=0, step=1)

if st.sidebar.button("Add to Table"):
    new_row = {
        "player": player_name,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.strftime("%Y-%m-%d"),
        "sport": sport,
        "user_id": "guest"
    }
    add_projection(new_row)
    st.rerun()

# Main Table Output
user_id = "guest"
projections = get_projections(user_id)
if projections and hasattr(projections, "data"):
    df = pd.DataFrame(projections.data)
else:
    df = pd.DataFrame()

if not df.empty:
    for idx, row in df.iterrows():
        if row["actual"] is None:
            actual = evaluate_projection(row)
            df.at[idx, "actual"] = actual
            df.at[idx, "met"] = actual >= row["target"] if actual is not None else None

    df_display = df[["player", "sport", "metric", "target", "actual", "met", "date"]]
    df_display["met"] = df_display["met"].apply(lambda x: "✅" if x else ("❌" if x is False else ""))
    st.dataframe(df_display, use_container_width=True)

    for i, row in df.iterrows():
        if st.button(f"Remove {row['player']} ({row['sport']})", key=f"remove_{i}"):
            remove_projection(row["user_id"], row["id"])
            st.rerun()
else:
    st.info("No projections found for the selected date.")
