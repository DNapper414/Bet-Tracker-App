import requests
import os
from datetime import datetime

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

# Static fallback NBA player names
FALLBACK_NBA_PLAYERS = [
    "LeBron James", "Stephen Curry", "Kevin Durant", "Jayson Tatum", "Giannis Antetokounmpo"
]

def get_players_for_date(sport, date):
    if sport == "MLB":
        return ["Aaron Judge", "Mookie Betts", "Shohei Ohtani", "Mike Trout"]

    elif sport == "NBA":
        try:
            games_url = "https://api-nba-v1.p.rapidapi.com/games"
            headers = {
                "x-rapidapi-key": "47945fd24fmsh2539580c53289bdp119b78jsne5525ec5acdf",
                "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
            }
            params = {"date": date}
            response = requests.get(games_url, headers=headers, params=params)
            games = response.json().get("response", [])

            player_names = set()

            for game in games:
                game_id = game.get("id")
                stats_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
                stat_resp = requests.get(stats_url, headers=headers, params={"game": game_id})
                stat_data = stat_resp.json().get("response", [])

                for item in stat_data:
                    if "player" in item:
                        full_name = f"{item['player']['firstname']} {item['player']['lastname']}"
                        player_names.add(full_name)

            return sorted(player_names) if player_names else FALLBACK_NBA_PLAYERS

        except Exception:
            return FALLBACK_NBA_PLAYERS

    return []

def evaluate_projection(projection):
    actual = 0

    if projection["sport"] == "MLB":
        actual = 2  # Replace with real MLB lookup logic

    elif projection["sport"] == "NBA":
        try:
            date = projection["date"]
            player_name = projection["player"]

            games_url = "https://api-nba-v1.p.rapidapi.com/games"
            headers = {
                "x-rapidapi-key": "47945fd24fmsh2539580c53289bdp119b78jsne5525ec5acdf",
                "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
            }
            params = {"date": date}
            response = requests.get(games_url, headers=headers, params=params)
            games = response.json().get("response", [])

            for game in games:
                game_id = game.get("id")
                stats_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
                stat_resp = requests.get(stats_url, headers=headers, params={"game": game_id})
                stat_data = stat_resp.json().get("response", [])

                for item in stat_data:
                    full_name = f"{item['player']['firstname']} {item['player']['lastname']}"
                    if full_name == player_name:
                        stats = item["statistics"]
                        if projection["metric"] == "points":
                            actual = stats.get("points", 0)
                        elif projection["metric"] == "rebounds":
                            actual = stats.get("totReb", 0)
                        elif projection["metric"] == "assist":
                            actual = stats.get("assists", 0)
                        elif projection["metric"] == "PRA":
                            actual = stats.get("points", 0) + stats.get("totReb", 0) + stats.get("assists", 0)
                        elif projection["metric"] == "blocks":
                            actual = stats.get("blocks", 0)
                        elif projection["metric"] == "steals":
                            actual = stats.get("steals", 0)
                        elif projection["metric"] == "3pt made":
                            actual = stats.get("tpm", 0)
                        break

        except Exception:
            actual = 0

    met = actual >= projection["target"]
    return actual, met
