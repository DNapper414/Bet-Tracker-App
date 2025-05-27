import requests
import time
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2

def fetch_boxscore(game_id):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
    try:
        response = requests.get(url, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def evaluate_projections(projections_df, boxscores):
    results = []
    for _, row in projections_df.iterrows():
        name = row["player"].strip().lower()
        metric = row["metric"]
        target = row["target"]
        actual = 0
        found = False

        for box in boxscores:
            for team in ["home", "away"]:
                team_players = box["teams"][team]["players"]
                for pdata in team_players.values():
                    pname = pdata["person"]["fullName"].strip().lower()
                    if name == pname or name in pname or pname in name:
                        stats = pdata.get("stats", {}).get("batting", {})
                        if metric in stats:
                            actual = stats[metric]
                            found = True
                        break
                if found:
                    break
            if found:
                break

        results.append({
            "player": row["player"],
            "metric": metric,
            "target": target,
            "actual": actual if found else None,
            "met": actual >= target if found else False
        })
    return results

def evaluate_projections_nba_nbaapi(projections_df, date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    game_ids = scoreboardv2.ScoreboardV2(game_date=date_obj.strftime("%m/%d/%Y")).game_header.get_data_frame()["GAME_ID"]
    results = []

    for _, row in projections_df.iterrows():
        name = row["player"].strip().lower()
        metric = row["metric"]
        target = row["target"]
        actual = 0
        found = False

        for gid in game_ids:
            time.sleep(0.6)  # prevent rate limiting
            df = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=gid).player_stats.get_data_frame()
            for _, p in df.iterrows():
                pname = p["PLAYER_NAME"].strip().lower()
                if name == pname or name in pname or pname in name:
                    found = True
                    if metric == "PRA":
                        actual = p.get("PTS", 0) + p.get("REB", 0) + p.get("AST", 0)
                    elif metric == "3pts made":
                        actual = p.get("FG3M", 0)
                    else:
                        actual = p.get(metric.upper(), 0)
                    break
            if found:
                break

        results.append({
            "player": row["player"],
            "metric": metric,
            "target": target,
            "actual": actual if found else None,
            "met": actual >= target if found else False
        })

    return results

def get_mlb_players_today(date_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    games = requests.get(url).json().get("dates", [])
    ids = [g["gamePk"] for d in games for g in d.get("games", [])]
    players = set()
    for gid in ids:
        box = fetch_boxscore(gid)
        if box:
            for t in ["home", "away"]:
                for p in box["teams"][t]["players"].values():
                    players.add(p["person"]["fullName"])
    return sorted(players)

def get_nba_players_today(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    game_ids = scoreboardv2.ScoreboardV2(game_date=date_obj.strftime("%m/%d/%Y")).game_header.get_data_frame()["GAME_ID"]
    players = set()
    for gid in game_ids:
        df = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=gid).player_stats.get_data_frame()
        players.update(df["PLAYER_NAME"])
    return sorted(players)
