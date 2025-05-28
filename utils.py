import os
import requests
from datetime import datetime

# NBA Player Autocomplete from RapidAPI
def get_nba_players_for_date(game_date):
    key = os.getenv("RAPIDAPI_KEY")
    host = "api-nba-v1.p.rapidapi.com"
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host
    }
    url = "https://api-nba-v1.p.rapidapi.com/players"
    params = {"team": "all", "season": "2023"}

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("RapidAPI error:", response.status_code)
            return []
        data = response.json().get("response", [])
        return sorted(set(f"{p['firstname']} {p['lastname']}" for p in data if p.get("firstname") and p.get("lastname")))
    except Exception as e:
        print("NBA player fetch failed:", e)
        return []

# MLB Dummy Sample
def get_mlb_players_for_date(game_date):
    return sorted(["Aaron Judge", "Shohei Ohtani", "Mookie Betts"])

# Available metrics by sport
METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assists", "PRA", "blocks", "steals", "3pt made"]
}
