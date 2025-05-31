import requests
import json
from datetime import datetime

# No longer using RapidAPI — all free APIs now

BALLEDONTLIE_BASE = "https://www.balldontlie.io/api/v1"
MLB_BASE = "https://statsapi.mlb.com/api/v1"

METRICS_BY_SPORT = {
    "NBA": ["Points", "Rebounds", "Assists"],
    "MLB": ["Hits", "Home Runs", "Strikeouts"]
}

def get_players_for_date(sport, date_str):
    if sport == "NBA":
        return get_nba_players_for_date(date_str)
    else:
        return get_mlb_players_for_date(date_str)

def get_nba_players_for_date(date_str):
    response = requests.get(f"{BALLEDONTLIE_BASE}/games?start_date={date_str}&end_date={date_str}")
    games = response.json().get("data", [])

    player_names = set()

    for game in games:
        game_id = game["id"]
        stats = requests.get(f"{BALLEDONTLIE_BASE}/stats?game_ids[]={game_id}").json().get("data", [])
        for stat in stats:
            player = stat["player"]
            full_name = f"{player['first_name']} {player['last_name']}"
            player_names.add(full_name)

    return sorted(player_names)

def get_mlb_players_for_date(date_str):
    response = requests.get(f"{MLB_BASE}/schedule?sportId=1&date={date_str}")
    schedule = response.json().get("dates", [])
    if not schedule:
        return []

    player_names = set()

    for game in schedule[0].get("games", []):
        game_id = game["gamePk"]
        boxscore = requests.get(f"{MLB_BASE}/game/{game_id}/boxscore").json()

        for team_key in ["home", "away"]:
            team = boxscore["teams"][team_key]
            for player_id, player_data in team["players"].items():
                person = player_data.get("person", {})
                full_name = person.get("fullName", "")
                if full_name:
                    player_names.add(full_name)

    return sorted(player_names)

def evaluate_projection(row):
    actual = row.get("actual", 0)
    target = row.get("target", 0)
    met = actual >= target
    return actual, met
