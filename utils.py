def calculate_nba_metric(statistics, metric):
    if not statistics:
        return 0
    
    if metric == "points":
        return statistics.get("points", 0)
    elif metric == "rebounds":
        return statistics.get("totReb", 0)
    elif metric == "assist":
        return statistics.get("assists", 0)
    elif metric == "PRA":
        return (statistics.get("points", 0) +
                statistics.get("totReb", 0) +
                statistics.get("assists", 0))
    elif metric == "blocks":
        return statistics.get("blocks", 0)
    elif metric == "steals":
        return statistics.get("steals", 0)
    elif metric == "3pt made":
        return statistics.get("tpm", 0)
    return 0