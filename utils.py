import requests
import datetime
from supabase_client import supabase


def evaluate_projections_mlb():
    from mlbgame import games, player_stats

    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    result = supabase.table("projections").select("*").eq("sport", "MLB").eq("date", date_str).execute()

    for proj in result.data:
        player = proj['player']
        metric = proj['metric'].lower()
        target = proj['target']

        actual = 0
        games_list = games(today.year, today.month, today.day)
        stats = player_stats(games_list)

        for team in stats:
            for p in team:
                if p.name.lower() == player.lower():
                    if metric == "hits":
                        actual = p.hit
                    elif metric == "homeruns":
                        actual = p.hr
                    elif metric == "rbi":
                        actual = p.rbi
                    elif metric == "runs":
                        actual = p.r
                    elif metric == "total bases":
                        actual = p.tb
                    elif metric == "stolen bases":
                        actual = p.sb
        met = actual >= target
        supabase.table("projections").update({"actual": actual, "met": met}).eq("id", proj["id"]).execute()


def get_nba_player_stats_rapidapi(name: str, date: str) -> int:
    import os

    RAPID_API_KEY = os.getenv("RAPIDAPI_KEY")

    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }

    query = {
        "date": date,
        "season": "2024",
        "player": name
    }

    try:
        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()
        stats = response.json().get("response", [])
        if not stats:
            print(f"[NBA] No game data for {name} on {date}")
            return 0
        total_points = sum(game.get("points", 0) for game in stats if "points" in game)
        return total_points
    except Exception as e:
        print(f"[NBA] Error fetching stats for {name} on {date}: {e}")
        return 0


def evaluate_projections_nba():
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    result = supabase.table("projections").select("*").eq("sport", "NBA").eq("date", date_str).execute()

    for proj in result.data:
        player = proj['player']
        metric = proj['metric'].lower()
        target = proj['target']

        actual = 0
        if metric == "points":
            actual = get_nba_player_stats_rapidapi(player, date_str)

        met = actual >= target
        supabase.table("projections").update({"actual": actual, "met": met}).eq("id", proj["id"]).execute()
