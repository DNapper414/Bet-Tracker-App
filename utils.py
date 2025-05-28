import os
import json
import requests
import datetime
from typing import List, Dict

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


def get_players_for_date(sport: str, date_str: str) -> List[str]:
    sport = sport.strip().lower()
    if sport == "nba":
        return get_nba_players_for_date(date_str)
    elif sport == "mlb":
        return get_mlb_players_for_date(date_str)
    return []


def evaluate_projection(projection: Dict) -> Dict:
    sport = projection.get("sport", "").lower()
    if sport == "nba":
        return evaluate_projection_nba(projection)
    elif sport == "mlb":
        return evaluate_projection_mlb(projection)
    return projection


def evaluate_projection_nba(projection: Dict) -> Dict:
    player = projection["player"].lower()
    metric = projection["metric"].lower()
    date = projection["date"].replace("-", "")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/scoreboard_{date}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        games = response.json().get("scoreboard", {}).get("games", [])
        for game in games:
            for team_key in ["homeTeam", "awayTeam"]:
                team = game.get(team_key, {})
                for p in team.get("players", []):
                    name_data = p.get("name", {})
                    full_name = name_data.get("display", "").lower()
                    if player == full_name:
                        stats = p.get("statistics", {})
                        actual = 0
                        if metric == "points":
                            actual = stats.get("points", 0)
                        elif metric == "rebounds":
                            actual = stats.get("reboundsTotal", 0)
                        elif metric == "assist":
                            actual = stats.get("assists", 0)
                        elif metric == "pra":
                            actual = sum(stats.get(k, 0) for k in ["points", "reboundsTotal", "assists"])
                        elif metric == "blocks":
                            actual = stats.get("blocks", 0)
                        elif metric == "steals":
                            actual = stats.get("steals", 0)
                        elif metric == "3pt made":
                            actual = stats.get("threePointersMade", 0)
                        projection["actual"] = actual
                        projection["met"] = actual >= projection.get("target", 0)
                        return projection
    except Exception:
        pass
    projection["actual"] = 0
    projection["met"] = False
    return projection


def evaluate_projection_mlb(projection: Dict) -> Dict:
    player = projection["player"].lower()
    metric = projection["metric"].lower()
    date = projection["date"]
    try:
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}&hydrate=team,linescore"
        schedule = requests.get(url).json()
        game_ids = [g["gamePk"] for g in schedule.get("dates", [{}])[0].get("games", [])]
        for game_id in game_ids:
            url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
            game_data = requests.get(url).json()
            players = game_data.get("liveData", {}).get("boxscore", {}).get("players", {})
            for p_id, p_data in players.items():
                full_name = p_data.get("person", {}).get("fullName", "").lower()
                if full_name == player:
                    stats = p_data.get("stats", {}).get("batting", {})
                    actual = 0
                    if metric == "hits":
                        actual = stats.get("hits", 0)
                    elif metric == "homeruns":
                        actual = stats.get("homeRuns", 0)
                    elif metric == "rbi":
                        actual = stats.get("rbi", 0)
                    elif metric == "runs":
                        actual = stats.get("runs", 0)
                    elif metric == "total bases":
                        actual = stats.get("totalBases", 0)
                    elif metric == "stolen bases":
                        actual = stats.get("stolenBases", 0)
                    projection["actual"] = actual
                    projection["met"] = actual >= projection.get("target", 0)
                    return projection
    except Exception:
        pass
    projection["actual"] = 0
    projection["met"] = False
    return projection
