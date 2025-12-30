import streamlit as st
import requests
import re

# ========== CONFIG ==========
st.set_page_config(page_title="TahminSor", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

TEAMS_URL = "https://v3.football.api-sports.io/teams"
FIXTURES_URL = "https://v3.football.api-sports.io/fixtures"
PRED_URL = "https://v3.football.api-sports.io/predictions"

# ========== STYLE ==========
st.markdown("""
<style>
.card{background:#fff;padding:16px;border-radius:12px;
box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:10px}
.good{color:#27ae60;font-weight:600}
.bad{color:#c0392b;font-weight:600}
</style>
""", unsafe_allow_html=True)

# ========== HELPERS ==========
def split_match(q):
    return [x.strip() for x in re.split("[-–]", q)]

def football_predict(match):
    try:
        home, away = split_match(match)
    except:
        return None

    team = requests.get(
        TEAMS_URL,
        headers=HEADERS,
        params={"search": home}
    ).json()

    if not team.get("response"):
        return None

    team_id = team["response"][0]["team"]["id"]

    fixture = requests.get(
        FIXTURES_URL,
        headers=HEADERS,
        params={"team": team_id, "next": 1}
    ).json()

    if not fixture.get("response"):
        return None

    fixture_id = fixture["response"][0]["fixture"]["id"]

    pred = requests.get(
        PRED_URL,
        headers=HEADERS,
        params={"fixture": fixture_id}
    ).json()

    if not pred.get("response"):
        return None

    perc = pred["response"][0]["predictions"]["percent"]

    home_p = int(perc["home"].replace("%", ""))
    draw_p = int(perc["draw"].replace("%", ""))
    away_p = int(perc["away"].replace("%", ""))

    pick, conf = max(
        [("Ev Sahibi", home_p), ("Beraberlik", draw_p), ("Deplasman", away_p)],
        key=lambda x: x[1]
    )

    return {
        "match": f"{home} - {away}",
        "pick": pick,
        "confidence": conf,
        "comment": "API verisine dayalı istatistiksel tahmin"
    }

# ========== SESSION ==========
if "current" not in st.session_state:
    st.session_state.current = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ========== UI ==========
st.title("⚽ TahminSor – Hybrid Matcher")

left, right = st.columns([3, 1])

# -------- LEFT --------
with left:
    with st.form("tahmin_form"):
        q = st.text_input("Maç gir (örn: genk - club brugge)")
        submit = st.form_submit_button("📊 Tahmin Al")

    if submit:
        result = football_predict(q)
        if result is None:
            st.session_state.current = None
            st.error("❌ Veri bulunamadı (lig / isim uyuşmuyor)")
        else:
            st.session_state.current = result

    if st.session_state.current:
        t = st.session_state.current
        st.markdown(f"""
        <div class="card">
            <h4>{t['match']}</h4>
            <b>Öneri:</b> {t['pick']}<br>
            <b>Güven:</b> %{t['confidence']}<br><br>
            <i>{t['comment']}</i>
        </div>
        """, unsafe_allow_html=True)

        st.progress(t["confidence"] / 100)

        if st.button("🧾 Kupona Ekle"):
            st.session_state.kupon.append(t)
            st.success("Kupona eklendi")

# -------- RIGHT --------
with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Henüz kupon yok")
    else:
        for k in st.session_state.kupon:
            st.markdown(f"""
            <div class="card">
                <b>{k['match']}</b><br>
                <span class="good">{k['pick']}</span><br>
                Güven: %{k['confidence']}
            </div>
            """, unsafe_allow_html=True)
