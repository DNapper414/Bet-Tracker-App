import requests
from datetime import datetime
import re


def get_mlb_players_for_date(date: str) -> list:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    response = requests.get(url)
    data = response.json()
    game_ids = [game["gamePk"] for d in data["dates"] for game in d["games"]]
    
    players = set()
    for game_id in game_ids:
        live_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
        r = requests.get(live_url).json()
        all_players = r.get("liveData", {}).get("boxscore", {}).get("teams", {})
        for side in ["home", "away"]:
            for pid, pdata in all_players.get(side, {}).get("players", {}).items():
                full_name = pdata.get("person", {}).get("fullName")
                if full_name:
                    players.add(full_name)
    return sorted(players)


def get_nba_players_for_date(date: str) -> list:
    # Using sportsdata.io or other stable sources recommended
    # Placeholder for player list retrieval (returns hardcoded fallback)
    return [
        "LeBron James", "Stephen Curry", "Giannis Antetokounmpo",
        "Kevin Durant", "Luka Dončić", "Nikola Jokić"
    ]


def fetch_mlb_actual(player_name, metric, game_date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={game_date}"
    game_ids = [
        game["gamePk"]
        for d in requests.get(url).json().get("dates", [])
        for game in d.get("games", [])
    ]

    for game_id in game_ids:
        live_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
        r = requests.get(live_url).json()
        all_players = {}
        for side in ["home", "away"]:
            players = r.get("liveData", {}).get("boxscore", {}).get("teams", {}).get(side, {}).get("players", {})
            all_players.update(players)
        
        for pid, pdata in all_players.items():
            if pdata.get("person", {}).get("fullName", "").lower() == player_name.lower():
                stats = pdata.get("stats", {}).get("batting", {})
                stat_map = {
                    "hits": "hits",
                    "homeruns": "homeRuns",
                    "rbi": "rbi",
                    "runs": "runs",
                    "total bases": "totalBases",
                    "stolen bases": "stolenBases"
                }
                key = stat_map.get(metric.lower())
                return stats.get(key, 0) if key else 0
    return 0


def fetch_nba_actual(player_name, metric, game_date):
    # NOTE: Replace with valid NBA stats API. Current endpoint no longer reliable.
    # Example logic using sportsdata.io or other paid API would be more dependable.
    # Simulate 0 due to lack of valid API.
    return 0


def evaluate_projection(proj):
    player = proj["player"]
    metric = proj["metric"].lower()
    target = proj["target"]
    date = proj["date"]
    sport = proj["sport"].lower()

    if sport == "mlb":
        actual = fetch_mlb_actual(player, metric, date)
    elif sport == "nba":
        actual = fetch_nba_actual(player, metric, date)
    else:
        actual = 0

    met = actual >= target if isinstance(actual, (int, float)) else False
    return actual, met
