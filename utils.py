import requests
import datetime

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

def get_players_for_date(date: datetime.date, sport: str) -> list:
    if sport == "MLB":
        return get_mlb_players_for_date(date)
    elif sport == "NBA":
        return get_nba_players_for_date(date)
    return []

def get_mlb_players_for_date(date: datetime.date) -> list:
    date_str = date.strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    response = requests.get(url)
    data = response.json()
    players = set()
    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            boxscore_url = f"https://statsapi.mlb.com/api/v1/game/{game['gamePk']}/boxscore"
            box_res = requests.get(boxscore_url)
            box_data = box_res.json()
            for team in ["home", "away"]:
                for pid, player_data in box_data["teams"][team]["players"].items():
                    if "person" in player_data:
                        players.add(player_data["person"]["fullName"])
    return sorted(players)

def get_nba_players_for_date(date: datetime.date) -> list:
    date_str = date.strftime("%Y%m%d")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{date_str}.json"
    response = requests.get(url)
    if not response.ok:
        return []
    data = response.json()
    players = set()
    for game in data.get("scoreboard", {}).get("games", []):
        for team_key in ["homeTeam", "awayTeam"]:
            team = game.get(team_key, {})
            for player in team.get("players", []):
                if "name" in player:
                    players.add(player["name"])
    return sorted(players)

def evaluate_projection(proj: dict) -> dict:
    if proj["sport"] == "MLB":
        return evaluate_projection_mlb(proj)
    elif proj["sport"] == "NBA":
        return evaluate_projection_nba(proj)
    return {"actual": None, "met": None}

def evaluate_projection_mlb(proj: dict) -> dict:
    date_str = proj["date"]
    name = proj["player"]
    metric = proj["metric"].lower()
    target = proj["target"]

    game_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    res = requests.get(game_url)
    data = res.json()
    for date_data in data.get("dates", []):
        for game in date_data.get("games", []):
            game_pk = game["gamePk"]
            box_url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
            box_data = requests.get(box_url).json()
            for team in ["home", "away"]:
                for p in box_data["teams"][team]["players"].values():
                    if p["person"]["fullName"].lower() == name.lower():
                        stats = p.get("stats", {}).get("batting", {})
                        actual = extract_mlb_stat(stats, metric)
                        return {"actual": actual, "met": actual >= target}
    return {"actual": 0, "met": False}

def extract_mlb_stat(stats, metric):
    return {
        "hits": stats.get("hits", 0),
        "homeruns": stats.get("homeRuns", 0),
        "rbi": stats.get("rbi", 0),
        "runs": stats.get("runs", 0),
        "total bases": stats.get("totalBases", 0),
        "stolen bases": stats.get("stolenBases", 0),
    }.get(metric, 0)

def evaluate_projection_nba(proj: dict) -> dict:
    date_str = proj["date"].replace("-", "")
    name = proj["player"]
    metric = proj["metric"].lower()
    target = proj["target"]

    url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{date_str}.json"
    res = requests.get(url)
    if not res.ok:
        return {"actual": 0, "met": False}

    data = res.json()
    for game in data.get("games", {}).values():
        for team in ["homeTeam", "awayTeam"]:
            for player in game[team]["players"]:
                if player.get("name", "").lower() == name.lower():
                    stats = player.get("statistics", {})
                    actual = extract_nba_stat(stats, metric)
                    return {"actual": actual, "met": actual >= target}
    return {"actual": 0, "met": False}

def extract_nba_stat(stats, metric):
    stat_map = {
        "points": stats.get("points", 0),
        "rebounds": stats.get("reboundsTotal", 0),
        "assist": stats.get("assists", 0),
        "blocks": stats.get("blocks", 0),
        "steals": stats.get("steals", 0),
        "3pt made": stats.get("threePointersMade", 0),
    }
    if metric == "pra":
        return (
            stats.get("points", 0)
            + stats.get("reboundsTotal", 0)
            + stats.get("assists", 0)
        )
    return stat_map.get(metric, 0)
