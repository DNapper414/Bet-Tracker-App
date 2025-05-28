import requests
import datetime

METRICS_BY_SPORT = {
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"]
}

def get_players_for_date(sport, date):
    date_str = date.strftime("%Y-%m-%d")
    if sport == "MLB":
        return get_mlb_players_for_date(date_str)
    elif sport == "NBA":
        return get_nba_players_for_date(date_str)
    return []

def get_mlb_players_for_date(date_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={date_str}"
    games = requests.get(url).json().get("dates", [])[0].get("games", [])
    player_names = set()
    for game in games:
        for team_type in ["away", "home"]:
            team_id = game["teams"][team_type]["team"]["id"]
            roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
            players = requests.get(roster_url).json().get("roster", [])
            for player in players:
                player_names.add(player["person"]["fullName"])
    return sorted(player_names)

def get_nba_players_for_date(date_str):
    yyyymmdd = date_str.replace("-", "")
    url = f"https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_{yyyymmdd}.json"
    res = requests.get(url)
    player_names = set()

    if res.status_code != 200:
        return []

    games = res.json().get("leagueSchedule", {}).get("gameDates", [])
    for game in games:
        for g in game.get("games", []):
            for team in [g["awayTeam"], g["homeTeam"]]:
                team_id = team["teamId"]
                players_url = f"https://data.nba.com/data/v2015/json/mobile_teams/nba/2024/teams/{team_id}_roster.json"
                players_res = requests.get(players_url)
                if players_res.status_code == 200:
                    roster = players_res.json().get("t", {}).get("pl", [])
                    for p in roster:
                        player_names.add(p["fn"] + " " + p["ln"])
    return sorted(player_names)

def evaluate_projection(player, metric, date, sport):
    if sport == "MLB":
        return evaluate_projection_mlb_statsapi(player, metric, date)
    elif sport == "NBA":
        return evaluate_projection_nba(player, metric, date)
    return None

def evaluate_projection_mlb_statsapi(player_name, metric, date_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    schedule = requests.get(url).json()
    games = schedule.get("dates", [])[0].get("games", [])

    for game in games:
        game_id = game.get("gamePk")
        stats_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
        stats = requests.get(stats_url).json()

        all_players = stats.get("liveData", {}).get("boxscore", {}).get("teams", {})
        for side in ["home", "away"]:
            players = all_players.get(side, {}).get("players", {})
            for pdata in players.values():
                full_name = pdata.get("person", {}).get("fullName", "").lower()
                if player_name.lower() == full_name:
                    stat = pdata.get("stats", {}).get("batting", {})
                    return extract_mlb_stat(metric, stat)
    return 0

def extract_mlb_stat(metric, stats):
    return {
        "hits": stats.get("hits", 0),
        "homeruns": stats.get("homeRuns", 0),
        "RBI": stats.get("rbi", 0),
        "runs": stats.get("runs", 0),
        "Total Bases": stats.get("totalBases", 0),
        "stolen bases": stats.get("stolenBases", 0)
    }.get(metric, 0)

def evaluate_projection_nba(player_name, metric, date_str):
    date_fmt = date_str.replace("-", "")
    url = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_{date_fmt}.json"
    res = requests.get(url)

    if res.status_code != 200:
        return 0

    games = res.json().get("scoreboard", {}).get("games", [])
    for game in games:
        for team_type in ["awayTeam", "homeTeam"]:
            for player in game[team_type].get("players", []):
                full_name = f"{player['firstName']} {player['familyName']}".lower()
                if player_name.lower() == full_name:
                    stats = player.get("statistics", {})
                    return extract_nba_stat(metric, stats)
    return 0

def extract_nba_stat(metric, stats):
    points = stats.get("points", 0)
    rebounds = stats.get("reboundsTotal", 0)
    assists = stats.get("assists", 0)
    return {
        "points": points,
        "rebounds": rebounds,
        "assist": assists,
        "PRA": points + rebounds + assists,
        "blocks": stats.get("blocks", 0),
        "steals": stats.get("steals", 0),
        "3pt made": stats.get("threePointersMade", 0)
    }.get(metric, 0)
