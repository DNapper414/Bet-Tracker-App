import os
from supabase import create_client, Client
import streamlit as st

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        st.error(f"❌ Environment variable {name} is not set.")
        raise RuntimeError(f"{name} is required")
    return value

try:
    SUPABASE_URL = get_env_var("SUPABASE_URL")
    SUPABASE_KEY = get_env_var("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize Supabase client: {e}")
    supabase = None

def get_projections(user_id):
    if not supabase:
        return []
    try:
        return supabase.table("projections").select("*").eq("user_id", user_id).execute()
    except Exception as e:
        st.error(f"❌ get_projections failed: {e}")
        return []

def add_projection(data):
    if not supabase:
        return []
    try:
        return supabase.table("projections").insert(data).execute()
    except Exception as e:
        st.error(f"❌ add_projection failed: {e}")
        return []

def remove_projection(user_id, proj_id):
    if not supabase:
        return []
    try:
        return supabase.table("projections").delete().eq("user_id", user_id).eq("id", proj_id).execute()
    except Exception as e:
        st.error(f"❌ remove_projection failed: {e}")
        return []

def update_projection_result(proj_id, actual, met):
    if not supabase:
        return []
    try:
        return supabase.table("projections").update({"actual": actual, "met": met}).eq("id", proj_id).execute()
    except Exception as e:
        st.error(f"❌ update_projection_result failed: {e}")
        return []
