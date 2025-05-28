import datetime
import requests
from typing import Dict, Any, Optional


MLB_METRICS = ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"]
NBA_METRICS = ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]


def fetch_mlb_boxscore(game_pk: int) -> Optional[Dict[str, Any]]:
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    try:
        response = requests.get(url)
        if response.ok:
            return response.json()
    except Exception:
        return None
    return None


def evaluate_mlb_player_stat(boxscore: dict, player_name: str, metric: str) -> int:
    for team in ["home", "away"]:
        players = boxscore.get("liveData", {}).get("boxscore", {}).get("teams", {}).get(team, {}).get("players", {})
        for data in players.values():
            full_name = data.get("person", {}).get("fullName", "").lower()
            if full_name == player_name.lower():
                stats = data.get("stats", {}).get("batting", {})
                if metric == "hits":
                    return stats.get("hits", 0)
                elif metric == "homeruns":
                    return stats.get("homeRuns", 0)
                elif metric == "RBI":
                    return stats.get("rbi", 0)
                elif metric == "runs":
                    return stats.get("runs", 0)
                elif metric == "Total Bases":
                    return stats.get("totalBases", 0)
                elif metric == "stolen bases":
                    return stats.get("stolenBases", 0)
    return 0


def fetch_nba_boxscore(date: str) -> list:
    url = f"https://www.balldontlie.io/api/v1/games?dates[]={date}"
    try:
        response = requests.get(url)
        if response.ok:
            return response.json().get("data", [])
    except Exception:
        return []
    return []


def evaluate_nba_stat(player_stats: dict, metric: str) -> int:
    if metric == "points":
        return player_stats.get("pts", 0)
    elif metric == "rebounds":
        return player_stats.get("reb", 0)
    elif metric == "assist":
        return player_stats.get("ast", 0)
    elif metric == "PRA":
        return player_stats.get("pts", 0) + player_stats.get("reb", 0) + player_stats.get("ast", 0)
    elif metric == "blocks":
        return player_stats.get("blk", 0)
    elif metric == "steals":
        return player_stats.get("stl", 0)
    elif metric == "3pt made":
        return player_stats.get("fg3m", 0)
    return 0
