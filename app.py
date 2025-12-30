import streamlit as st
import requests
import re

# ================= CONFIG =================
st.set_page_config(
    page_title="TahminSor",
    layout="wide"
)

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOTBALL_TEAMS = "https://v3.football.api-sports.io/teams"
FOOTBALL_FIXTURES = "https://v3.football.api-sports.io/fixtures"
FOOTBALL_PRED = "https://v3.football.api-sports.io/predictions"

# ================= STYLE =================
st.markdown("""
<style>
body { background:#f4f6fb; }
.card {
    background:#fff;
    padding:16px;
    border-radius:12px;
    margin-top:10px;
    box-shadow:0 2px 10px rgba(0,0,0,.08);
}
.good { color:#2ecc71; font-weight:600 }
.bad { color:#e74c3c; font-weight:600 }
</style>
""", unsafe_allow_html=True)

# ================= HELPERS =================
def split_match(q):
    return [x.strip() for x in re.split("[-–]", q)]

def football_predict(match):
    home, away = split_match(match)

    t = requests.get(
        FOOTBALL_TEAMS,
        headers=HEADERS,
        params={"search": home}
    ).json()

    if not t.get("response"):
        return None

    team_id = t["response"][0]["team"]["id"]

    f = requests.get(
        FOOTBALL_FIXTURES,
        headers=HEADERS,
        params={"team": team_id, "next": 1}
    ).json()

    if not f.get("response"):
        return None

    fixture_id = f["response"][0]["fixture"]["id"]

    p = requests.get(
        FOOTBALL_PRED,
        headers=HEADERS,
        params={"fixture": fixture_id}
    ).json()

    if not p.get("response"):
        return None

    perc = p["response"][0]["predictions"]["percent"]

    home_p = int(perc["home"].replace("%", ""))
    draw_p = int(perc["draw"].replace("%", ""))
    away_p = int(perc["away"].replace("%", ""))

    best = max(
        [("Ev Sahibi", home_p), ("Beraberlik", draw_p), ("Deplasman", away_p)],
        key=lambda x: x[1]
    )

    return {
        "match": f"{home} - {away}",
        "pick": best[0],
        "confidence": best[1],
        "comment": "API istatistiklerine göre en yüksek olasılık"
    }

# ================= SESSION =================
if "tahmin" not in st.session_state:
    st.session_state.tahmin = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ================= UI =================
st.title("⚽ TahminSor – Hybrid Matcher")

left, right = st.columns([3, 1])

# -------- LEFT --------
with left:
    with st.form("tahmin_form"):
        q = st.text_input("Maç gir (örn: genk - club brugge)")
        submit = st.form_submit_button("📊 Tahmin Al")

    if submit:
        data = football_predict(q)
        if not data:
            st.error("❌ Veri bulunamadı (isim / lig uyuşmuyor)")
            st.session_state.tahmin = None
        else:
            st.session_state.tahmin = data

    if st.session_state.tahmin:
        t = st.session_state.tahmin
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
