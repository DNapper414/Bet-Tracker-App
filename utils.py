import requests
import datetime
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players as nba_players

# Get player dictionary keyed by full name
NBA_PLAYERS = {p['full_name']: p['id'] for p in nba_players.get_players()}

def get_nba_players_for_date(date_str):
    """
    Returns a list of NBA player names who played on the given date.
    """
    date_obj = pd.to_datetime(date_str)
    player_names = []

    for player_name, player_id in NBA_PLAYERS.items():
        try:
            logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25', season_type_all_star='Regular Season').get_data_frames()[0]
            logs['GAME_DATE'] = pd.to_datetime(logs['GAME_DATE'])
            if date_obj in logs['GAME_DATE'].values:
                player_names.append(player_name)
        except Exception:
            continue  # Skip players who fail to fetch

    return sorted(player_names)

def get_nba_player_stats(name, date_str):
    """
    Returns NBA player metrics from a specific game date.
    """
    date_obj = pd.to_datetime(date_str)
    player_id = NBA_PLAYERS.get(name)

    if not player_id:
        return {}

    try:
        logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25', season_type_all_star='Regular Season').get_data_frames()[0]
        logs['GAME_DATE'] = pd.to_datetime(logs['GAME_DATE'])

        row = logs.loc[logs['GAME_DATE'] == date_obj]
        if row.empty:
            return {}

        row = row.iloc[0]
        return {
            "points": int(row["PTS"]),
            "rebounds": int(row["REB"]),
            "assist": int(row["AST"]),
            "PRA": int(row["PTS"]) + int(row["REB"]) + int(row["AST"]),
            "blocks": int(row["BLK"]),
            "steals": int(row["STL"]),
            "3pt made": int(row["FG3M"]),
        }
    except Exception:
        return {}

# Sample test
if __name__ == "__main__":
    print(get_nba_players_for_date("2025-05-24"))
    print(get_nba_player_stats("Stephen Curry", "2025-05-24"))
