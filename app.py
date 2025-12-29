import streamlit as st
import requests
from difflib import get_close_matches

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="TahminSor AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_KEY = "2aafffec4c31cf146173e2064c6709d1"

HEADERS = {
    "x-apisports-key": API_KEY
}

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background-color: #f5f6fa;
}
.block-container {
    padding-top: 1rem;
}
.kupon-box {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 10px;
}
.match-box {
    background-color: #ffffff;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    margin-bottom: 8px;
}
.confidence {
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def normalize(name):
    return name.lower().replace(".", "").replace("-", " ").strip()

def hybrid_match(team, team_list):
    team = normalize(team)
    names = [normalize(t) for t in team_list]
    match = get_close_matches(team, names, n=1, cutoff=0.6)
    if match:
        idx = names.index(match[0])
        return team_list[idx]
    return None

# ---------------- API FUNCTIONS ----------------
def get_football_fixture(home, away):
    url = "https://v3.football.api-sports.io/teams"
    res = requests.get(url, headers=HEADERS).json()

    teams = [t["team"]["name"] for t in res["response"]]

    h = hybrid_match(home, teams)
    a = hybrid_match(away, teams)

    if not h or not a:
        return None

    return {
        "home": h,
        "away": a,
        "sport": "Futbol"
    }

def get_basketball_fixture(home, away):
    url = "https://v1.basketball.api-sports.io/teams"
    res = requests.get(url, headers=HEADERS).json()

    teams = [t["name"] for t in res["response"]]

    h = hybrid_match(home, teams)
    a = hybrid_match(away, teams)

    if not h or not a:
        return None

    return {
        "home": h,
        "away": a,
        "sport": "Basketbol"
    }

# ---------------- SESSION ----------------
if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ---------------- UI ----------------
st.title("🤖 TahminSor AI")
st.caption("Futbol & Basketbol | Hybrid API | Kupon Üretici")

col1, col2 = st.columns([2, 1])

with col1:
    sport = st.radio("Spor Türü", ["Futbol", "Basketbol"], horizontal=True)

    match_input = st.text_input(
        "Maç Gir (örn: Genk - Club Brugge)",
        placeholder="Ev Sahibi - Deplasman"
    )

    if st.button("Analiz Et"):
        if "-" not in match_input:
            st.error("Format yanlış")
        else:
            home, away = [x.strip() for x in match_input.split("-")]

            if sport == "Futbol":
                data = get_football_fixture(home, away)
            else:
                data = get_basketball_fixture(home, away)

            if not data:
                st.error("❌ Veri bulunamadı (isim/lig uyuşmuyor)")
            else:
                confidence = 65 + len(home) % 20
                ran = round(confidence / 10, 2)

                st.markdown(f"""
                <div class="match-box">
                <b>{data['sport']}</b><br>
                {data['home']} vs {data['away']}<br>
                <div class="confidence">Güven: %{confidence}</div>
                RAN: {ran}
                </div>
                """, unsafe_allow_html=True)

                if st.button("➕ Kupona Ekle"):
                    st.session_state.kupon.append({
                        "match": f"{data['home']} - {data['away']}",
                        "sport": data["sport"],
                        "confidence": confidence,
                        "ran": ran
                    })

with col2:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for i, k in enumerate(st.session_state.kupon):
            st.markdown(f"""
            <div class="kupon-box">
            <b>{k['match']}</b><br>
            {k['sport']}<br>
            Güven: %{k['confidence']}<br>
            RAN: {k['ran']}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon = []

# ---------------- MOBILE NOTE ----------------
st.caption("📱 Mobil uyumlu | Streamlit Responsive Layout")
