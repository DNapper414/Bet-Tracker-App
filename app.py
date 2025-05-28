import streamlit as st
import pandas as pd
from datetime import date
from utils import (
    get_players_for_date,
    METRICS_BY_SPORT,
    evaluate_projection,
    add_projection,
    remove_projection,
    get_projections
)

# Initial state
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

st.title("📊 Sports Projection Tracker")

sport = st.selectbox("Select Sport", ["MLB", "NBA"])
selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

players = get_players_for_date(sport, selected_date)
player = st.selectbox("Choose a Player", players)
metric = st.selectbox("Select Metric", METRICS_BY_SPORT[sport])
target = st.number_input("Enter Target", step=1)

if st.button("Add to Tracker"):
    data = {
        "user_id": "guest",
        "player": player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": str(selected_date),
        "sport": sport
    }
    add_projection(data)

st.markdown("### 🎯 Your Projections")
projections = get_projections("guest")
table = []

for proj in projections:
    actual, met = evaluate_projection(proj)
    table.append({
        "Player": proj["player"],
        "Metric": proj["metric"],
        "Target": proj["target"],
        "Actual": actual,
        "Met": "✅" if met else "❌",
        "Date": proj["date"],
        "Remove": f"Remove_{proj['id']}"
    })

df = pd.DataFrame(table)

if not df.empty:
    st.dataframe(df.drop(columns="Remove"))
    for proj in projections:
        if st.button("❌ Remove", key=f"remove_{proj['id']}"):
            remove_projection("guest", proj["id"])
            st.experimental_rerun()

if st.button("🔁 Reset Table"):
    for proj in projections:
        remove_projection("guest", proj["id"])
    st.experimental_rerun()
