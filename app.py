import streamlit as st
import random

# -------------------------------------------------
# PAGE
# -------------------------------------------------
st.set_page_config("TahminSor", layout="wide")

# -------------------------------------------------
# STYLE
# -------------------------------------------------
st.markdown("""
<style>
body { background:#f5f6fa; }
.card {
    background:#fff;
    padding:12px;
    border-radius:10px;
    margin-bottom:10px;
    box-shadow:0 2px 6px rgba(0,0,0,.1);
}
.good { color:green; }
.bad { color:red; }
.bar { background:#ddd; height:8px; border-radius:6px; }
.fill { background:#27ae60; height:8px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SESSION
# -------------------------------------------------
if "kupon" not in st.session_state:
    st.session_state.kupon = []

# -------------------------------------------------
# DATA (MOCK)
# -------------------------------------------------
FOOTBALL = [
    "krc genk",
    "club brugge kv",
    "manchester united",
    "newcastle united",
    "sakaryaspor a s",
    "manisa futbol kulubu"
]

BASKETBALL = [
    "nlex road warriors",
    "san miguel beermen"
]

ALIASES = {
    "genk": "krc genk",
    "rkc genk": "krc genk",
    "club brugge": "club brugge kv",
    "man utd": "manchester united",
    "road warriors": "nlex road warriors",
    "san miguel": "san miguel beermen",
    "manisa fk": "manisa futbol kulubu"
}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def normalize(t):
    return t.lower().replace(".", "").replace("-", " ").strip()

def detect_sport(txt):
    b = ["warriors","beermen","nba"]
    return "basketball" if any(x in normalize(txt) for x in b) else "football"

def match_score(a, b):
    sa = set(normalize(a).split())
    sb = set(normalize(b).split())
    return len(sa & sb) / max(len(sa), len(sb))

def find_team(user_input, pool):
    u = normalize(user_input)
    u = normalize(ALIASES.get(u, u))

    best = None
    best_score = 0

    for team in pool:
        score = match_score(u, team)
        if score > best_score:
            best = team
            best_score = score

    return best if best_score >= 0.5 else None

def predict():
    home = random.randint(30,45)
    draw = random.randint(20,30)
    away = 100 - home - draw
    pick = max(
        [("Ev Sahibi",home),("Beraberlik",draw),("Deplasman",away)],
        key=lambda x:x[1]
    )
    return pick[0], pick[1]

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("⚽🏀 TahminSor")

left, right = st.columns([2,1])

with left:
    match = st.text_input("Maç gir (örn: genk - club brugge)")

    if st.button("Kupona Ekle"):
        try:
            a,b = match.split("-")
            sport = detect_sport(match)
            pool = BASKETBALL if sport=="basketball" else FOOTBALL

            t1 = find_team(a, pool)
            t2 = find_team(b, pool)

            tahmin, guven = predict()

            st.session_state.kupon.append({
                "match": f"{t1 or a.strip()} - {t2 or b.strip()}",
                "ok": bool(t1 and t2),
                "sport": sport,
                "tahmin": tahmin,
                "guven": guven
            })
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
                    {"🟢 Veri bulundu" if k['ok'] else "❌ Veri bulunamadı"}
                </span><br><br>
                <b>Öneri:</b> {k['tahmin']}<br>
                <small>Güven: %{k['guven']}</small>
                <div class="bar">
                    <div class="fill" style="width:{k['guven']}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
