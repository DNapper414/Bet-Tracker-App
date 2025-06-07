# Bet Tracker App - Render.com Deployment (REST API Version)

## 🚀 Deployment Instructions

✅ This version no longer depends on supabase-py and is fully compatible with Render.com.

1️⃣ Upload this repo to GitHub.

2️⃣ In Render.com, create **New Web Service**.

3️⃣ Select **Python** language.

4️⃣ Start command:
```bash
streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```

5️⃣ Set the following environment variables:

| Variable | Value |
| -------- | ----- |
| RAPIDAPI_KEY | 47945fd24fmsh2539580c53289bdp119b78jsne5525ec5acdf |
| RAPIDAPI_HOST | api-nba-v1.p.rapidapi.com |
| SUPABASE_URL | https://dpedazmpshbufsmrnhet.supabase.co |
| SUPABASE_KEY | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |

✅ No more pip dependency conflicts 🚀