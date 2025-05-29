import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    get_players_for_date,
    evaluate_projection,
    METRICS_BY_SPORT
)
from supabase_client import get_projections, add_projection, remove_projection, update_projection_result

st.set_page_config(page_title="Bet Tracker", layout="wide")

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

st.title("📊 Bet Tracker")

selected_sport = st.selectbox("Select Sport", ["NBA", "MLB"])
selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

players = get_players_for_date(selected_sport, selected_date.isoformat())
selected_player = st.selectbox("Select Player", players)
selected_metric = st.selectbox("Select Metric", METRICS_BY_SPORT[selected_sport])
target = st.number_input("Target", min_value=0, value=1)

if st.button("Add to Tracker"):
    new_projection = {
        "player": selected_player,
        "metric": selected_metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.isoformat(),
        "sport": selected_sport,
        "user_id": "guest"
    }
    add_projection(new_projection)
    st.success(f"{selected_player} added to tracker.")

if st.button("Reset Tracker"):
    projections = get_projections("guest")
    for row in projections.data:
        remove_projection("guest", row["id"])
    st.success("Tracker reset.")

st.subheader("📈 Projections Table")
projections = get_projections("guest")
if projections and projections.data:
    df = pd.DataFrame(projections.data)

    for idx, row in df.iterrows():
        if row["actual"] is None:
            actual, met = evaluate_projection(row)
            df.at[idx, "actual"] = actual
            df.at[idx, "met"] = met
            update_projection_result(row["id"], actual, met)

    def display_status(val):
        return "✅" if val else "❌"

    df["met"] = df["met"].apply(display_status)
    df["remove"] = df["id"].apply(lambda x: f"Remove {x}")

    st.dataframe(df[["date", "sport", "player", "metric", "target", "actual", "met"]])
else:
    st.write("No projections yet.")
