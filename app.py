import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    get_players_for_date,
    evaluate_projection,
    METRICS_BY_SPORT
)
from supabase_client import (
    add_projection,
    get_projections,
    remove_projection,
    update_projection_result
)

st.set_page_config(page_title="Bet Tracker App", layout="centered")

# --- SESSION STATE INIT ---
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()

if "sport" not in st.session_state:
    st.session_state.sport = "MLB"

# --- HEADER ---
st.title("📊 Bet Tracker App")
st.write("Track your projections by sport, player, and metric.")

# --- SPORT SELECTION ---
st.session_state.sport = st.selectbox("Select Sport", ["MLB", "NBA"], index=["MLB", "NBA"].index(st.session_state.sport))

# --- DATE SELECTION ---
selected_date = st.date_input("Select Game Date", value=pd.to_datetime(st.session_state.selected_date))
st.session_state.selected_date = selected_date.date()

# --- PLAYER SEARCH ---
players = get_players_for_date(st.session_state.sport, st.session_state.selected_date)
selected_player = st.selectbox("Select Player", options=players)

# --- METRIC AND TARGET ---
metric = st.selectbox("Select Metric", METRICS_BY_SPORT[st.session_state.sport])
target = st.number_input("Enter Target", min_value=0.0, value=1.0, step=0.5)

# --- ADD PROJECTION ---
if st.button("➕ Add to Tracker"):
    if selected_player:
        data = {
            "user_id": "guest",
            "player": selected_player,
            "metric": metric,
            "target": target,
            "actual": None,
            "met": None,
            "date": st.session_state.selected_date.isoformat(),
            "sport": st.session_state.sport
        }
        add_projection(data)
        st.success(f"✅ Added {selected_player} - {metric} to tracker")

# --- RESET TRACKER ---
if st.button("🗑️ Reset Tracker"):
    projections = get_projections("guest")
    for p in projections.data:
        remove_projection("guest", p["id"])
    st.success("Tracker has been reset.")

# --- GET PROJECTIONS ---
projections = get_projections("guest")
if projections and projections.data:
    st.subheader("📋 Tracked Projections")
    df = pd.DataFrame(projections.data)

    # --- Evaluate and Update ---
    for i, row in df.iterrows():
        if row["actual"] is None:
            actual = evaluate_projection(row["player"], row["metric"], row["date"], row["sport"])
            met = actual >= row["target"] if actual is not None else None
            update_projection_result(row["id"], actual, met)
            df.at[i, "actual"] = actual
            df.at[i, "met"] = met

    # --- Format Display ---
    df["Result"] = df["met"].apply(lambda x: "✅" if x else "❌" if x is False else "⏳")
    df_display = df[["player", "metric", "target", "actual", "Result"]]

    # --- Remove Button ---
    for i, row in df.iterrows():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(df_display.iloc[i])
        with col2:
            if st.button("❌ Remove", key=f"remove_{row['id']}"):
                remove_projection("guest", row["id"])
                st.rerun()

else:
    st.info("Add a player to start tracking results.")
