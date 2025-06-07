import requests
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_TABLE = "projections"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def insert_projection(projection):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    response = requests.post(url, headers=HEADERS, json=projection)
    response.raise_for_status()
    return response.json()

def fetch_projections():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=*"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def clear_projections():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?id=neq.0"
    response = requests.delete(url, headers=HEADERS)
    response.raise_for_status()

def update_projection(id, actual, hit):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?id=eq.{id}"
    payload = {"actual": actual, "hit": hit}
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()