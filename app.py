import streamlit as st
import pandas as pd
from datetime import date
from utils import get_mlb_players_for_date, get_nba_players_for_date, METRICS_BY_SPORT

st.set_page_config("📊 Bet Tracker", layout="centered")

st.title("📊 Bet Tracker")

# Persist selected date across sessions
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

sport = st.selectbox("Select Sport", ["MLB", "NBA"])
selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

# Get autocompletion players by sport
if sport == "MLB":
    player_list = get_mlb_players_for_date(str(selected_date))
elif sport == "NBA":
    player_list = get_nba_players_for_date(str(selected_date))
else:
    player_list = []

player = st.selectbox("Select Player", player_list)
metric = st.selectbox("Select Metric", METRICS_BY_SPORT[sport])
target = st.number_input("Set Target", step=1)

if st.button("Add to Tracker"):
    st.success(f"✅ Added {player} - {metric} ≥ {target} on {selected_date}")
