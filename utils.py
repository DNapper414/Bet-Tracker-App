import requests
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

# NBA player fetch using teams -> rosters
def get_nba_players_for_date(date_str):
    url = f"{BALLEDONTLIE_BASE}/games?start_date={date_str}&end_date={date_str}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        games = response.json().get("data", [])
    except Exception as e:
        print(f"[NBA] Failed to fetch games: {e}")
        return []

    team_ids = set()
    for game in games:
        team_ids.add(game['home_team']['id'])
        team_ids.add(game['visitor_team']['id'])

    player_names = set()
    for team_id in team_ids:
        team_players_url = f"{BALLEDONTLIE_BASE}/players?per_page=100&team_ids[]={team_id}"
        try:
            team_response = requests.get(team_players_url, timeout=10)
            team_response.raise_for_status()
            players = team_response.json().get("data", [])
            for player in players:
                full_name = f"{player['first_name']} {player['last_name']}"
                player_names.add(full_name)
        except Exception as e:
            print(f"[NBA] Failed to fetch roster for team {team_id}: {e}")
            continue

    return sorted(player_names)

# MLB player fetch using teams -> rosters
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

def evaluate_projection(row):
    actual = row.get("actual", 0)
    target = row.get("target", 0)
    met = actual >= target
    return actual, met
