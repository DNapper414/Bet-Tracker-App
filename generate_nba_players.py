import requests
import json
import time

BALLEDONTLIE_BASE = "https://www.balldontlie.io/api/v1"

def fetch_all_nba_players():
    player_names = set()
    page = 1

    while True:
        url = f"{BALLEDONTLIE_BASE}/players?per_page=100&page={page}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            players = data.get("data", [])
            if not players:
                break

            for player in players:
                full_name = f"{player['first_name']} {player['last_name']}"
                player_names.add(full_name)

            page += 1
            time.sleep(0.2)  # be nice to API rate limit
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return sorted(player_names)

if __name__ == "__main__":
    nba_players = fetch_all_nba_players()
    with open("nba_players.json", "w") as f:
        json.dump(nba_players, f, indent=2)
    print(f"Saved {len(nba_players)} NBA players to nba_players.json")
