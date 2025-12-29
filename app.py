import streamlit as st
import random

# -------------------------------------------------
# SAYFA
# -------------------------------------------------
st.set_page_config("TahminSor", layout="wide")

# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown("""
<style>
body { background:#f4f6f8; }
.block-container { padding-top:1rem; }

.card {
    background:#fff;
    padding:12px;
    border-radius:10px;
    margin-bottom:10px;
    box-shadow:0 0 8px rgba(0,0,0,.08);
}

.good { color:green; }
.bad { color:red; }

.bar {
    background:#eee;
    border-radius:6px;
    height:10px;
}
.fill {
    background:#2ecc71;
    height:10px;
    border-radius:6px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SESSION
# -------------------------------------------------
if "kupon" not in st.session_state:
    st.session_state.kupon = []

if "aliases" not in st.session_state:
    st.session_state.aliases = {
        "genk": "krc genk",
        "rkc genk": "krc genk",
        "club brugge": "club brugge kv",
        "man utd": "manchester united",
        "road warriors": "nlex road warriors",
        "san miguel": "san miguel beermen"
    }

# -------------------------------------------------
# NORMALIZE
# -------------------------------------------------
def n(t):
    return t.lower().replace(".", "").replace("-", " ").strip()

# -------------------------------------------------
# SPORT DETECT
# -------------------------------------------------
def detect_sport(text):
    b = ["nba","basket","warriors","beermen","lakers","celtics"]
    return "basketball" if any(x in n(text) for x in b) else "football"

# -------------------------------------------------
# MOCK API DATA
# -------------------------------------------------
FOOTBALL = ["krc genk","club brugge kv","manchester united","sakaryaspor a s","manisa futbol kulubu"]
BASKETBALL = ["nlex road warriors","san miguel beermen"]

# -------------------------------------------------
# FIND TEAM (HYBRID)
# -------------------------------------------------
def find_team(user, pool):
    u = n(user)
    u = st.session_state.aliases.get(u, u)

    for t in pool:
        if u == n(t):
            return t

    for t in pool:
        if u in n(t) or n(t) in u:
            return t

    return None

# -------------------------------------------------
# TAHMİN MOTORU
# -------------------------------------------------
def predict():
    home = random.randint(30,45)
    draw = random.randint(20,30)
    away = 100 - home - draw

    winner = max(
        [("Ev Sahibi",home),("Beraberlik",draw),("Deplasman",away)],
        key=lambda x:x[1]
    )

    confidence = winner[1]
    return winner[0], confidence, home, draw, away

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("⚽🏀 TahminSor")

col1, col2 = st.columns([2,1])

with col1:
    match = st.text_input("Maç gir (örn: genk - club brugge)")
    if st.button("Kupona Ekle"):
        try:
            a,b = match.split("-")
            sport = detect_sport(match)
            pool = BASKETBALL if sport=="basketball" else FOOTBALL

            t1 = find_team(a, pool)
            t2 = find_team(b, pool)

            ok = bool(t1 and t2)

            tahmin, conf, h,d,aw = predict()

            st.session_state.kupon.append({
                "match": f"{t1 or a.strip()} - {t2 or b.strip()}",
                "sport": sport,
                "ok": ok,
                "tahmin": tahmin,
                "conf": conf
            })
        except:
            st.warning("Format: takım1 - takım2")

# -------------------------------------------------
# KUPON
# -------------------------------------------------
with col2:
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
                <small>Güven: %{k['conf']}</small>
                <div class="bar">
                    <div class="fill" style="width:{k['conf']}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
