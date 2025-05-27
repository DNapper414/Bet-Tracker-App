import requests
from datetime import datetime
import os


# -------------------
# MLB Projections
# -------------------

def get_mlb_game_data(date: str) -> list:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
    resp = requests.get(url)
    return resp.json()["dates"][0]["games"] if resp.status_code == 200 else []


def get_mlb_player_stats(game_id: int) -> dict:
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    resp = requests.get(url)
    data = resp.json()
    stats = {}
    try:
        all_players = data["liveData"]["boxscore"]["teams"]
        for team in ["home", "away"]:
            for player_id, player_data in all_players[team]["players"].items():
                name = player_data["person"]["fullName"].lower()
                hits = player_data["stats"]["batting"].get("hits", 0)
                stats[name] = hits
    except Exception:
        pass
    return stats


def evaluate_projections_mlb(projections: list):
    for p in projections:
        if p["actual"] is not None:
            continue
        games = get_mlb_game_data(p["date"])
        for g in games:
            game_id = g["gamePk"]
            stats = get_mlb_player_stats(game_id)
            player_hits = stats.get(p["player"].lower())
            if player_hits is not None:
                p["actual"] = player_hits
                p["met"] = player_hits >= p["target"]
                break


# -------------------
# NBA Projections (via RapidAPI)
# -------------------

RAPID_API_KEY = os.getenv("RAPIDAPI_KEY")  # Set this in Railway or .env

def get_nba_player_stats_rapidapi(name: str, date: str) -> int:
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }

    query = {
        "date": date,
        "season": "2024",  # adjust if necessary
        "team": "",        # not required
        "player": name
    }

    try:
        res = requests.get(url, headers=headers, params=query)
        stats = res.json()["response"]

        if not stats:
            return None

        total_points = 0
        for entry in stats:
            total_points += entry["points"]

        return total_points
    except Exception as e:
        print(f"NBA API error for {name}: {e}")
        return None


def evaluate_projections_nba(projections: list):
    for p in projections:
        if p["actual"] is not None:
            continue
        date_str = p["date"]
        points = get_nba_player_stats_rapidapi(p["player"], date_str)
        if points is not None:
            p["actual"] = points
            p["met"] = points >= p["target"]
