import streamlit as st
from utils import (
    get_players_for_date,
    METRICS_BY_SPORT,
    evaluate_projection,
)
from supabase_client import (
    get_projections,
    add_projection,
    remove_projection,
    update_projection_result,
)
import datetime
import pandas as pd

st.set_page_config(page_title="Bet Tracker", layout="wide")

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()

selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

selected_sport = st.selectbox("Select Sport", ["MLB", "NBA"])
players = get_players_for_date(selected_date, selected_sport)

selected_player = st.selectbox("Select Player", players)
selected_metric = st.selectbox("Select Metric", METRICS_BY_SPORT[selected_sport])
target = st.number_input("Enter Target Value", min_value=0)

if st.button("Add to Tracker"):
    data = {
        "player": selected_player,
        "metric": selected_metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.isoformat(),
        "sport": selected_sport,
        "user_id": "guest"
    }
    add_projection(data)
    st.success("✅ Player added.")

if st.button("Reset Table"):
    for p in get_projections("guest").data:
        remove_projection("guest", p["id"])
    st.success("🧹 Table cleared.")

# Show table
projections = get_projections("guest").data
if projections:
    for proj in projections:
        if proj["actual"] is None:
            result = evaluate_projection(proj)
            if result is not None:
                update_projection_result(proj["id"], result["actual"], result["met"])

    df = pd.DataFrame(get_projections("guest").data)
    df["Status"] = df["met"].apply(lambda x: "✅" if x else "❌" if x is not None else "")
    df_display = df[["player", "metric", "target", "actual", "Status", "date", "sport"]]
    st.dataframe(df_display)

    for proj in projections:
        if st.button(f"Remove {proj['player']}", key=f"remove_{proj['id']}"):
            remove_projection("guest", proj["id"])
            st.experimental_rerun()
