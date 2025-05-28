import statsapi
import requests
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2

def get_mlb_players_for_date(game_date):
    try:
        games = statsapi.schedule(start_date=game_date, end_date=game_date)
        players = set()
        for game in games:
            box = statsapi.boxscore_data(game['game_id'])
            for team in ['home', 'away']:
                for pid, pdata in box[team]['players'].items():
                    players.add(pdata['person']['fullName'])
        return sorted(players)
    except Exception:
        return []

def get_nba_players_for_date(game_date):
    try:
        date_str = datetime.strptime(game_date, "%Y-%m-%d").strftime('%Y%m%d')
        scoreboard = scoreboardv2.ScoreboardV2(game_date=date_str)
        game_ids = scoreboard.game_header.get_data_frame()['GAME_ID'].tolist()
        players = set()
        for gid in game_ids:
            boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=gid)
            stats_df = boxscore.player_stats.get_data_frame()
            stats_df = stats_df[stats_df['MIN'].notnull()]
            players.update(stats_df['PLAYER_NAME'].tolist())
        return sorted(players)
    except Exception:
        return []

def get_players_for_date(sport, game_date):
    if sport == 'MLB':
        return get_mlb_players_for_date(game_date)
    elif sport == 'NBA':
        return get_nba_players_for_date(game_date)
    return []
