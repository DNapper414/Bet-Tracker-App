import streamlit as st
import pandas as pd
from supabase_client import get_projections, add_projection, remove_projection, update_projection_result
from utils import (
    METRICS_BY_SPORT,
    get_players_for_date,
    evaluate_projection
)

st.set_page_config(layout="wide")
st.title("🎯 Player Projection Tracker")

if "selected_date" not in st.session_state:
    st.session_state.selected_date = pd.Timestamp.now().date()

selected_date = st.date_input("Select Game Date", value=pd.to_datetime(st.session_state.selected_date))
st.session_state.selected_date = selected_date  # fixed here

# Select sport
sport = st.selectbox("Select Sport", options=["NBA", "MLB"])

# Load player list
players = get_players_for_date(sport, selected_date.strftime("%Y-%m-%d"))

# Inputs
player = st.selectbox("Select Player", players)
metric = st.selectbox("Select Metric", METRICS_BY_SPORT[sport])
target = st.number_input("Enter Target", min_value=0)

if st.button("Add to Tracker"):
    add_projection({
        "player": player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.strftime("%Y-%m-%d"),
        "sport": sport,
        "user_id": "guest"
    })
    st.success("✅ Added projection")

# View projections
projections = get_projections("guest")
if projections:
    df = pd.DataFrame(projections.data)

    if not df.empty:
        df["Evaluate"] = df.apply(lambda row: evaluate_projection(dict(row)), axis=1)
        df["actual"] = df["Evaluate"].apply(lambda x: x.get("actual"))
        df["met"] = df["Evaluate"].apply(lambda x: x.get("met"))
        df.drop(columns=["Evaluate"], inplace=True)

        # Display
        def icon(met):
            return "✅" if met else "❌"

        df["Result"] = df["met"].apply(icon)

        st.dataframe(df[["player", "metric", "target", "actual", "Result", "sport", "date"]])

        if st.button("Reset Table"):
            for _, row in df.iterrows():
                remove_projection("guest", row["id"])
            st.success("🗑️ Table cleared")
