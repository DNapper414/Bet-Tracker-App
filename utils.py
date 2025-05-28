import os
import statsapi
import requests
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.static import players
from supabase import create_client
from datetime import datetime
import streamlit as st

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Metrics definition
METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

def get_players_for_date(sport, date_obj):
    date_str = date_obj.strftime("%Y-%m-%d")
    if sport == "MLB":
        game_ids = statsapi.schedule(date=date_str)
        names = set()
        for game in game_ids:
            names.add(game['home_name'])
            names.add(game['away_name'])
        return sorted(list(names))
    elif sport == "NBA":
        nba_players = players.get_active_players()
        return sorted([p['full_name'] for p in nba_players])
    return []

def evaluate_projection(proj):
    if proj["sport"] == "MLB":
        return evaluate_projection_mlb(proj)
    elif proj["sport"] == "NBA":
        return evaluate_projection_nba(proj)
    return 0, False

def evaluate_projection_mlb(proj):
    games = statsapi.schedule(date=proj["date"])
    player_stats = statsapi.player_stat_data(statsapi.lookup_player(proj["player"])[0]['id'], game=games[0]['game_id'])
    actual = 0
    if proj["metric"] == "hits":
        actual = player_stats['stats']['h']
    elif proj["metric"] == "homeruns":
        actual = player_stats['stats']['hr']
    elif proj["metric"] == "RBI":
        actual = player_stats['stats']['rbi']
    elif proj["metric"] == "runs":
        actual = player_stats['stats']['r']
    elif proj["metric"] == "Total Bases":
        actual = player_stats['stats']['tb']
    elif proj["metric"] == "stolen bases":
        actual = player_stats['stats']['sb']
    return actual, actual >= proj["target"]

def evaluate_projection_nba(proj):
    player_list = players.find_players_by_full_name(proj["player"])
    if not player_list:
        return 0, False

    player_id = player_list[0]['id']
    today = datetime.strptime(proj["date"], "%Y-%m-%d")
    season = f"{today.year-1}-{str(today.year)[-2:]}"
    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(player_id=player_id, game_date=proj["date"], season=season)

    stats = boxscore.get_data_frames()[0]
    if stats.empty:
        return 0, False

    row = stats.iloc[0]
    if proj["metric"] == "points":
        actual = row["PTS"]
    elif proj["metric"] == "rebounds":
        actual = row["REB"]
    elif proj["metric"] == "assist":
        actual = row["AST"]
    elif proj["metric"] == "PRA":
        actual = row["PTS"] + row["REB"] + row["AST"]
    elif proj["metric"] == "blocks":
        actual = row["BLK"]
    elif proj["metric"] == "steals":
        actual = row["STL"]
    elif proj["metric"] == "3pt made":
        actual = row["FG3M"]
    else:
        actual = 0
    return actual, actual >= proj["target"]

def add_projection(data):
    return supabase.table("projections").insert(data).execute()

def get_projections(user_id):
    return supabase.table("projections").select("*").eq("user_id", user_id).execute().data

def remove_projection(user_id, proj_id):
    return supabase.table("projections").delete().eq("user_id", user_id).eq("id", proj_id).execute()
