import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_client import supabase
from utils import (
    get_players_for_date,
    get_metrics_for_sport,
    evaluate_projection,
    METRICS_BY_SPORT
)

st.set_page_config(page_title="Bet Tracker App", layout="wide")

# Persistent selected date
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.today().date()

st.title("📊 Sports Projection Tracker")

selected_date = st.date_input("Select Game Date", value=st.session_state.selected_date)
st.session_state.selected_date = selected_date

# Sport selection
sport = st.selectbox("Choose Sport", options=["MLB", "NBA"])

# Pull players dynamically
players = get_players_for_date(sport.lower(), selected_date.strftime("%Y-%m-%d"))
player_name = st.selectbox("Select Player", players)

# Metric selection
metric = st.selectbox("Select Metric", options=get_metrics_for_sport(sport))

# Target entry
target = st.number_input("Enter Target", min_value=0, value=1)

if st.button("Add to Tracker"):
    supabase.table("projections").insert({
        "player": player_name,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.isoformat(),
        "sport": sport,
        "user_id": "guest"
    }).execute()
    st.success("Player added to tracker.")

# Reset button
if st.button("Reset Table"):
    supabase.table("projections").delete().eq("user_id", "guest").execute()
    st.warning("Table reset.")

# Display tracked projections
projections = supabase.table("projections").select("*").eq("user_id", "guest").order("id", desc=False).execute()
df = pd.DataFrame(projections.data)

if not df.empty:
    # Evaluate actual stats
    df = df.apply(evaluate_projection, axis=1)

    # Show table with remove buttons
    st.subheader("📋 Results")
    for index, row in df.iterrows():
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
        col1.write(row["player"])
        col2.write(row["metric"])
        col3.write(row["target"])
        col4.write(row["actual"] if row["actual"] is not None else "N/A")
        col5.write("✅" if row["met"] else "❌" if row["met"] is not None else "—")
        col6.write(row["sport"])
        col7.write(row["date"])
        if col8.button("Remove", key=f"remove_{row['id']}"):
            supabase.table("projections").delete().eq("id", row["id"]).execute()
            st.experimental_rerun()
else:
    st.info("No players being tracked yet.")
