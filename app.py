import streamlit as st
from datetime import datetime
from utils import (
    get_players_for_date,
    METRICS_BY_SPORT,
    evaluate_projection
)
from supabase_client import (
    get_projections,
    add_projection,
    remove_projection,
    update_projection_result
)
import pandas as pd

st.set_page_config(page_title="Bet Tracker App", layout="centered")
st.title("📊 Bet Tracker App")

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()
if "projections" not in st.session_state:
    st.session_state.projections = []

sport = st.selectbox("Select Sport", ["MLB", "NBA"])
selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

players = get_players_for_date(sport, selected_date.isoformat())
selected_player = st.selectbox("Select Player", players if players else ["No players found"])

metric = st.selectbox("Select Metric", METRICS_BY_SPORT[sport])
target = st.number_input("Set Target", min_value=0)

if st.button("Add to Tracker"):
    projection = {
        "player": selected_player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.isoformat(),
        "sport": sport,
        "user_id": "guest"
    }
    add_projection(projection)
    st.success("Projection added!")

projections = get_projections("guest")
df = pd.DataFrame(projections.data if projections else [])

if st.button("Evaluate All"):
    for i, row in df.iterrows():
        if row["actual"] is None:
            actual, met = evaluate_projection(row)
            update_projection_result(row["id"], actual, met)
    st.rerun()  # updated from st.experimental_rerun

if not df.empty:
    st.subheader("📋 Your Tracker Table")
    for idx, row in df.iterrows():
        col1, col2 = st.columns([5, 1])
        with col1:
            result_icon = "✅" if row["met"] else "❌" if row["met"] is False else ""
            st.write(
                f"{row['date']} | {row['player']} | {row['metric']} | Target: {row['target']} | Actual: {row['actual']} {result_icon}"
            )
        with col2:
            if st.button("❌ Remove", key=f"rm_{row['id']}"):
                remove_projection("guest", row["id"])
                st.rerun()  # updated from st.experimental_rerun
