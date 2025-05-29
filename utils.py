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
                stats_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
                stat_res = requests.get(stats_url, headers=RAPIDAPI_HEADERS, params={"game": game_id})
                stats = stat_res.json().get("response", [])
                for item in stats:
                    player = item.get("player")
                    if player:
                        name = f"{player['firstname']} {player['lastname']}"
                        player_names.add(name)

            return sorted(player_names) if player_names else FALLBACK_NBA_PLAYERS
        except Exception as e:
            print("NBA player list fetch failed:", e)
            return FALLBACK_NBA_PLAYERS

    return []

def get_nba_game_ids_for_date(date_str: str):
    try:
        url = "https://api-nba-v1.p.rapidapi.com/games"
        res = requests.get(url, headers=RAPIDAPI_HEADERS, params={"date": date_str})
        games = res.json().get("response", [])
        return [g.get("id") for g in games]
    except Exception as e:
        print("NBA gameId fetch error:", e)
        return []

def get_nba_player_id(full_name: str):
    try:
        first, last = full_name.split(" ", 1)
        search_url = "https://api-nba-v1.p.rapidapi.com/players"
        res = requests.get(search_url, headers=RAPIDAPI_HEADERS, params={"search": first})
        players = res.json().get("response", [])
        for player in players:
            name = f"{player['firstname']} {player['lastname']}"
            if name.lower() == full_name.lower():
                return player["id"]
    except Exception as e:
        print("NBA player ID fetch failed:", e)
    return None

def evaluate_projection(projection: dict):
    actual = 0

    if projection["sport"] == "MLB":
        actual = 2  # Placeholder
        return actual, actual >= projection["target"]

    elif projection["sport"] == "NBA":
        try:
            date = projection["date"]
            player_name = projection["player"]
            metric = projection["metric"]

            game_ids = get_nba_game_ids_for_date(date)
            player_id = get_nba_player_id(player_name)
            print(f"🧩 Evaluating {player_name} for {metric} | ID: {player_id}")

            if not player_id:
                print("❌ Player ID not found.")
                return 0, False

            for game_id in game_ids:
                stats_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
                res = requests.get(stats_url, headers=RAPIDAPI_HEADERS, params={"game": game_id, "id": player_id})
                stats = res.json().get("response", [])
                if not stats:
                    continue

                stat = stats[0].get("statistics", {})
                if metric == "points":
                    actual = int(stat.get("points", 0))
                elif metric == "rebounds":
                    actual = int(stat.get("totReb", 0))
                elif metric == "assist":
                    actual = int(stat.get("assists", 0))
                elif metric == "PRA":
                    actual = (
                        int(stat.get("points", 0)) +
                        int(stat.get("totReb", 0)) +
                        int(stat.get("assists", 0))
                    )
                elif metric == "blocks":
                    actual = int(stat.get("blocks", 0))
                elif metric == "steals":
                    actual = int(stat.get("steals", 0))
                elif metric == "3pt made":
                    actual = int(stat.get("tpm", 0))

                return actual, actual >= projection["target"]

        except Exception as e:
            print("NBA evaluate_projection failed:", e)

    return actual, actual >= projection["target"]
