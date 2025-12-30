import streamlit as st
import requests

st.set_page_config(page_title="TahminSor", layout="wide")

API_KEY = st.secrets["API_SPORTS_KEY"]

HEADERS = {
    "x-apisports-key": API_KEY
}

FOOTBALL_API = "https://v3.football.api-sports.io"
BASKET_API = "https://v1.basketball.api-sports.io"

# ================= SESSION =================
if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ================= HELPERS =================
def detect_sport(text):
    basket_words = ["lakers", "nba", "heat", "celtics", "warriors"]
    return "basket" if any(w in text.lower() for w in basket_words) else "football"

# ---------- FOOTBALL ----------
def football_team_id(name):
    r = requests.get(f"{FOOTBALL_API}/teams", headers=HEADERS, params={"search": name})
    data = r.json()["response"]
    return data[0]["team"]["id"] if data else None

def football_form(team_id):
    r = requests.get(f"{FOOTBALL_API}/fixtures", headers=HEADERS,
                     params={"team": team_id, "last": 5})
    return r.json()["response"]

# ---------- BASKET ----------
def basket_team_id(name):
    r = requests.get(f"{BASKET_API}/teams", headers=HEADERS, params={"search": name})
    data = r.json()["response"]
    return data[0]["id"] if data else None

def basket_form(team_id):
    r = requests.get(f"{BASKET_API}/games", headers=HEADERS,
                     params={"team": team_id, "last": 5})
    return r.json()["response"]

# ================= PREDICTION =================
def get_prediction(match):
    home, away = match.split("-", 1)
    home, away = home.strip(), away.strip()

    sport = detect_sport(match)

    if sport == "football":
        h_id = football_team_id(home)
        a_id = football_team_id(away)
        if not h_id or not a_id:
            return None

        h_form = football_form(h_id)
        a_form = football_form(a_id)

        h_w = sum(1 for m in h_form if m["teams"]["home"]["winner"])
        a_w = sum(1 for m in a_form if m["teams"]["away"]["winner"])

        pick = "1" if h_w > a_w else "2" if a_w > h_w else "X"
        conf = min(85, 40 + abs(h_w - a_w) * 10)

        return {
            "sport": "FUTBOL",
            "match": f"{home.title()} - {away.title()}",
            "pick": pick,
            "confidence": conf,
            "desc": "Son 5 maç form analizi"
        }

    else:
        h_id = basket_team_id(home)
        a_id = basket_team_id(away)
        if not h_id or not a_id:
            return None

        h_form = basket_form(h_id)
        a_form = basket_form(a_id)

        h_w = sum(1 for g in h_form if g["teams"]["home"]["winner"])
        a_w = sum(1 for g in a_form if g["teams"]["away"]["winner"])

        pick = "ÜST" if (h_w + a_w) >= 5 else "ALT"
        conf = min(85, 45 + abs(h_w - a_w) * 8)

        return {
            "sport": "BASKETBOL",
            "match": f"{home.title()} - {away.title()}",
            "pick": pick,
            "confidence": conf,
            "desc": "Tempo & kazanma trendi analizi"
        }

# ================= UI =================
st.title("⚽🏀 TahminSor – Gerçek API (Futbol + Basketbol)")

left, right = st.columns([2, 1])

with left:
    with st.form("form", clear_on_submit=False):
        match = st.text_input("Maç gir (örn: genk - club brugge / lakers - heat)")
        submit = st.form_submit_button("🔮 Tahmin Al")

    if submit and "-" in match:
        result = get_prediction(match)
        if result:
            st.session_state.prediction = result
            st.success("Tahmin alındı")
        else:
            st.error("❌ Veri bulunamadı")

    if st.session_state.prediction:
        p = st.session_state.prediction
        st.markdown(f"""
        <div style="background:#f8f9fa;padding:15px;border-radius:10px">
        <b>{p['match']}</b><br>
        {p['sport']}<br>
        <b>Öneri:</b> {p['pick']}<br>
        <b>Güven:</b> %{p['confidence']}<br>
        <i>{p['desc']}</i>
        </div>
        """, unsafe_allow_html=True)

    if st.button("➕ Kupona Ekle"):
        if st.session_state.prediction:
            st.session_state.kupon.append(st.session_state.prediction)
            st.success("Kupona eklendi")

with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for k in st.session_state.kupon:
            st.markdown(f"""
            <div style="background:#ffffff;padding:12px;border-radius:8px;margin-bottom:8px">
            <b>{k['match']}</b><br>
            {k['sport']} | {k['pick']} | %{k['confidence']}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon = []
            st.experimental_rerun()
