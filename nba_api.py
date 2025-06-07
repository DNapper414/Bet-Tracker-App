import streamlit as st
import requests

RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
RAPIDAPI_HOST = st.secrets["RAPIDAPI_HOST"]
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
}
BASE_URL = f"https://{RAPIDAPI_HOST}"

def fetch_nba_games(date):
    url = f"{BASE_URL}/games/date/{date}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()['response']

def fetch_nba_players_by_game(date):
    games = fetch_nba_games(date)
    players = {}
    for game in games:
        for team_key in ['home', 'away']:
            team_id = game['teams'][team_key]['id']
            url = f"{BASE_URL}/players?team={team_id}&season=2023"
            res = requests.get(url, headers=HEADERS)
            res.raise_for_status()
            for player in res.json()['response']:
                players[player['id']] = player['firstname'] + " " + player['lastname']
    return players

def fetch_nba_player_statistics(game_id, player_id):
    url = f"{BASE_URL}/players/statistics?game={game_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    stats = response.json()['response']
    for stat in stats:
        if stat['player']['id'] == player_id:
            return stat['statistics']
    return None