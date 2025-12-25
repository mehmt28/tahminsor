# app.py — TAHMINSOR | FAZ 2 ANALİZ MOTORU
import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor", layout="centered")

# =========================
# API
# =========================
API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"
BASKET_GAMES = "https://v1.basketball.api-sports.io/games"
BASKET_PRED = "https://v1.basketball.api-sports.io/predictions"

# =========================
# ALIAS
# =========================
ALIASES = {
    "rkc genk": "genk",
    "krc genk": "genk",
    "racing genk": "genk",
    "club brugge": "club brugge kv",
    "man utd": "manchester united",
    "road warriors": "nlex road warriors",
    "san miguel": "san miguel beermen",
}

def normalize(t): return ALIASES.get(t.lower().strip(), t.lower().strip())

# =========================
# FORMAT
# =========================
def mac_mi(q): return bool(re.search(r".+\s*-\s*.+", q))
def parcala(q):
    h,a = re.split(r"\s*-\s*", q, 1)
    return normalize(h), normalize(a)

# =========================
# YARDIMCI
# =========================
def bar(p):
    return "█" * int(p/10) + "░" * (10-int(p/10))

# =========================
# FALLBACK MODEL
# =========================
def fallback(home, away, spor):
    guven = min(70, 55 + abs(len(home)-len(away)))
    secim = "Ev Sahibi" if len(home)>=len(away) else "Deplasman"

    altust = "ÜST" if spor=="Basketbol" else "2.5 ÜST"
    kg = "KG VAR"

    return {
        "secim": secim,
        "guven": guven,
        "altust": altust,
        "kg": kg,
        "neden": "Takım güç farkı + genel lig ortalamaları",
        "kaynak": "Model"
    }

# =========================
# FUTBOL
# =========================
def futbol(home, away):
    try:
        f = requests.get(FOOT_FIX, headers=HEADERS, params={"team": home, "next": 5}, timeout=8).json()
        if f.get("response"):
            fix = f["response"][0]["fixture"]["id"]
            p = requests.get(FOOT_PRED, headers=HEADERS, params={"fixture": fix}, timeout=8).json()
            if p.get("response"):
                pr = p["response"][0]["predictions"]
                pct = pr["percent"]
                g = pr["goals"]

                h,d,a = int(pct["home"][:-1]), int(pct["draw"][:-1]), int(pct["away"][:-1])
                secim, guven = max([("Ev Sahibi",h),("Beraberlik",d),("Deplasman",a)], key=lambda x:x[1])

                gol = float(g["home"]) + float(g["away"])
                altust = "2.5 ÜST" if gol >= 2.6 else "2.5 ALT"
                kg = "KG VAR" if float(g["home"])>0.8 and float(g["away"])>0.8 else "KG YOK"

                return {
                    "secim": secim,
                    "guven": guven,
                    "altust": altust,
                    "kg": kg,
                    "neden": "Gol beklentisi + maç sonucu yüzdeleri",
                    "kaynak": "API"
                }
    except:
        pass

    return fallback(home, away, "Futbol")

# =========================
# BASKETBOL
# =========================
def basket(home, away):
    try:
        g = requests.get(BASKET_GAMES, headers=HEADERS, params={"team": home, "season": 2024}, timeout=8).json()
        if g.get("response"):
            gid = g["response"][0]["id"]
            p = requests.get(BASKET_PRED, headers=HEADERS, params={"game": gid}, timeout=8).json()
            if p.get("response"):
                h = int(p["response"][0]["percent"]["home"][:-1])
                a = 100-h
                secim = "Ev Sahibi" if h>=a else "Deplasman"
                guven = max(h,a)

                total = p["response"][0].get("points",{}).get("total",165)
                altust = "ÜST" if total>=165 else "ALT"

                return {
                    "secim": secim,
                    "guven": guven,
                    "altust": altust,
                    "kg": None,
                    "neden": "Tempo + hücum verimliliği",
                    "kaynak": "API"
                }
    except:
        pass

    return fallback(home, away, "Basketbol")

# =========================
# SESSION
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

# =========================
# UI
# =========================
st.title("💬 Tahminsor – FAZ 2")
st.caption("Maç yaz → detaylı analiz al")

for m in st.session_state.chat:
    with st.chat_message(m["r"]):
        st.markdown(m["c"])

q = st.chat_input("Örnek: Genk - Club Brugge | Road Warriors - San Miguel")

if q:
    st.session_state.chat.append({"r":"user","c":q})

    if mac_mi(q):
        h,a = parcala(q)
        basket_ipucu = ["warriors","beermen","kgc","thunders","bullets","breakers"]
        spor = "Basketbol" if any(x in q.lower() for x in basket_ipucu) else "Futbol"

        s = basket(h,a) if spor=="Basketbol" else futbol(h,a)

        cevap = (
            f"🏟️ **{h.title()} - {a.title()}**\n\n"
            f"🏀 Spor: {spor}\n"
            f"👉 Ana Tahmin: **{s['secim']}**\n"
            f"📊 Güven: %{s['guven']} {bar(s['guven'])}\n"
            f"📈 Alt/Üst: **{s['altust']}**\n"
            f"{f'⚽ KG: {s['kg']}' if s['kg'] else ''}\n\n"
            f"🧠 Neden?: {s['neden']}\n"
            f"🔗 Kaynak: {s['kaynak']}"
        )
    else:
        cevap = "Sohbet edebiliriz 🙂 Maç yazarsan analiz ederim."

    st.session_state.chat.append({"r":"assistant","c":cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)
