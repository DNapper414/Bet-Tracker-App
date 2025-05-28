import requests
import os
from datetime import datetime

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

# Static fallback NBA players if API fails
FALLBACK_NBA_PLAYERS = [
    "LeBron James", "Stephen Curry", "Kevin Durant", "Jayson Tatum", "Giannis Antetokounmpo"
]

def get_players_for_date(sport, date):
    if sport == "MLB":
        return ["Aaron Judge", "Mookie Betts", "Shohei Ohtani", "Mike Trout"]
    elif sport == "NBA":
        try:
            url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
            headers = {
                "x-rapidapi-key": "47945fd24fmsh2539580c53289bdp119b78jsne5525ec5acdf",
                "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
            }
            params = {"game": "8133"}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            return list({
                f"{item['player']['firstname']} {item['player']['lastname']}"
                for item in data.get("response", [])
                if "player" in item
            })
        except Exception:
            return FALLBACK_NBA_PLAYERS
    return []

def evaluate_projection(projection):
    actual = 0

    if projection["sport"] == "MLB":
        actual = 2  # replace with real MLB lookup logic
    elif projection["sport"] == "NBA":
        # Use same fixed game for example; in real app you'd map to correct game by date/player
        try:
            url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
            headers = {
                "x-rapidapi-key": "47945fd24fmsh2539580c53289bdp119b78jsne5525ec5acdf",
                "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
            }
            params = {"game": "8133"}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            for entry in data.get("response", []):
                full_name = f"{entry['player']['firstname']} {entry['player']['lastname']}"
                if full_name == projection["player"]:
                    stats = entry["statistics"]
                    if projection["metric"] == "points":
                        actual = stats.get("points", 0)
                    elif projection["metric"] == "rebounds":
                        actual = stats.get("totReb", 0)
                    elif projection["metric"] == "assist":
                        actual = stats.get("assists", 0)
                    elif projection["metric"] == "PRA":
                        actual = stats.get("points", 0) + stats.get("totReb", 0) + stats.get("assists", 0)
                    elif projection["metric"] == "blocks":
                        actual = stats.get("blocks", 0)
                    elif projection["metric"] == "steals":
                        actual = stats.get("steals", 0)
                    elif projection["metric"] == "3pt made":
                        actual = stats.get("tpm", 0)
                    break
        except Exception:
            actual = 0

    met = actual >= projection["target"]
    return actual, met
