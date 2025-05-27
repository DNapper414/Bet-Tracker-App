import requests
from datetime import datetime
import pandas as pd


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
    today = datetime.today().strftime("%Y-%m-%d")
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


def get_nba_games(date: str) -> list:
    url = f"https://www.balldontlie.io/api/v1/games?start_date={date}&end_date={date}"
    resp = requests.get(url)
    return resp.json()["data"] if resp.status_code == 200 else []


def get_nba_player_stats(game_id: int) -> list:
    url = f"https://www.balldontlie.io/api/v1/stats?game_ids[]={game_id}&per_page=100"
    resp = requests.get(url)
    return resp.json()["data"] if resp.status_code == 200 else []


def evaluate_projections_nba(projections: list):
    for p in projections:
        if p["actual"] is not None:
            continue
        date = p["date"]
        player_name = p["player"].lower()
        games = get_nba_games(date)
        for game in games:
            stats = get_nba_player_stats(game["id"])
            for stat in stats:
                full_name = f"{stat['player']['first_name']} {stat['player']['last_name']}".lower()
                if full_name == player_name:
                    points = stat.get("pts", 0)
                    p["actual"] = points
                    p["met"] = points >= p["target"]
                    return
