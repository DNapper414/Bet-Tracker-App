import requests
import pandas as pd
from datetime import datetime

def get_mlb_players_for_date(game_date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={game_date}"
    response = requests.get(url)
    data = response.json()

    player_names = set()
    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            game_pk = game.get("gamePk")
            if not game_pk:
                continue

            live_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
            r = requests.get(live_url)
            game_data = r.json()
            for team in ["home", "away"]:
                players = game_data.get("liveData", {}).get("boxscore", {}).get("teams", {}).get(team, {}).get("players", {})
                for player in players.values():
                    full_name = player.get("person", {}).get("fullName")
                    if full_name:
                        player_names.add(full_name)

    return sorted(player_names)

def get_nba_players_for_date(game_date):
    # Converts date to NBA format YYYYMMDD
    date_str = datetime.strptime(str(game_date), "%Y-%m-%d").strftime("%Y%m%d")
    scoreboard_url = f"https://data.nba.net/10s/prod/v1/{date_str}/scoreboard.json"
    r = requests.get(scoreboard_url)
    data = r.json()

    player_names = set()
    for game in data.get("games", []):
        game_id = game.get("gameId")
        if not game_id:
            continue
        boxscore_url = f"https://data.nba.net/prod/v1/{date_str}/{game_id}_boxscore.json"
        box_res = requests.get(boxscore_url)
        if box_res.status_code != 200:
            continue
        box_data = box_res.json()
        for team in ["hTeam", "vTeam"]:
            players = box_data.get("stats", {}).get("activePlayers", [])
            for p in players:
                full_name = f"{p.get('firstName', '').strip()} {p.get('lastName', '').strip()}"
                if full_name.strip():
                    player_names.add(full_name.strip())

    return sorted(player_names)

def evaluate_projections_mlb_statsapi(df):
    df = df.copy()
    df["actual"] = 0
    df["met"] = False

    for i, row in df.iterrows():
        player = row["player"]
        metric = row["metric"].lower()
        date = row["date"]
        total = 0

        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
        r = requests.get(url)
        games = r.json().get("dates", [])[0].get("games", [])

        for game in games:
            game_pk = game["gamePk"]
            live_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
            game_data = requests.get(live_url).json()

            for team in ["home", "away"]:
                players = game_data.get("liveData", {}).get("boxscore", {}).get("teams", {}).get(team, {}).get("players", {})
                for p in players.values():
                    p_name = p.get("person", {}).get("fullName", "")
                    stats = p.get("stats", {}).get("batting", {})
                    if player == p_name:
                        if metric == "hits":
                            total += stats.get("hits", 0)
                        elif metric == "homeruns":
                            total += stats.get("homeRuns", 0)
                        elif metric == "rbi":
                            total += stats.get("rbi", 0)
                        elif metric == "runs":
                            total += stats.get("runs", 0)
                        elif metric == "total bases":
                            total += stats.get("totalBases", 0)
                        elif metric == "stolen bases":
                            total += stats.get("stolenBases", 0)
        df.at[i, "actual"] = total
        df.at[i, "met"] = total >= row["target"]
    return df

def evaluate_projections_nba_nbaapi(df):
    df = df.copy()
    df["actual"] = 0
    df["met"] = False

    for i, row in df.iterrows():
        player = row["player"]
        metric = row["metric"].lower()
        date = row["date"]
        date_str = datetime.strptime(str(date), "%Y-%m-%d").strftime("%Y%m%d")
        score_url = f"https://data.nba.net/10s/prod/v1/{date_str}/scoreboard.json"
        r = requests.get(score_url)
        data = r.json()

        total = 0
        for game in data.get("games", []):
            game_id = game.get("gameId")
            if not game_id:
                continue
            box_url = f"https://data.nba.net/prod/v1/{date_str}/{game_id}_boxscore.json"
            box_res = requests.get(box_url)
            if box_res.status_code != 200:
                continue
            box = box_res.json()
            for p in box.get("stats", {}).get("activePlayers", []):
                full_name = f"{p.get('firstName', '').strip()} {p.get('lastName', '').strip()}"
                if player.lower() == full_name.lower():
                    pts = p.get("points", 0)
                    reb = p.get("totReb", 0)
                    ast = p.get("assists", 0)
                    blk = p.get("blocks", 0)
                    stl = p.get("steals", 0)
                    tpm = p.get("tpm", 0)
                    if metric == "points":
                        total = pts
                    elif metric == "rebounds":
                        total = reb
                    elif metric == "assist":
                        total = ast
                    elif metric == "pra":
                        total = pts + reb + ast
                    elif metric == "blocks":
                        total = blk
                    elif metric == "steals":
                        total = stl
                    elif metric == "3pt made":
                        total = tpm
        df.at[i, "actual"] = total
        df.at[i, "met"] = total >= row["target"]
    return df
