import streamlit as st
import random
import re

st.set_page_config("TahminSor", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body { background:#f4f6fb; }
.card {
    background:#ffffff;
    padding:14px;
    border-radius:12px;
    margin-bottom:12px;
    box-shadow:0 2px 8px rgba(0,0,0,.08);
}
.good { color:#27ae60; font-weight:bold; }
.bad { color:#c0392b; font-weight:bold; }
.bar { background:#e0e0e0; height:8px; border-radius:6px; }
.fill { background:#27ae60; height:8px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ---------------- DATA ----------------
FOOTBALL_TEAMS = [
    "krc genk",
    "club brugge kv",
    "manchester united",
    "newcastle united",
    "sakaryaspor",
    "manisa futbol kulubu"
]

BASKET_TEAMS = [
    "nlex road warriors",
    "san miguel beermen"
]

ALIASES = {
    "genk": "krc genk",
    "rkc genk": "krc genk",
    "club brugge": "club brugge kv",
    "brugge": "club brugge kv",
    "man utd": "manchester united",
    "newcastle utd": "newcastle united",
    "road warriors": "nlex road warriors",
    "san miguel": "san miguel beermen",
    "manisa fk": "manisa futbol kulubu"
}

# ---------------- HELPERS ----------------
def normalize(txt):
    return re.sub(r"[^a-z0-9 ]", "", txt.lower()).strip()

def apply_alias(txt):
    t = normalize(txt)
    return normalize(ALIASES.get(t, t))

def match_score(a, b):
    sa = set(a.split())
    sb = set(b.split())
    if not sa or not sb:
        return 0
    return len(sa & sb) / len(sa | sb)

def find_team(user_text, pool):
    u = apply_alias(user_text)

    best_team = None
    best_score = 0

    for team in pool:
        t = normalize(team)

        # 1️⃣ token skor
        score = match_score(u, t)

        # 2️⃣ contains bonus
        if u in t or t in u:
            score += 0.3

        if score > best_score:
            best_score = score
            best_team = team

    # 3️⃣ eşik ZORLA düşürüldü
    return best_team if best_score >= 0.3 else None

def detect_sport(text):
    t = normalize(text)
    return "basketbol" if any(x in t for x in ["warriors", "beermen"]) else "futbol"

def predict():
    h = random.randint(35, 50)
    d = random.randint(20, 30)
    a = 100 - h - d
    pick = max(
        [("Ev Sahibi", h), ("Beraberlik", d), ("Deplasman", a)],
        key=lambda x: x[1]
    )
    return pick

# ---------------- UI ----------------
st.title("⚽🏀 TahminSor – Hybrid Matcher")

left, right = st.columns([2,1])

with left:
    match = st.text_input("Maç gir (örn: genk - club brugge)")

    if st.button("Kupona Ekle"):
        try:
            home, away = match.split("-")
            sport = detect_sport(match)
            pool = BASKET_TEAMS if sport == "basketbol" else FOOTBALL_TEAMS

            h_team = find_team(home, pool)
            a_team = find_team(away, pool)

            pick, conf = predict()

            st.session_state.kupon.append({
                "match": f"{h_team or home.strip()} - {a_team or away.strip()}",
                "ok": bool(h_team and a_team),
                "sport": sport,
                "pick": pick,
                "conf": conf
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
                <b>Öneri:</b> {k['pick'][0]}<br>
                <small>Güven: %{k['conf']}</small>
                <div class="bar">
                    <div class="fill" style="width:{k['conf']}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
