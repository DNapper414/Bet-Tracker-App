# Bet Tracker App - Streamlit Cloud Deployment

## Quick Deployment Instructions

1. Create a free Streamlit Cloud account: https://streamlit.io/cloud
2. Create a new app and connect it to this repository.
3. Make sure `requirements.txt` is present (already included).
4. Set environment variables in Streamlit Cloud UI:
   - `RAPIDAPI_KEY` = your RapidAPI key
   - `RAPIDAPI_HOST` = api-nba-v1.p.rapidapi.com
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase API key

5. Deploy!

Streamlit Cloud will automatically detect and run `main.py` as entry point.

Enjoy 🚀