import streamlit as st
import pandas as pd
import requests
import uuid
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

st.set_page_config(page_title="Bet Tracker by Apprentice Ent. Sports Picks", layout="centered")
st.title("🏀⚾ Bet Tracker by Apprentice Ent. Sports Picks")

# ✅ Simple fix: hardcoded user_id
if "user_id" not in st.session_state or not st.session_state.user_id:
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
sport = st.radio("Select Sport for New Projection", ["MLB", "NBA"], index=["MLB", "NBA"].index(st.session_state.last_sport))
st.session_state.last_sport = sport

if "projections" not in st.session_state:
    response = get_projections(user_id)
    st.session_state.projections = response.data if response.data else []
all_projections = st.session_state.projections

filtered = [p for p in all_projections if p.get("date") == date_str]
df = pd.DataFrame(filtered)

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

st.subheader(f"➕ Add {sport} Player Projection")

try:
    with st.spinner("Fetching player list..."):
        player_list = get_nba_players_today(date_str) if sport == "NBA" else get_mlb_players_today(date_str)
except Exception as e:
    st.warning("⚠️ Could not fetch player list. Please enter manually.")
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
    st.info("⏳ Adding projection...")
    try:
        response = add_projection(new_proj)
        if response.data:
            st.session_state.projections.append(response.data[0])
            st.success("✅ Added!")
        else:
            st.warning("⚠️ No data returned from Supabase.")
    except Exception as e:
        st.error(f"❌ Failed to add projection: {e}")
    st.rerun()

st.subheader("📊 Results")

if df.empty:
    st.info("No projections added for this date.")
else:
    if st.button("🧹 Clear All Projections"):
        for row in df.itertuples():
            remove_projection(user_id, row.id)
        st.session_state.projections = [p for p in st.session_state.projections if p["date"] != date_str]
        st.rerun()

    need_eval = df[df["Actual"].isnull()]
    if not need_eval.empty:
        sports_in_data = df["Sport"].unique()
        fresh_results = []

        if "MLB" in sports_in_data:
            schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
            resp = requests.get(schedule_url).json()
            game_ids = [
                str(game["gamePk"])
                for d in resp.get("dates", [])
                for game in d.get("games", [])
                if game.get("status", {}).get("abstractGameState") in ["Final", "Live", "In Progress"]
            ]
            boxscores = [fetch_boxscore(gid) for gid in game_ids if fetch_boxscore(gid)]
            mlb_results = evaluate_projections(df[df["Sport"] == "MLB"], boxscores)
            for r in mlb_results:
                r["Sport"] = "MLB"
            fresh_results += mlb_results

        if "NBA" in sports_in_data:
            nba_results = evaluate_projections_nba_nbaapi(df[df["Sport"] == "NBA"], date_str)
            for r in nba_results:
                r["Sport"] = "NBA"
            fresh_results += nba_results

        for eval_row in fresh_results:
            match = next(
                (p for p in st.session_state.projections if
                 p["player"] == eval_row["Player"] and
                 p["metric"] == eval_row["Metric"] and
                 str(p["target"]) == str(eval_row["Target"]) and
                 p["sport"] == eval_row["Sport"] and
                 p["date"] == date_str),
                None
            )
            if match:
                update_projection_result(match["id"], eval_row["Actual"], eval_row["✅ Met?"])
        st.rerun()

    st.markdown("""
    <style>
    div[data-testid="column"] {
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    col_config = [1.5, 2, 2, 1.5, 1.5, 1.5, 1]
    header = st.columns(col_config)
    for col, title in zip(header, ["Sport", "Player", "Metric", "Target", "Actual", "✅ Met?", ""]):
        col.markdown(f"**{title}**")

    for _, row in df.iterrows():
        cols = st.columns(col_config)
        cols[0].markdown(row["Sport"])
        cols[1].markdown(row["Player"])
        cols[2].markdown(row["Metric"])
        cols[3].markdown(str(row["Target"]))
        cols[4].markdown(str(row["Actual"]) if row["Actual"] is not None else "N/A")
        cols[5].markdown("✅" if row["✅ Met?"] else "❌")
        if cols[6].button("❌", key=f"remove_{row['id']}"):
            remove_projection(user_id, row["id"])
            st.session_state.projections = [p for p in st.session_state.projections if p["id"] != row["id"]]
            st.rerun()

    csv_df = df[["Sport", "Player", "Metric", "Target", "Actual", "✅ Met?"]]
    csv = csv_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results CSV", csv, file_name="bet_results.csv")