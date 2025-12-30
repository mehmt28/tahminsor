import streamlit as st
import requests
import re

# ================== CONFIG ==================
st.set_page_config(
    page_title="TahminSor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOTBALL_TEAMS = "https://v3.football.api-sports.io/teams"
FOOTBALL_FIXTURES = "https://v3.football.api-sports.io/fixtures"
FOOTBALL_PRED = "https://v3.football.api-sports.io/predictions"

BASKET_TEAMS = "https://v1.basketball.api-sports.io/teams"
BASKET_GAMES = "https://v1.basketball.api-sports.io/games"
BASKET_PRED = "https://v1.basketball.api-sports.io/predictions"

# ================== STYLE ==================
st.markdown("""
<style>
body { background:#f5f7fb; }
.card {
    background:#ffffff;
    padding:14px;
    border-radius:12px;
    margin-bottom:10px;
    box-shadow:0 2px 8px rgba(0,0,0,.08);
}
.good { color:#27ae60; font-weight:600 }
.bad { color:#c0392b; font-weight:600 }
</style>
""", unsafe_allow_html=True)

# ================== HELPERS ==================
def split_match(q):
    return [x.strip() for x in re.split("[-–]", q)]

def normalize(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower())

def detect_sport(q):
    t = normalize(q)
    basket_words = ["kgc", "thunders", "warriors", "beermen", "bullets", "breakers"]
    return "basketbol" if any(w in t for w in basket_words) else "futbol"

# ================== FOOTBALL ==================
def football_predict(match):
    home, away = split_match(match)

    team_res = requests.get(
        FOOTBALL_TEAMS,
        headers=HEADERS,
        params={"search": home}
    ).json()

    if not team_res.get("response"):
        return None

    team_id = team_res["response"][0]["team"]["id"]

    fix = requests.get(
        FOOTBALL_FIXTURES,
        headers=HEADERS,
        params={"team": team_id, "next": 1}
    ).json()

    if not fix.get("response"):
        return None

    fixture_id = fix["response"][0]["fixture"]["id"]

    pred = requests.get(
        FOOTBALL_PRED,
        headers=HEADERS,
        params={"fixture": fixture_id}
    ).json()

    if not pred.get("response"):
        return None

    perc = pred["response"][0]["predictions"]["percent"]
    home_p = int(perc["home"].replace("%", ""))
    draw_p = int(perc["draw"].replace("%", ""))
    away_p = int(perc["away"].replace("%", ""))

    best = max(
        [("Ev Sahibi", home_p), ("Beraberlik", draw_p), ("Deplasman", away_p)],
        key=lambda x: x[1]
    )

    return {
        "match": f"{home} - {away}",
        "sport": "FUTBOL",
        "pick": best[0],
        "confidence": best[1],
        "api": True
    }

# ================== BASKETBALL ==================
def basket_predict(match):
    home, away = split_match(match)

    team_res = requests.get(
        BASKET_TEAMS,
        headers=HEADERS,
        params={"search": home}
    ).json()

    if not team_res.get("response"):
        return None

    team_id = team_res["response"][0]["id"]

    games = requests.get(
        BASKET_GAMES,
        headers=HEADERS,
        params={"team": team_id, "season": 2024}
    ).json()

    if not games.get("response"):
        return None

    game_id = games["response"][0]["id"]

    pred = requests.get(
        BASKET_PRED,
        headers=HEADERS,
        params={"game": game_id}
    ).json()

    if not pred.get("response"):
        return None

    home_p = int(pred["response"][0]["percent"]["home"].replace("%", ""))
    away_p = 100 - home_p

    pick = "Ev Sahibi" if home_p > away_p else "Deplasman"

    return {
        "match": f"{home} - {away}",
        "sport": "BASKETBOL",
        "pick": pick,
        "confidence": max(home_p, away_p),
        "api": True
    }

# ================== SESSION ==================
if "son_tahmin" not in st.session_state:
    st.session_state.son_tahmin = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ================== UI ==================
st.title("⚽🏀 TahminSor – Hybrid Matcher")

left, right = st.columns([3, 1])

with left:
    q = st.text_input("Maç gir (örn: genk - club brugge)")

    c1, c2 = st.columns(2)
    with c1:
        tahmin_al = st.button("📊 Tahmin Al")
    with c2:
        kupona_ekle = st.button("🧾 Kupona Ekle")

    if tahmin_al and q:
        sport = detect_sport(q)
        data = football_predict(q) if sport == "futbol" else basket_predict(q)

        if not data:
            st.warning("❌ Veri bulunamadı (isim / lig uyuşmuyor)")
            st.session_state.son_tahmin = None
        else:
            st.session_state.son_tahmin = data

    if st.session_state.son_tahmin:
        t = st.session_state.son_tahmin
        st.markdown(f"""
        <div class="card">
        <b>{t['match']}</b><br>
        <small>{t['sport']}</small><br><br>
        <b>Öneri:</b> {t['pick']}<br>
        <b>Güven:</b> %{t['confidence']}
        </div>
        """, unsafe_allow_html=True)
        st.progress(t["confidence"] / 100)

    if kupona_ekle and st.session_state.son_tahmin:
        st.session_state.kupon.append(st.session_state.son_tahmin)
        st.success("✅ Tahmin kupona eklendi")

with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for k in st.session_state.kupon:
            st.markdown(f"""
            <div class="card">
            <b>{k['match']}</b><br>
            <small>{k['sport']}</small><br>
            <span class="good">Öneri: {k['pick']}</span><br>
            Güven: %{k['confidence']}
            </div>
            """, unsafe_allow_html=True)
