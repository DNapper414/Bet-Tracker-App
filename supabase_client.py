from supabase import create_client

# ✅ Supabase credentials (from original)
SUPABASE_URL = "https://dpedazmpshbufsmrnhet.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRwZWRhem1wc2hidWZzbXJuaGV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwOTMyODUsImV4cCI6MjA2MzY2OTI4NX0.ldE4FNtnCHzfNVDBYSqPLVxX0m4OAQFZrS-bE1mEirk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_projections(user_id):
    return supabase.table("projections").select("*").eq("user_id", user_id).execute()

def add_projection(data):
    return supabase.table("projections").insert(data).execute()

def remove_projection(user_id, proj_id):
    return supabase.table("projections").delete().eq("user_id", user_id).eq("id", proj_id).execute()

def update_projection_result(proj_id, actual, met):
    return supabase.table("projections").update({
        "actual": actual,
        "met": met
    }).eq("id", proj_id).execute()