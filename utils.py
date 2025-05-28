import requests
from datetime import datetime
from typing import List

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

def get_metrics_for_sport(sport: str) -> List[str]:
    return METRICS_BY_SPORT.get(sport, [])

def get_players_for_date(sport: str, game_date: str) -> List[str]:
    if sport.upper() == "MLB":
        return get_mlb_players_for_date(game_date)
    elif sport.upper() == "NBA":
        return get_nba_players_for_date(game_date)
    return []

def get_mlb_players_for_date(game_date: str) -> List[str]:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={game_date}"
    resp = requests.get(url)
    data = resp.json()
    players = set()

    for date in data.get("dates", []):
        for game in date.get("games", []):
            game_id = game["gamePk"]
            boxscore_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
            boxscore_resp = requests.get(boxscore_url).json()
            for team in ["home", "away"]:
                for pid, player_data in boxscore_resp["teams"][team]["players"].items():
                    name = player_data["person"]["fullName"]
                    players.add(name)

    return sorted(players)

def get_nba_players_for_date(game_date: str) -> List[str]:
    date_str = datetime.strptime(game_date, "%Y-%m-%d").strftime("%Y%m%d")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/scoreboard_{date_str}.json"
    resp = requests.get(url)
    if not resp.ok:
        return []
    data = resp.json()

    players = set()
    for game in data.get("scoreboard", {}).get("games", []):
        for team_key in ["homeTeam", "awayTeam"]:
            team_data = game.get(team_key, {})
            for player in team_data.get("players", []):
                name = player.get("name")
                if name:
                    players.add(name)
    return sorted(players)

def evaluate_projection(row):
    if row["sport"] == "MLB":
        actual = fetch_mlb_stat(row["player"], row["metric"], row["date"])
    elif row["sport"] == "NBA":
        actual = fetch_nba_stat(row["player"], row["metric"], row["date"])
    else:
        actual = None
    met = actual >= row["target"] if actual is not None else None
    row["actual"] = actual
    row["met"] = met
    return row

def fetch_mlb_stat(player: str, metric: str, game_date: str) -> int:
    # Placeholder, you'd implement your MLB stat pull here.
    return 1  # Simulated stat for testing

def fetch_nba_stat(player: str, metric: str, game_date: str) -> int:
    date_str = datetime.strptime(game_date, "%Y-%m-%d").strftime("%Y%m%d")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/scoreboard_{date_str}.json"
    resp = requests.get(url)
    if not resp.ok:
        return 0

    games = resp.json().get("scoreboard", {}).get("games", [])
    for game in games:
        for team_key in ["homeTeam", "awayTeam"]:
            team = game.get(team_key, {})
            for p in team.get("players", []):
                if p.get("name") == player:
                    stats = p.get("statistics", {})
                    if metric == "points":
                        return stats.get("points", 0)
                    elif metric == "rebounds":
                        return stats.get("reboundsTotal", 0)
                    elif metric == "assist":
                        return stats.get("assists", 0)
                    elif metric == "PRA":
                        return stats.get("points", 0) + stats.get("reboundsTotal", 0) + stats.get("assists", 0)
                    elif metric == "blocks":
                        return stats.get("blocks", 0)
                    elif metric == "steals":
                        return stats.get("steals", 0)
                    elif metric == "3pt made":
                        return stats.get("threePointersMade", 0)
    return 0
