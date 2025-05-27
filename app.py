import streamlit as st
from datetime import date
from utils import evaluate_projections_mlb, evaluate_projections_nba
from supabase_client import get_projections, add_projection, remove_projection, update_projection_result

st.set_page_config(page_title="Player Projections Tracker", layout="centered")

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today().strftime("%Y-%m-%d")

st.title("Player Projections Tracker")
st.caption("Track your MLB and NBA player performance projections.")

sport = st.selectbox("Select Sport", ["MLB", "NBA"])
player = st.text_input("Enter Player Name")
metric = st.selectbox("Select Metric", ["hits"] if sport == "MLB" else ["points"])
target = st.number_input("Enter Target Value", min_value=0, step=1)
selected_date = st.date_input("Select Game Date", value=pd.to_datetime(st.session_state.selected_date))
user_id = "guest"

if st.button("Add to Tracker"):
    if player:
        data = {
            "player": player,
            "metric": metric,
            "target": target,
            "actual": None,
            "met": None,
            "date": selected_date.strftime("%Y-%m-%d"),
            "sport": sport,
            "user_id": user_id,
        }
        add_projection(data)
        st.success("Added to tracker!")

if st.button("Reset Table"):
    all_projections = get_projections(user_id)
    for p in all_projections.data:
        remove_projection(user_id, p["id"])
    st.success("Table cleared!")

projections = get_projections(user_id)
rows = projections.data if projections else []

mlb_rows = [p for p in rows if p["sport"] == "MLB"]
nba_rows = [p for p in rows if p["sport"] == "NBA"]

evaluate_projections_mlb(mlb_rows)
evaluate_projections_nba(nba_rows)

for p in mlb_rows + nba_rows:
    if p["actual"] is not None:
        update_projection_result(p["id"], p["actual"], p["met"])

if rows:
    st.subheader("Your Projections")
    for p in rows:
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            st.write(p["player"])
        with col2:
            st.write(p["metric"])
        with col3:
            st.write(p["target"])
        with col4:
            st.write(p["actual"] if p["actual"] is not None else "-")
        with col5:
            st.markdown("✅" if p["met"] else "❌" if p["met"] is not None else "-")
        with col6:
            st.write(p["date"])
        with col7:
            if st.button("Remove", key=f"remove_{p['id']}"):
                remove_projection(user_id, p["id"])
                st.rerun()
