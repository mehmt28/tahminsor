import streamlit as st
import requests

st.set_page_config(page_title="TahminSor", layout="wide")

API_KEY = st.secrets["API_SPORTS_KEY"]
HEADERS = {"x-apisports-key": API_KEY}

FOOTBALL_API = "https://v3.football.api-sports.io"
BASKET_API = "https://v1.basketball.api-sports.io"

# ================= STATE =================
if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ================= HELPERS =================
def detect_sport(text):
    basket_words = [
        "nba", "lakers", "heat", "celtics", "warriors",
        "bulls", "bucks", "nuggets", "suns"
    ]
    return "basket" if any(w in text.lower() for w in basket_words) else "football"

# ================= FOOTBALL =================
def football_team_id(name):
    r = requests.get(f"{FOOTBALL_API}/teams", headers=HEADERS, params={"search": name})
    data = r.json().get("response", [])
    return data[0]["team"]["id"] if data else None

def football_fixture(home_id, away_id):
    r = requests.get(
        f"{FOOTBALL_API}/fixtures",
        headers=HEADERS,
        params={"team": home_id, "next": 10}
    )
    fixtures = r.json().get("response", [])
    for f in fixtures:
        if f["teams"]["away"]["id"] == away_id:
            return f
    return None

def football_form(team_id):
    r = requests.get(
        f"{FOOTBALL_API}/fixtures",
        headers=HEADERS,
        params={"team": team_id, "last": 5}
    )
    return r.json().get("response", [])

# ================= BASKET =================
def basket_team_id(name):
    r = requests.get(f"{BASKET_API}/teams", headers=HEADERS, params={"search": name})
    data = r.json().get("response", [])
    return data[0]["id"] if data else None

def basket_form(team_id):
    r = requests.get(
        f"{BASKET_API}/games",
        headers=HEADERS,
        params={"team": team_id, "last": 5}
    )
    return r.json().get("response", [])

# ================= PREDICTION =================
def get_prediction(match):
    if "-" not in match:
        return None

    home, away = [x.strip() for x in match.split("-", 1)]
    sport = detect_sport(match)

    # -------- FOOTBALL --------
    if sport == "football":
        h_id = football_team_id(home)
        a_id = football_team_id(away)
        if not h_id or not a_id:
            return None

        fixture = football_fixture(h_id, a_id)
        if not fixture:
            return None

        h_form = football_form(h_id)
        a_form = football_form(a_id)

        h_w = sum(1 for m in h_form if m["teams"]["home"]["winner"])
        a_w = sum(1 for m in a_form if m["teams"]["away"]["winner"])

        pick = "1" if h_w > a_w else "2" if a_w > h_w else "X"
        confidence = min(85, 50 + abs(h_w - a_w) * 8)

        return {
            "sport": "FUTBOL",
            "match": f"{home.title()} - {away.title()}",
            "pick": pick,
            "confidence": confidence,
            "desc": "Son 5 maç form + gerçek fikstür"
        }

    # -------- BASKET --------
    else:
        h_id = basket_team_id(home)
        a_id = basket_team_id(away)
        if not h_id or not a_id:
            return None

        h_form = basket_form(h_id)
        a_form = basket_form(a_id)
        if not h_form or not a_form:
            return None

        h_w = sum(1 for g in h_form if g["teams"]["home"]["winner"])
        a_w = sum(1 for g in a_form if g["teams"]["away"]["winner"])

        pick = "ÜST" if (h_w + a_w) >= 5 else "ALT"
        confidence = min(85, 55 + abs(h_w - a_w) * 7)

        return {
            "sport": "BASKETBOL",
            "match": f"{home.title()} - {away.title()}",
            "pick": pick,
            "confidence": confidence,
            "desc": "Tempo + kazanma trendi"
        }

# ================= UI =================
st.title("⚽🏀 TahminSor – Gerçek API (Stabil)")

left, right = st.columns([2, 1])

with left:
    with st.form("predict_form"):
        match = st.text_input("Maç gir (örn: chelsea - bournemouth / lakers - heat)")
        submit = st.form_submit_button("🔮 Tahmin Al")

    if submit:
        pred = get_prediction(match)
        if pred:
            st.session_state.prediction = pred
            st.success("Tahmin alındı")
        else:
            st.session_state.prediction = None
            st.error("❌ Yeterli gerçek veri bulunamadı")

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
            st.session_state.kupon.append(p)
            st.success("Kupona eklendi")

with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for k in st.session_state.kupon:
            st.markdown(
                f"**{k['match']}** — {k['sport']} | {k['pick']} | %{k['confidence']}"
            )

        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon = []
            st.rerun()
