import requests
import os
from datetime import datetime

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

def get_players_for_date(sport, date):
    if sport == "MLB":
        return ["Aaron Judge", "Mookie Betts", "Shohei Ohtani", "Mike Trout"]
    elif sport == "NBA":
        try:
            url = "https://api-nba-v1.p.rapidapi.com/players"
            headers = {
                "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
                "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
            }
            params = {"season": "2023", "page": "1"}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            return [player["firstname"] + " " + player["lastname"] for player in data.get("response", [])]
        except Exception:
            return []
    return []

def evaluate_projection(projection):
    # Dummy actual logic — replace with real API
    if projection["sport"] == "MLB":
        actual = 2  # Replace with real MLB logic
    elif projection["sport"] == "NBA":
        actual = 25  # Replace with NBA stat lookup
    else:
        actual = 0
    met = actual >= projection["target"]
    return actual, met
