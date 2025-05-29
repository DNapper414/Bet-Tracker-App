import requests
import json
from datetime import datetime
from pathlib import Path

# Constants
RAPIDAPI_KEY = "your_rapidapi_key_here"
RAPIDAPI_HOST = "api-nba-v1.p.rapidapi.com"
NBA_CACHE_PATH = Path("nba_cache.json")

METRICS_BY_SPORT = {
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"],
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"]
}

# Load or initialize cache
if NBA_CACHE_PATH.exists():
    with open(NBA_CACHE_PATH, "r") as f:
        nba_cache = json.load(f)
else:
    nba_cache = {}

def get_players_for_date(sport, date_str):
    if sport == "NBA":
        return get_nba_players_for_date(date_str)
    else:
        return get_mlb_players_for_date(date_str)

def get_nba_players_for_date(date_str):
    if date_str in nba_cache:
        return nba_cache[date_str]

    url = f"https://api-nba-v1.p.rapidapi.com/games"
    query = {"date": date_str}
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    response = requests.get(url, headers=headers, params=query)
    games = response.json().get("response", [])

    player_names = set()
    for game in games:
        game_id = game["id"]
        stats_url = f"https://api-nba-v1.p.rapidapi.com/players/statistics"
        stats_query = {"game": game_id}
        stats_resp = requests.get(stats_url, headers=headers, params=stats_query)
        stats = stats_resp.json().get("response", [])
        for s in stats:
            full_name = s["player"]["firstname"] + " " + s["player"]["lastname"]
            player_names.add(full_name)

    player_list = sorted(player_names)
    nba_cache[date_str] = player_list
    with open(NBA_CACHE_PATH, "w") as f:
        json.dump(nba_cache, f)
    return player_list

def get_mlb_players_for_date(date_str):
    return ["Aaron Judge", "Shohei Ohtani", "Mookie Betts", "Juan Soto"]

def evaluate_projection(row):
    sport = row["sport"]
    metric = row["metric"]
    player = row["player"]
    date = row["date"]

    if sport == "NBA":
        return evaluate_projection_nba(date, player, metric)
    else:
        return evaluate_projection_mlb(date, player, metric)

def evaluate_projection_nba(date, player, metric):
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    games_resp = requests.get(
        "https://api-nba-v1.p.rapidapi.com/games",
        headers=headers,
        params={"date": date}
    )
    games = games_resp.json().get("response", [])

    for game in games:
        game_id = game["id"]
        stats_resp = requests.get(
            "https://api-nba-v1.p.rapidapi.com/players/statistics",
            headers=headers,
            params={"game": game_id}
        )
        stats = stats_resp.json().get("response", [])
        for s in stats:
            name = s["player"]["firstname"] + " " + s["player"]["lastname"]
            if name == player:
                return extract_nba_stat(s, metric), None  # Skip met calc here
    return 0, None

def extract_nba_stat(stat, metric):
    if metric == "points":
        return stat.get("points", 0)
    elif metric == "rebounds":
        return stat.get("totReb", 0)
    elif metric == "assist":
        return stat.get("assists", 0)
    elif metric == "PRA":
        return (
            stat.get("points", 0)
            + stat.get("totReb", 0)
            + stat.get("assists", 0)
        )
    elif metric == "blocks":
        return stat.get("blocks", 0)
    elif metric == "steals":
        return stat.get("steals", 0)
    elif metric == "3pt made":
        return stat.get("fg3m", 0)
    return 0

def evaluate_projection_mlb(date, player, metric):
    # Dummy MLB fallback
    sample_stats = {
        "hits": 2, "homeruns": 1, "RBI": 3, "runs": 1, "Total Bases": 5, "stolen bases": 1
    }
    return sample_stats.get(metric, 0), None
