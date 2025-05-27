import streamlit as st
from datetime import date
import pandas as pd
from supabase_client import get_projections, add_projection, remove_projection, update_projection_result
from utils import evaluate_projections_mlb, evaluate_projections_nba

st.set_page_config(page_title="Bet Tracker", layout="wide")
st.title("📊 Bet Tracker App")

def get_default_date():
    return st.session_state.get("selected_date", date.today())

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

selected_date = st.date_input("Select Game Date", value=pd.to_datetime(st.session_state.selected_date))
st.session_state.selected_date = selected_date

sport = st.radio("Select Sport", ["MLB", "NBA"], horizontal=True)

# Player lists
def load_mlb_players():
    try:
        df = pd.read_csv("sample_projections.csv")
        return sorted(df["player"].dropna().unique())
    except:
        return []

def load_nba_players():
    return [
        "LeBron James", "Stephen Curry", "Luka Doncic", "Jayson Tatum",
        "Shai Gilgeous-Alexander", "Giannis Antetokounmpo", "Alex Caruso"
    ]

player_list = load_mlb_players() if sport == "MLB" else load_nba_players()

with st.form("add_form"):
    player = st.selectbox("Select Player", player_list)
    metric = st.selectbox("Metric", ["points", "rebounds", "assists"] if sport == "NBA" else ["hits", "runs", "home_runs"])
    target = st.number_input("Target", min_value=0.0, step=0.5)
    submit = st.form_submit_button("Add to Table")

if submit and player and metric and target:
    new_proj = {
        "player": player,
        "metric": metric,
        "target": target,
        "actual": None,
        "met": None,
        "date": selected_date.strftime("%Y-%m-%d"),
        "sport": sport,
        "user_id": "guest"
    }
    add_projection(new_proj)
    st.success("Added successfully!")

if st.button("Reset Table"):
    projections = get_projections("guest")
    for row in projections.data:
        remove_projection("guest", row["id"])
    st.success("Table cleared.")

if st.button("Evaluate Results"):
    projections = get_projections("guest")
    rows = projections.data if projections else []
    evaluate_projections_mlb(rows)
    evaluate_projections_nba(rows)
    st.success("Evaluated actual results.")

# Results table (MLB + NBA filtered by date)
projections = get_projections("guest")
rows = projections.data if projections else []

if rows:
    df = pd.DataFrame(rows)
    df = df[df["date"] == selected_date.strftime("%Y-%m-%d")]
    df = df.sort_values("player")

    def display_status(met):
        return "✅" if met else ("❌" if met is not None else "")

    df["Status"] = df["met"].apply(display_status)
    df["Remove"] = df["id"].apply(lambda i: f"Remove-{i}")

    display_df = df[["player", "metric", "target", "actual", "Status"]]
    st.dataframe(display_df.rename(columns={
        "player": "Player", "metric": "Metric", "target": "Target",
        "actual": "Actual", "Status": "Result"
    }), use_container_width=True)

    for row in df.itertuples():
        if st.button("Remove", key=row.id):
            remove_projection("guest", row.id)
            st.experimental_rerun()
