import os
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import fetch_boxscore, evaluate_projections, get_mlb_players_today
from supabase_client import get_projections, add_projection, update_projection_result, remove_projection
import requests

os.environ["STREAMLIT_SERVER_PORT"] = os.getenv("PORT", "8080")

st.set_page_config(page_title="Bet Tracker", layout="centered")
st.title("📊 Bet Tracker - MLB")

user_id = st.session_state.get("user_id", "guest")

selected_date = st.date_input("📅 Select Game Date", value=datetime.today())
date_str = selected_date.strftime("%Y-%m-%d")

response = get_projections(user_id)
projections = response.data if hasattr(response, "data") else []
projections_today = [p for p in projections if p["date"] == date_str and p["sport"] == "MLB"]

# Add projection
st.subheader("➕ Add New Player Projection")
try:
    players = get_mlb_players_today(date_str)
except:
    players = []
    st.warning("⚠️ Could not fetch MLB players.")

player = st.selectbox("Player", players) if players else st.text_input("Player")
metric = st.selectbox("Metric", ["hits", "homeRuns", "totalBases", "rbi", "baseOnBalls", "runs", "stolenBases"])
target = st.number_input("Target", min_value=0, step=1)

if st.button("Add to Tracker"):
    add_projection({
        "user_id": user_id,
        "sport": "MLB",
        "date": date_str,
        "player": player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None
    })
    st.success("✅ Added!")
    st.rerun()

# Evaluate incomplete
incomplete = [p for p in projections_today if p["actual"] is None]

if incomplete:
    st.info("🔍 Evaluating pending projections...")
    try:
        sched_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
        games = requests.get(sched_url).json().get("dates", [])[0].get("games", [])
        game_ids = [g["gamePk"] for g in games if g["status"]["abstractGameState"] in ["Final", "Live"]]
        boxscores = [b for b in map(fetch_boxscore, game_ids) if b]

        df = pd.DataFrame(incomplete)
        df.columns = df.columns.str.lower()  # ✅ Normalize column names
        results = evaluate_projections(df, boxscores)

        for r in results:
            match = next((p for p in projections_today if p["player"] == r["player"] and p["metric"] == r["metric"]), None)
            if match and r["actual"] is not None:
                update_projection_result(match["id"], r["actual"], r["met"])
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error evaluating stats: {e}")

# Reset all
if projections_today and st.button("🧹 Reset All Projections"):
    for p in projections_today:
        remove_projection(user_id, p["id"])
    st.success("✅ All removed.")
    st.rerun()

# Show table
st.subheader("📋 Projections for " + date_str)

if projections_today:
    for row in projections_today:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(
                f"**{row['player']}** | {row['metric']} | 🎯 {row['target']} | 📊 {row.get('actual', '—')} | ✅ {row.get('met', '—')}")
        with col2:
            if st.button("❌ Remove", key=f"remove_{row['id']}"):
                remove_projection(user_id, row["id"])
                st.rerun()
else:
    st.info("No projections for this date.")
