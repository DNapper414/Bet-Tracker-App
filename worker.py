import requests
import datetime
from supabase_client import get_projections, update_projection_result

# For NBA we switch to official nba_api:
from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv2
from nba_api.stats.static import players as nba_players_api
import time

# MLB external API remains:
MLB_BASE = "https://statsapi.mlb.com/api/v1"

# Build NBA player dictionary for fast matching
NBA_PLAYER_DICT = { 
    f"{p['first_name']} {p['last_name']}": p['id'] 
    for p in nba_players_api.get_active_players() 
}

def fetch_nba_stats():
    today = datetime.date.today().strftime('%Y-%m-%d')

    try:
        # Get today's NBA games
        gamefinder = leaguegamefinder.LeagueGameFinder(game_date_from=today, game_date_to=today)
        games = gamefinder.get_data_frames()[0]
    except Exception as e:
        print(f"[NBA] Failed to fetch games: {e}")
        return

    game_ids = games['GAME_ID'].unique()

    for game_id in game_ids:
        try:
            boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            stats = boxscore.player_stats.get_data_frame()
        except Exception as e:
            print(f"[NBA] Failed to fetch boxscore for game {game_id}: {e}")
            continue

        for _, row in stats.iterrows():
            player_name = f"{row['PLAYER_FIRST_NAME']} {row['PLAYER_LAST_NAME']}"
            points = row['PTS']
            rebounds = row['REB']
            assists = row['AST']

            projections = get_projections("guest").data  # replace with actual user system
            for proj in projections:
                if proj['sport'] != 'NBA':
                    continue
                if proj['player'] == player_name:
                    actual = {
                        "Points": points,
                        "Rebounds": rebounds,
                        "Assists": assists
                    }.get(proj['metric'], None)
                    if actual is not None:
                        met = actual >= proj['target']
                        update_projection_result(proj['id'], actual, met)

        time.sleep(1)  # be nice to nba_api servers

def fetch_mlb_stats():
    today = datetime.date.today().strftime('%Y-%m-%d')

    try:
        schedule = requests.get(f"{MLB_BASE}/schedule?sportId=1&date={today}").json().get("dates", [])
    except Exception as e:
        print(f"[MLB] Failed to fetch schedule: {e}")
        return

    if not schedule:
        return

    for game in schedule[0]["games"]:
        game_id = game["gamePk"]
        try:
            boxscore = requests.get(f"{MLB_BASE}/game/{game_id}/boxscore").json()
        except Exception as e:
            print(f"[MLB] Failed to fetch boxscore for game {game_id}: {e}")
            continue

        for team_key in ["home", "away"]:
            team = boxscore.get("teams", {}).get(team_key, {})
            for player_id, player_data in team.get("players", {}).items():
                person = player_data.get("person", {})
                full_name = person.get("fullName", "")

                stats = player_data.get("stats", {})
                batting = stats.get("batting", {})

                hits = batting.get("hits", 0)
                home_runs = batting.get("homeRuns", 0)
                strikeouts = batting.get("strikeOuts", 0)

                projections = get_projections("guest").data  # replace with actual user system
                for proj in projections:
                    if proj['sport'] != 'MLB':
                        continue
                    if proj['player'] == full_name:
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
