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
        return get_nba_players_for_date(date_str)
    else:
        return get_mlb_players_for_date(date_str)

def get_nba_players_for_date(date_str):
    url = f"{BALLEDONTLIE_BASE}/games?start_date={date_str}&end_date={date_str}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[NBA] Failed to fetch game schedule: {e}")
        return []

    games = data.get("data", [])
    player_names = set()

    for game in games:
        game_id = game["id"]
        stats_url = f"{BALLEDONTLIE_BASE}/stats?game_ids[]={game_id}"
        try:
            stats_response = requests.get(stats_url, timeout=10)
            stats_response.raise_for_status()
            stats_data = stats_response.json()
        except Exception as e:
            print(f"[NBA] Failed to fetch boxscore for game {game_id}: {e}")
            continue

        stats = stats_data.get("data", [])
        for stat in stats:
            player = stat["player"]
            full_name = f"{player['first_name']} {player['last_name']}"
            player_names.add(full_name)

    return sorted(player_names)

def get_mlb_players_for_date(date_str):
    url = f"{MLB_BASE}/schedule?sportId=1&date={date_str}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[MLB] Failed to fetch schedule: {e}")
        return []

    schedule = data.get("dates", [])
    if not schedule:
        return []

    player_names = set()

    for game in schedule[0].get("games", []):
        game_id = game["gamePk"]
        boxscore_url = f"{MLB_BASE}/game/{game_id}/boxscore"
        try:
            boxscore_response = requests.get(boxscore_url, timeout=10)
            boxscore_response.raise_for_status()
            boxscore = boxscore_response.json()
        except Exception as e:
            print(f"[MLB] Failed to fetch boxscore for game {game_id}: {e}")
            continue

        for team_key in ["home", "away"]:
            team = boxscore.get("teams", {}).get(team_key, {})
            for player_id, player_data in team.get("players", {}).items():
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
