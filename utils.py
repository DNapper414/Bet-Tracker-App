import os
import requests
from datetime import datetime
from functools import lru_cache

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

FALLBACK_NBA_PLAYERS = [
    "LeBron James", "Stephen Curry", "Kevin Durant", "Jayson Tatum", "Giannis Antetokounmpo"
]

# Headers for RapidAPI (env var from Railway)
RAPIDAPI_HEADERS = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
}

@lru_cache(maxsize=128)
def get_players_for_date(sport: str, date_str: str):
    if sport == "MLB":
        return ["Aaron Judge", "Shohei Ohtani", "Mike Trout", "Mookie Betts"]

    elif sport == "NBA":
        try:
            url = "https://api-nba-v1.p.rapidapi.com/games"
            games_res = requests.get(url, headers=RAPIDAPI_HEADERS, params={"date": date_str})
            games = games_res.json().get("response", [])

            player_names = set()
            for game in games:
                game_id = game.get("id")
                stat_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
                stat_res = requests.get(stat_url, headers=RAPIDAPI_HEADERS, params={"game": game_id})
                stats = stat_res.json().get("response", [])
                for item in stats:
                    player = item.get("player")
                    if player:
                        full_name = f"{player['firstname']} {player['lastname']}"
                        player_names.add(full_name)

            return sorted(player_names) if player_names else FALLBACK_NBA_PLAYERS
        except Exception:
            return FALLBACK_NBA_PLAYERS

    return []

def get_nba_game_ids_for_date(date_str: str):
    try:
        url = "https://api-nba-v1.p.rapidapi.com/games"
        res = requests.get(url, headers=RAPIDAPI_HEADERS, params={"date": date_str})
        games = res.json().get("response", [])
        return [g.get("id") for g in games]
    except Exception:
        return []

def evaluate_projection(projection: dict):
    actual = 0

    if projection["sport"] == "MLB":
        actual = 2  # Placeholder until live MLB stats are integrated

    elif projection["sport"] == "NBA":
        try:
            date = projection["date"]
            player_name = projection["player"]

            game_ids = get_nba_game_ids_for_date(date)

            for game_id in game_ids:
                stats_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
                res = requests.get(stats_url, headers=RAPIDAPI_HEADERS, params={"game": game_id})
                data = res.json().get("response", [])

                for item in data:
                    player = item.get("player")
                    stats = item.get("statistics", {})
                    if not player:
                        continue

                    full_name = f"{player['firstname']} {player['lastname']}"
                    if full_name != player_name:
                        continue

                    if projection["metric"] == "points":
                        actual = int(stats.get("points", 0))
                    elif projection["metric"] == "rebounds":
                        actual = int(stats.get("totReb", 0))
                    elif projection["metric"] == "assist":
                        actual = int(stats.get("assists", 0))
                    elif projection["metric"] == "PRA":
                        actual = (
                            int(stats.get("points", 0)) +
                            int(stats.get("totReb", 0)) +
                            int(stats.get("assists", 0))
                        )
                    elif projection["metric"] == "blocks":
                        actual = int(stats.get("blocks", 0))
                    elif projection["metric"] == "steals":
                        actual = int(stats.get("steals", 0))
                    elif projection["metric"] == "3pt made":
                        actual = int(stats.get("tpm", 0))
                    return actual, actual >= projection["target"]

        except Exception:
            pass

    return actual, actual >= projection["target"]
