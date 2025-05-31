import requests
import json
from datetime import datetime

# New NBA imports using nba_api
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder

# External APIs
BALLEDONTLIE_BASE = "https://www.balldontlie.io/api/v1"  # No longer used for players, but kept for reference
MLB_BASE = "https://statsapi.mlb.com/api/v1"

# Metrics supported
METRICS_BY_SPORT = {
    "NBA": ["Points", "Rebounds", "Assists"],
    "MLB": ["Hits", "Home Runs", "Strikeouts"]
}

def get_players_for_date(sport, date_str):
    if sport == "NBA":
        return get_nba_players_for_date(date_str)
    else:
        return get_mlb_players_for_date(date_str)

# ✅ Fully patched NBA logic using nba_api
def get_nba_players_for_date(date_str):
    try:
        # Parse date string into datetime object
        game_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Use leaguegamefinder to get games played on that date
        gamefinder = leaguegamefinder.LeagueGameFinder(game_date_from=game_date, game_date_to=game_date)
        games = gamefinder.get_data_frames()[0]

        # Extract all team IDs playing today
        team_ids = set(games['TEAM_ID'].unique())

        # Load all active NBA players
        all_players = players.get_active_players()

        # Filter players that belong to teams playing today
        today_players = [
            f"{p['first_name']} {p['last_name']}"
            for p in all_players
            if p['team_id'] in team_ids
        ]

        return sorted(today_players)
    except Exception as e:
        print(f"[NBA] Failed to fetch NBA players: {e}")
        return []

# ✅ MLB stays schedule-based via MLB API
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

# ✅ Safe evaluator for projections
def evaluate_projection(row):
    actual = row.get("actual")
    target = row.get("target", 0)
    if actual is None:
        return None, None
    met = actual >= target
    return actual, met
