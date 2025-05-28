import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_client import supabase
from utils import (
    get_players_for_date,
    METRICS_BY_SPORT,
    evaluate_projection
)

# Streamlit page setup
st.set_page_config(page_title="Bet Tracker App", layout="wide")

# Session state init
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()
if "tracker_data" not in st.session_state:
    st.session_state.tracker_data = pd.DataFrame(columns=[
        "Player", "Metric", "Target", "Actual", "Met", "Date", "Sport", "User"
    ])

# Title
st.title("📊 Sports Bet Tracker")

# Sidebar controls
selected_sport = st.selectbox("Select Sport", ["MLB", "NBA"])
selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

# Dynamic player list based on sport and date
players = get_players_for_date(selected_sport, selected_date.strftime("%Y-%m-%d"))

# Input form
with st.form("add_projection_form"):
    player = st.selectbox("Player", players)
    metric = st.selectbox("Metric", METRICS_BY_SPORT[selected_sport])
    target = st.number_input("Target", min_value=0.0, step=0.5)
    user_id = st.text_input("User ID", value="guest")
    submit = st.form_submit_button("Add to Tracker")

    if submit:
        new_entry = {
            "Player": player,
            "Metric": metric,
            "Target": target,
            "Actual": None,
            "Met": None,
            "Date": selected_date.strftime("%Y-%m-%d"),
            "Sport": selected_sport,
            "User": user_id
        }
        st.session_state.tracker_data = pd.concat(
            [st.session_state.tracker_data, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        st.success("Player added to tracker.")

# Evaluate Projections Button
if st.button("Evaluate Projections"):
    updated_rows = []
    for i, row in st.session_state.tracker_data.iterrows():
        actual, met = evaluate_projection(row["Sport"], row["Player"], row["Metric"], row["Date"])
        st.session_state.tracker_data.at[i, "Actual"] = actual
        st.session_state.tracker_data.at[i, "Met"] = met
        updated_rows.append(i)
    if updated_rows:
        st.success("Projections evaluated.")

# Reset and Remove Buttons
if st.button("Reset Tracker Table"):
    st.session_state.tracker_data = pd.DataFrame(columns=st.session_state.tracker_data.columns)

# Display Table
if not st.session_state.tracker_data.empty:
    st.dataframe(st.session_state.tracker_data)

# Save to Supabase (optional)
if st.button("Save Results to Supabase"):
    for _, row in st.session_state.tracker_data.iterrows():
        supabase.table("projections").insert({
            "player": row["Player"],
            "metric": row["Metric"],
            "target": row["Target"],
            "actual": row["Actual"],
            "met": row["Met"],
            "date": row["Date"],
            "sport": row["Sport"],
            "user_id": row["User"]
        }).execute()
    st.success("Results saved to Supabase.")
