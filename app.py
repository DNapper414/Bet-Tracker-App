import os
import pandas as pd
import streamlit as st
from datetime import datetime
from utils import (
    get_mlb_players_for_date,
    get_nba_players_for_date,
    evaluate_projections_mlb_statsapi,
    evaluate_projections_nba_nbaapi,
)
from supabase_client import get_projections, add_projection, remove_projection

st.set_page_config(page_title="📊 Bet Tracker", layout="wide")

SPORTS = ["MLB", "NBA"]

METRICS = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"],
}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

st.title("📊 Bet Tracker")

selected_sport = st.selectbox("Choose a Sport", SPORTS)
selected_date = st.date_input("Select Game Date", value=pd.to_datetime(st.session_state.selected_date))
st.session_state.selected_date = selected_date

players = (
    get_mlb_players_for_date(selected_date) if selected_sport == "MLB"
    else get_nba_players_for_date(selected_date)
)
player_name = st.selectbox("Select Player", players)
metric = st.selectbox("Select Metric", METRICS[selected_sport])
target = st.number_input("Set Target", min_value=0)

if st.button("➕ Add to Tracker"):
    if player_name not in players:
        st.error(f"🚫 {player_name} did not play on {selected_date}")
    else:
        add_projection({
            "player": player_name,
            "metric": metric,
            "target": target,
            "actual": None,
            "met": None,
            "date": selected_date.isoformat(),
            "sport": selected_sport,
            "user_id": "guest"
        })
        st.success("✅ Projection added.")

if st.button("🧹 Reset All (Danger)"):
    st.warning("⚠️ This feature is disabled in demo for safety.")

projections = get_projections("guest")
projections_data = projections.data if hasattr(projections, "data") else []

if projections_data:
    df = pd.DataFrame(projections_data).sort_values(by="date", ascending=False)

    df_mlb = df[df["sport"] == "MLB"]
    df_nba = df[df["sport"] == "NBA"]

    df_eval_mlb = evaluate_projections_mlb_statsapi(df_mlb) if not df_mlb.empty else pd.DataFrame()
    df_eval_nba = evaluate_projections_nba_nbaapi(df_nba) if not df_nba.empty else pd.DataFrame()

    combined = pd.concat([df_eval_mlb, df_eval_nba])

    def status_icon(met):
        if met is None:
            return ""
        return "✅" if met else "❌"

    combined["Status"] = combined["met"].apply(status_icon)

    st.dataframe(combined[[
        "date", "sport", "player", "metric", "target", "actual", "Status"
    ]], use_container_width=True)
else:
    st.info("No projections to show yet.")
