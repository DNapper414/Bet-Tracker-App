import os
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from utils import (
    fetch_boxscore,
    evaluate_projections,
    evaluate_projections_nba_nbaapi,
    get_nba_players_today,
    get_mlb_players_today
)
from supabase_client import (
    get_projections,
    add_projection,
    remove_projection,
    update_projection_result
)

# Force correct port for Railway
os.environ["STREAMLIT_SERVER_PORT"] = os.getenv("PORT", "8080")

st.set_page_config(page_title="Bet Tracker", layout="centered")
st.title("🏀⚾ Bet Tracker by Apprentice Ent. Sports Picks")

# Session state defaults
if "user_id" not in st.session_state:
    st.session_state.user_id = "guest"
user_id = st.session_state.user_id

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().strftime("%Y-%m-%d")
selected_date = datetime.strptime(st.session_state.selected_date, "%Y-%m-%d")
game_date = st.date_input("📅 Choose Game Date", value=selected_date)
st.session_state.selected_date = game_date.strftime("%Y-%m-%d")
date_str = st.session_state.selected_date

if "last_sport" not in st.session_state:
    st.session_state.last_sport = "MLB"
sport = st.radio("Select Sport", ["MLB", "NBA"], index=["MLB", "NBA"].index(st.session_state.last_sport))
st.session_state.last_sport = sport

# Load projections from Supabase
if "projections" not in st.session_state:
    response = get_projections(user_id)
    st.write("🧩 Supabase response:", response)
    st.session_state.projections = response.data if hasattr(response, "data") else []

all_projections = st.session_state.projections
filtered = [p for p in all_projections if p.get("date") == date_str]
st.write("🔍 Filtered Projections:", filtered)

df = pd.DataFrame(filtered)
st.write("📊 DataFrame before evaluation:", df)

if not df.empty:
    df.rename(columns={
        "sport": "Sport",
        "player": "Player",
        "metric": "Metric",
        "target": "Target",
        "actual": "Actual",
        "met": "✅ Met?",
        "id": "id"
    }, inplace=True)

# Input new projection
st.subheader(f"➕ Add {sport} Player Projection")

try:
    with st.spinner("Fetching players..."):
        player_list = get_nba_players_today(date_str) if sport == "NBA" else get_mlb_players_today(date_str)
except Exception as e:
    st.warning("⚠️ Could not fetch player list.")
    player_list = []
    st.text(f"Error: {e}")

player = st.selectbox("Player Name", player_list) if player_list else st.text_input("Player Name")
metric = st.selectbox("Metric", {
    "MLB": ["hits", "homeRuns", "totalBases", "rbi", "baseOnBalls", "runs", "stolenBases"],
    "NBA": ["points", "assists", "rebounds", "steals", "blocks", "3pts made", "PRA"]
}[sport])
target = st.number_input("Target", value=1)

if st.button("➕ Add to Table"):
    new_proj = {
        "user_id": user_id,
        "sport": sport,
        "date": date_str,
        "player": player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None
    }
    st.info("⏳ Adding...")
    try:
        response = add_projection(new_proj)
        st.write("📦 Added:", response.data)
        if response.data:
            st.session_state.projections.append(response.data[0])
            st.success("✅ Added!")
        else:
            st.warning("⚠️ No data returned.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
    st.rerun()

# Run evaluation if actuals are missing
need_eval = df[df["Actual"].isnull()]

if not need_eval.empty and sport == "MLB":
    st.info("🔍 Evaluating missing MLB stats...")
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"

    try:
        resp = requests.get(schedule_url).json()
        game_ids = [
            g["gamePk"]
            for d in resp.get("dates", [])
            for g in d.get("games", [])
            if g.get("status", {}).get("abstractGameState") in ["Final", "Live"]
        ]
        st.write("🎯 Game IDs:", game_ids)

        boxscores = [fetch_boxscore(gid) for gid in game_ids]
        boxscores = [b for b in boxscores if b]
        st.write("📦 Loaded Boxscores:", len(boxscores))

        results = evaluate_projections(df, boxscores)

        for r in results:
            if r["Actual"] is not None:
                match = next((p for p in all_projections if p["player"] == r["Player"] and p["metric"] == r["Metric"]), None)
                if match:
                    update_projection_result(match["id"], r["Actual"], r["✅ Met?"])

        st.success("✅ Evaluation complete.")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Evaluation failed: {e}")
