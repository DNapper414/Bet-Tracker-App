import requests
import json
from datetime import datetime

BALLEDONTLIE_BASE = "https://www.balldontlie.io/api/v1"
MLB_BASE = "https://statsapi.mlb.com/api/v1"

METRICS_BY_SPORT = {
    "NBA": ["Points", "Rebounds", "Assists"],
    "MLB": ["Hits", "Home Runs", "Strikeouts"]
}

def get_players_for_date(sport, date_str):
    if sport == "NBA":
        return get_all_nba_players()
    else:
        return get_mlb_players_for_date(date_str)

# Load NBA players from static file
def get_all_nba_players():
    try:
        with open("nba_players.json", "r") as f:
            player_list = json.load(f)
        return sorted(player_list)
    except Exception as e:
        print(f"Failed to load nba_players.json: {e}")
        return []

# MLB fetching remains live, based on schedule + rosters
def get_mlb_players_for_date(date_str):
    schedule_url = f"{MLB_BASE}/schedule?sportId=1&date={date_str}"
    try:
        response = requests.get(schedule_url, timeout=10)
        response.raise_for_status()
        schedule = response.json().get("dates", [])
    except Exception as e:
        print(f"[MLB] Failed to fetch schedule: {e}")
        return []

    if not schedule:
        return []

    team_ids = set()
    for game in schedule[0].get("games", []):
        team_ids.add(game['teams']['home']['team']['id'])
        team_ids.add(game['teams']['away']['team']['id'])

    player_names = set()
    for team_id in team_ids:
        roster_url = f"{MLB_BASE}/teams/{team_id}/roster"
        try:
            roster_response = requests.get(roster_url, timeout=10)
            roster_response.raise_for_status()
            roster = roster_response.json().get("roster", [])
            for player in roster:
                full_name = player['person']['fullName']
                player_names.add(full_name)
        except Exception as e:
            print(f"[MLB] Failed to fetch roster for team {team_id}: {e}")
            continue

    return sorted(player_names)

# Safely evaluate projections
def evaluate_projection(row):
    actual = row.get("actual")
    target = row.get("target", 0)
    if actual is None:
        return None, None
    met = actual >= target
    return actual, met
