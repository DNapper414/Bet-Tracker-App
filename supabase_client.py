import os
import sys
from supabase import create_client, Client

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"❌ Environment variable {name} is not set.", file=sys.stderr)
        raise RuntimeError(f"{name} is required")
    return value

try:
    SUPABASE_URL = get_env_var("SUPABASE_URL")
    SUPABASE_KEY = get_env_var("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}", file=sys.stderr)
    supabase = None

def get_projections(user_id):
    if not supabase: return []
    return supabase.table("projections").select("*").eq("user_id", user_id).execute()

def add_projection(data):
    if not supabase: return []
    return supabase.table("projections").insert(data).execute()

def remove_projection(user_id, proj_id):
    if not supabase: return []
    return supabase.table("projections").delete().eq("user_id", user_id).eq("id", proj_id).execute()

def update_projection_result(proj_id, actual, met):
    if not supabase: return []
    return supabase.table("projections").update({
        "actual": actual,
        "met": met
    }).eq("id", proj_id).execute()
