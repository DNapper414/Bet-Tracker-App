import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_client import get_projections, add_projection, remove_projection, update_projection_result
from utils import (
    fetch_mlb_boxscore,
    evaluate_mlb_player_stat,
    fetch_nba_boxscore,
    evaluate_nba_stat,
    MLB_METRICS,
    NBA_METRICS
)

st.set_page_config(page_title="Bet Tracker", layout="wide")
st.title("📊 Bet Tracker")

# Persist date selection
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().strftime("%Y-%m-%d")

selected_date = st.date_input("Select Game Date", value=pd.to_datetime(st.session_state.selected_date))
st.session_state.selected_date = selected_date.strftime("%Y-%m-%d")

# Sport selection
sport = st.selectbox("Select Sport", ["MLB", "NBA"])

# Load player lists
@st.cache_data
def load_player_pool(sport):
    if sport == "MLB":
        return ["Aaron Judge", "Shohei Ohtani", "Juan Soto", "Ronald Acuña Jr."]
    else:
        return ["LeBron James", "Stephen Curry", "Jayson Tatum", "Nikola Jokic"]

players = load_player_pool(sport)

# UI Inputs
player = st.selectbox("Select Player", players)
metric_list = MLB_METRICS if sport == "MLB" else NBA_METRICS
metric = st.selectbox("Metric", metric_list)
target = st.number_input("Target", min_value=0, step=1)

# Add player button
if st.button("➕ Add to Tracker"):
    new_entry = {
        "player": player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.strftime("%Y-%m-%d"),
        "sport": sport,
        "user_id": "guest"
    }
    add_projection(new_entry)

# Reset all
if st.button("🗑 Reset Table"):
    user_projections = get_projections("guest")
    for row in user_projections.data:
        remove_projection("guest", row["id"])

# Fetch and display results
user_projections = get_projections("guest")
if user_projections.data:
    updated_rows = []
    for proj in user_projections.data:
        if proj["actual"] is None:
            date_str = proj["date"]
            if proj["sport"] == "MLB":
                # Simulate gamePk lookup for example purpose
                sample_game_pk = 777782
                box = fetch_mlb_boxscore(sample_game_pk)
                actual = evaluate_mlb_player_stat(box, proj["player"], proj["metric"]) if box else 0
            else:
                box_scores = fetch_nba_boxscore(date_str)
                actual = 0
                for game in box_scores:
                    for player_stats in game.get("player_stats", []):
                        if player_stats.get("player_name", "").lower() == proj["player"].lower():
                            actual = evaluate_nba_stat(player_stats, proj["metric"])
                            break

            met = actual >= proj["target"]
            update_projection_result(proj["id"], actual, met)

    # Refresh after update
    user_projections = get_projections("guest")

    df = pd.DataFrame(user_projections.data)
    df["Met"] = df["met"].apply(lambda x: "✅" if x else "❌" if x is not None else "⏳")
    df["Remove"] = df["id"].apply(lambda i: f"❌ Remove {i}")

    df_display = df[["player", "metric", "target", "actual", "Met", "Remove"]]
    st.dataframe(df_display, use_container_width=True)

    # Handle remove button
    for i in df["id"]:
        if st.button(f"Remove {i}"):
            remove_projection("guest", i)
            st.experimental_rerun()
else:
    st.info("No projections added yet.")
