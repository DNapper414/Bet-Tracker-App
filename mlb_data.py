MLB_PLAYERS = {
    "Aaron Judge": {"hits": 2, "homeruns": 1, "RBI": 3, "runs": 2, "Total Bases": 5, "stolen bases": 0},
    "Mookie Betts": {"hits": 1, "homeruns": 0, "RBI": 1, "runs": 1, "Total Bases": 2, "stolen bases": 1}
}

MLB_METRICS = ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"]

def get_mlb_players():
    return list(MLB_PLAYERS.keys())

def get_mlb_player_stat(player, metric):
    return MLB_PLAYERS[player].get(metric, 0)