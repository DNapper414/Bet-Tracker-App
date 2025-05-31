import requests
import datetime
from supabase_client import get_projections, update_projection_result

# NBA: balldontlie.io API
BALLEDONTLIE_BASE = "https://www.balldontlie.io/api/v1"
# MLB: statsapi.mlb.com API
MLB_BASE = "https://statsapi.mlb.com/api/v1"

def fetch_nba_stats():
    today = datetime.date.today().isoformat()
    games = requests.get(f"{BALLEDONTLIE_BASE}/games?start_date={today}&end_date={today}").json()["data"]

    for game in games:
        game_id = game["id"]
        stats = requests.get(f"{BALLEDONTLIE_BASE}/stats?game_ids[]={game_id}").json()["data"]
        for player_stat in stats:
            process_nba_stat(player_stat)

def process_nba_stat(player_stat):
    player_name = f"{player_stat['player']['first_name']} {player_stat['player']['last_name']}"
    points = player_stat['pts']
    rebounds = player_stat['reb']
    assists = player_stat['ast']

    # Simplified matching by name (can later improve by storing external IDs)
    projections = get_projections("guest").data
    for proj in projections:
        if proj['sport'] != 'NBA': continue
        if proj['player'] == player_name:
            actual = {
                "Points": points,
                "Rebounds": rebounds,
                "Assists": assists
            }.get(proj['metric'], None)
            if actual is not None:
                met = actual >= proj['target']
                update_projection_result(proj['id'], actual, met)

def fetch_mlb_stats():
    today = datetime.date.today().isoformat()
    schedule = requests.get(f"{MLB_BASE}/schedule?sportId=1&date={today}").json()["dates"]
    if not schedule: return

    for game in schedule[0]["games"]:
        game_id = game["gamePk"]
        boxscore = requests.get(f"{MLB_BASE}/game/{game_id}/boxscore").json()
        for player_id, player in boxscore["stats"]["batting"].items():
            process_mlb_stat(player)

def process_mlb_stat(player_stat):
    player_name = player_stat['person']['fullName']
    hits = player_stat.get("hits", 0)
    home_runs = player_stat.get("homeRuns", 0)
    strikeouts = player_stat.get("strikeOuts", 0)

    projections = get_projections("guest").data
    for proj in projections:
        if proj['sport'] != 'MLB': continue
        if proj['player'] == player_name:
            actual = {
                "Hits": hits,
                "Home Runs": home_runs,
                "Strikeouts": strikeouts
            }.get(proj['metric'], None)
            if actual is not None:
                met = actual >= proj['target']
                update_projection_result(proj['id'], actual, met)

def main():
    fetch_nba_stats()
    fetch_mlb_stats()

if __name__ == "__main__":
    main()
