import requests
import datetime

# Metrics by sport
METRICS_BY_SPORT = {
    "NBA": ["points", "rebounds", "assist", "PRA", "blocks", "steals", "3pt made"],
    "MLB": ["hits", "homeruns", "RBI", "runs", "Total Bases", "stolen bases"],
}

def get_players_for_date(sport: str, date: datetime.date):
    """Return list of player names active on a given date."""
    if sport == "NBA":
        return get_nba_players(date)
    elif sport == "MLB":
        return get_mlb_players(date)
    return []

def evaluate_projection(row):
    """Fetch actual metric value for a player and return result"""
    sport = row.get("sport")
    if sport == "NBA":
        return get_nba_actual(row)
    elif sport == "MLB":
        return get_mlb_actual(row)
    return None

# --- NBA HANDLING ---

def get_nba_players(date: datetime.date):
    """Return list of NBA player names from that day."""
    url = f"https://www.balldontlie.io/api/v1/games?dates[]={date}&per_page=100"
    players_url = "https://www.balldontlie.io/api/v1/players?per_page=100"
    try:
        player_names = set()
        page = 1
        while True:
            resp = requests.get(players_url + f"&page={page}")
            data = resp.json()
            for p in data["data"]:
                player_names.add(f"{p['first_name']} {p['last_name']}")
            if not data["meta"]["next_page"]:
                break
            page += 1
        return sorted(list(player_names))
    except Exception:
        return []

def get_nba_actual(row):
    """Return actual NBA stat for player/metric/date"""
    name = row.get("player", "")
    metric = row.get("metric", "").lower()
    date = row.get("date", "")
    if not name or not date:
        return None

    first_name, last_name = name.split(" ", 1)
    player_search_url = f"https://www.balldontlie.io/api/v1/players?search={last_name}"
    try:
        players = requests.get(player_search_url).json()["data"]
        player = next((p for p in players if p["first_name"].lower() == first_name.lower()), None)
        if not player:
            return None
        player_id = player["id"]

        stats_url = f"https://www.balldontlie.io/api/v1/stats?player_ids[]={player_id}&dates[]={date}"
        stat_data = requests.get(stats_url).json()["data"]
        if not stat_data:
            return 0

        stats = stat_data[0]["stats"]
        if metric == "points":
            return stats.get("pts", 0)
        elif metric == "rebounds":
            return stats.get("reb", 0)
        elif metric == "assist":
            return stats.get("ast", 0)
        elif metric == "blocks":
            return stats.get("blk", 0)
        elif metric == "steals":
            return stats.get("stl", 0)
        elif metric == "3pt made":
            return stats.get("fg3m", 0)
        elif metric == "PRA":
            return stats.get("pts", 0) + stats.get("reb", 0) + stats.get("ast", 0)
        return 0
    except Exception:
        return 0

# --- MLB HANDLING ---

def get_mlb_players(date: datetime.date):
    """Hardcoded MLB players list fallback."""
    return ["Aaron Judge", "Mookie Betts", "Shohei Ohtani", "Mike Trout", "Ronald Acuña Jr."]

def get_mlb_actual(row):
    """Return actual MLB stat for player/metric/date"""
    # Placeholder or use statsapi or similar service if deployed
    # For now, fake mock values
    metric = row.get("metric", "").lower()
    player = row.get("player", "").lower()
    date = row.get("date", "")

    # Replace with real lookup
    mock_stats = {
        "hits": 2,
        "homeruns": 1,
        "rbi": 3,
        "runs": 2,
        "total bases": 4,
        "stolen bases": 1,
    }
    return mock_stats.get(metric, 0)
