import os
import json
import requests
import datetime
from typing import List

CACHE_DIR = ".cache"
CACHE_EXPIRY_DAYS = 3
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_path(sport: str, date_str: str) -> str:
    safe_sport = sport.lower().replace(" ", "_")
    sport_dir = os.path.join(CACHE_DIR, safe_sport)
    os.makedirs(sport_dir, exist_ok=True)
    return os.path.join(sport_dir, f"{date_str}.json")

def _is_cache_valid(path: str) -> bool:
    if not os.path.exists(path):
        return False
    modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    age = (datetime.datetime.now() - modified).days
    return age <= CACHE_EXPIRY_DAYS

def save_to_cache(sport: str, date_str: str, data):
    path = _get_cache_path(sport, date_str)
    with open(path, "w") as f:
        json.dump(data, f)

def load_from_cache(sport: str, date_str: str):
    path = _get_cache_path(sport, date_str)
    if _is_cache_valid(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def get_nba_players_for_date(date_str: str) -> List[str]:
    cached = load_from_cache("NBA", date_str)
    if cached:
        return cached
    try:
        yyyymmdd = date_str.replace("-", "")
        url = f"https://cdn.nba.com/static/json/liveData/scoreboard/scoreboard_{yyyymmdd}.json"
        res = requests.get(url)
        res.raise_for_status()
        games = res.json().get("scoreboard", {}).get("games", [])
        players = set()
        for game in games:
            for team_key in ["awayTeam", "homeTeam"]:
                team = game.get(team_key, {})
                for player in team.get("players", []):
                    full_name = player.get("name", {}).get("display")
                    if full_name:
                        players.add(full_name)
        player_list = sorted(players)
        save_to_cache("NBA", date_str, player_list)
        return player_list
    except Exception:
        return []

def get_mlb_players_for_date(date_str: str) -> List[str]:
    cached = load_from_cache("MLB", date_str)
    if cached:
        return cached
    try:
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=team,linescore"
        res = requests.get(url)
        res.raise_for_status()
        games = res.json().get("dates", [{}])[0].get("games", [])
        players = set()
        for game in games:
            for team_type in ["home", "away"]:
                team = game.get(f"{team_type}Team", {})
                team_name = team.get("name")
                if team_name:
                    players.add(team_name)  # placeholder until real player data scraped
        player_list = sorted(players)
        save_to_cache("MLB", date_str, player_list)
        return player_list
    except Exception:
        return []

# ✅ NEW: Unified wrapper
def get_players_for_date(sport: str, date_str: str) -> List[str]:
    sport = sport.strip().lower()
    if sport == "nba":
        return get_nba_players_for_date(date_str)
    elif sport == "mlb":
        return get_mlb_players_for_date(date_str)
    return []
