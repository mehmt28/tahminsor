import streamlit as st
import requests
import re
import random

# ================== CONFIG ==================
st.set_page_config("TahminSor | API", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOTBALL_TEAMS_API = "https://v3.football.api-sports.io/teams"
FOOTBALL_FIXTURES = "https://v3.football.api-sports.io/fixtures"
FOOTBALL_PRED = "https://v3.football.api-sports.io/predictions"

BASKET_TEAMS_API = "https://v1.basketball.api-sports.io/teams"
BASKET_GAMES = "https://v1.basketball.api-sports.io/games"
BASKET_PRED = "https://v1.basketball.api-sports.io/predictions"

# ================== STYLE ==================
st.markdown("""
<style>
body { background:#f5f7fb; }
.card { background:#fff; padding:14px; border-radius:12px; margin-bottom:10px;
box-shadow:0 2px 8px rgba(0,0,0,.08);}
.good{color:#27ae60;font-weight:600}
.bad{color:#c0392b;font-weight:600}
.bar{background:#ddd;height:8px;border-radius:6px}
.fill{background:#27ae60;height:8px;border-radius:6px}
</style>
""", unsafe_allow_html=True)

# ================== HELPERS ==================
def normalize(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()

def split_match(q):
    return [x.strip() for x in re.split("[-–]", q)]

def detect_sport(q):
    t = normalize(q)
    return "basketbol" if any(x in t for x in ["warriors","beermen","kgc","thunders"]) else "futbol"

def confidence_bar(p):
    return f'<div class="bar"><div class="fill" style="width:{p}%"></div></div>'

# ================== FOOTBALL ==================
def football_predict(match):
    home, away = split_match(match)

    # TEAM SEARCH
    t = requests.get(FOOTBALL_TEAMS_API, headers=HEADERS,
                     params={"search": home}).json()

    if not t["response"]:
        return None

    home_id = t["response"][0]["team"]["id"]

    # NEXT FIXTURE
    f = requests.get(FOOTBALL_FIXTURES, headers=HEADERS,
                     params={"team": home_id, "next": 1}).json()

    if not f["response"]:
        return None

    fix_id = f["response"][0]["fixture"]["id"]

    # PREDICTION
    p = requests.get(FOOTBALL_PRED, headers=HEADERS,
                     params={"fixture": fix_id}).json()

    if not p["response"]:
        return None

    pr = p["response"][0]["predictions"]["percent"]
    h = int(pr["home"].replace("%",""))
    d = int(pr["draw"].replace("%",""))
    a = int(pr["away"].replace("%",""))

    pick = max(
        [("Ev Sahibi",h),("Beraberlik",d),("Deplasman",a)],
        key=lambda x:x[1]
    )

    return {
        "match": f"{home} - {away}",
        "pick": pick[0],
        "conf": pick[1],
        "sport": "futbol",
        "ok": True
    }

# ================== BASKETBALL ==================
def basket_predict(match):
    home, away = split_match(match)

    t = requests.get(BASKET_TEAMS_API, headers=HEADERS,
                     params={"search": home}).json()

    if not t["response"]:
        return None

    home_id = t["response"][0]["id"]

    g = requests.get(BASKET_GAMES, headers=HEADERS,
                     params={"team": home_id, "season": 2024}).json()

    if not g["response"]:
        return None

    game_id = g["response"][0]["id"]

    p = requests.get(BASKET_PRED, headers=HEADERS,
                     params={"game": game_id}).json()

    if not p["response"]:
        return None

    pr = p["response"][0]["percent"]
    h = int(pr["home"].replace("%",""))
    a = 100 - h

    pick = "Ev Sahibi" if h > a else "Deplasman"

    return {
        "match": f"{home} - {away}",
        "pick": pick,
        "conf": max(h,a),
        "sport": "basketbol",
        "ok": True
    }

# ================== SESSION ==================
if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ================== UI ==================
st.title("⚽🏀 TahminSor – Gerçek API")

left,right = st.columns([2,1])

with left:
    q = st.text_input("Maç gir (örn: genk - club brugge)")

    if st.button("Kupona Ekle"):
        try:
            sport = detect_sport(q)
            data = football_predict(q) if sport=="futbol" else basket_predict(q)

            if not data:
                data = {
                    "match": q,
                    "pick": "—",
                    "conf": random.randint(35,45),
                    "sport": sport,
                    "ok": False
                }

            st.session_state.kupon.append(data)

        except:
            st.warning("Format: takım1 - takım2")

with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for k in st.session_state.kupon:
            st.markdown(f"""
            <div class="card">
            <b>{k['match']}</b><br>
            <small>{k['sport'].upper()}</small><br>
            <span class="{ 'good' if k['ok'] else 'bad' }">
            {"🟢 API Verisi" if k['ok'] else "⚠ Tahmini/Fallback"}
            </span><br><br>
            <b>Öneri:</b> {k['pick']}<br>
            <small>Güven: %{k['conf']}</small>
            {confidence_bar(k['conf'])}
            </div>
            """, unsafe_allow_html=True)
