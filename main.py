import streamlit as st
import datetime

from nba_api import fetch_nba_players_by_game, fetch_nba_player_statistics
from mlb_data import get_mlb_players, get_mlb_player_stat, MLB_METRICS
from supabase_client import insert_projection, fetch_projections, clear_projections, update_projection
from cache import get_cached_players, update_cache
from utils import calculate_nba_metric

SPORTS = ["NBA", "MLB"]
NBA_METRICS = ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]

def main():
    st.title("📊 Bet Tracker App")

    date = st.date_input("Select Game Date", datetime.date.today())
    sport = st.selectbox("Select Sport", SPORTS)

    if sport == "NBA":
        cache = get_cached_players(str(date))
        if cache:
            players = cache
        else:
            try:
                players = fetch_nba_players_by_game(str(date))
                update_cache(str(date), players)
            except Exception as e:
                st.error(f"Error fetching NBA players: {e}")
                players = {}
        player_names = list(players.values())
        player_dict = {v: k for k, v in players.items()}
        selected_player = st.selectbox("Select Player", player_names)
        metric = st.selectbox("Select Metric", NBA_METRICS)
    
    else:
        players = get_mlb_players()
        selected_player = st.selectbox("Select Player", players)
        metric = st.selectbox("Select Metric", MLB_METRICS)

    projection = st.number_input("Set Target Projection", min_value=0.0, step=0.5)

    if st.button("Add to Tracker Table"):
        record = {
            "date": str(date),
            "sport": sport,
            "player": selected_player,
            "metric": metric,
            "projection": projection,
            "actual": None,
            "hit": None
        }
        insert_projection(record)
        st.success("Projection added.")

    st.header("📈 Tracker Table")
    data = fetch_projections()

    if st.button("Run Evaluation"):
        for row in data:
            if row["actual"] is not None:
                continue
            if row["sport"] == "NBA":
                game_date = row["date"]
                try:
                    games = fetch_nba_players_by_game(game_date)
                    game_id = list(games.keys())[0]
                    player_id = player_dict[row["player"]]
                    stats = fetch_nba_player_statistics(game_id, player_id)
                    actual = calculate_nba_metric(stats, row["metric"])
                except:
                    actual = 0
            else:
                actual = get_mlb_player_stat(row["player"], row["metric"])
            hit = actual >= row["projection"]
            update_projection(row["id"], actual, hit)
        data = fetch_projections()
        st.success("Evaluation complete.")

    st.table(data)

    if st.button("Reset Table"):
        clear_projections()
        st.success("All data cleared.")

if __name__ == '__main__':
    main()