import json, os

CACHE_FILE = "nba_cache.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_cached_players(date):
    cache = load_cache()
    return cache.get(date, {})

def update_cache(date, players):
    cache = load_cache()
    cache[date] = players
    save_cache(cache)