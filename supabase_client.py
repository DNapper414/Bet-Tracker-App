import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_projection(projection):
    data = supabase.table("projections").insert(projection).execute()
    return data

def fetch_projections():
    data = supabase.table("projections").select("*").execute()
    return data.data

def clear_projections():
    supabase.table("projections").delete().neq("id", 0).execute()

def update_projection(id, actual, hit):
    supabase.table("projections").update({"actual": actual, "hit": hit}).eq("id", id).execute()