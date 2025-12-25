# app.py — TAHMINSOR FINAL PRO
import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor PRO", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

# =====================
# API ENDPOINTS
# =====================
FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"
BASKET_GAMES = "https://v1.basketball.api-sports.io/games"
BASKET_PRED = "https://v1.basketball.api-sports.io/predictions"

# =====================
# ALIAS
# =====================
ALIASES = {
    "rkc genk": "genk",
    "krc genk": "genk",
    "racing genk": "genk",
    "club brugge": "club brugge kv",
    "man utd": "manchester united",
    "road warriors": "nlex road warriors",
    "san miguel": "san miguel beermen",
}

def norm(t):
    return ALIASES.get(t.lower().strip(), t.lower().strip())

def parse(q):
    if "-" not in q:
        return None, None, None
    base, *lig = q.split("|")
    h, a = base.split("-", 1)
    return norm(h), norm(a), lig[0].strip() if lig else None

# =====================
# VALUE + STAKE
# =====================
def implied_prob(o): return round((1 / o) * 100, 1)
def value(m, o): return m > implied_prob(o)

def stake(p):
    if p >= 65: return "3/10 🔥"
    if p >= 55: return "2/10 ⚠️"
    return "1/10 ❄️"

def bar(p): return "█" * int(p/10) + "░" * (10-int(p/10))

# =====================
# FALLBACK MODEL
# =====================
def model(home, away):
    g = 54 + abs(len(home) - len(away)) * 2
    secim = "Ev Sahibi" if len(home) >= len(away) else "Deplasman"
    return secim, min(70, g)

# =====================
# FUTBOL
# =====================
def futbol(q):
    home, away, _ = parse(q)
    r = requests.get(FOOT_FIX, headers=HEADERS, params={"team": home, "next": 5}).json()

    if r.get("response"):
        fix_id = r["response"][0]["fixture"]["id"]
        p = requests.get(FOOT_PRED, headers=HEADERS, params={"fixture": fix_id}).json()
        if p.get("response"):
            pr = p["response"][0]["predictions"]
            h,d,a = [int(pr["percent"][x][:-1]) for x in ["home","draw","away"]]
            secim, guven = max([("Ev Sahibi",h),("Beraberlik",d),("Deplasman",a)], key=lambda x:x[1])
            odds = round(1 + (100/guven),2)
            return secim, guven, odds, "API"

    secim, guven = model(home, away)
    odds = round(1 + (100/guven),2)
    return secim, guven, odds, "MODEL"

# =====================
# BASKETBOL
# =====================
def basket(q):
    home, away, _ = parse(q)
    r = requests.get(BASKET_GAMES, headers=HEADERS, params={"team": home, "season": 2024}).json()

    if r.get("response"):
        gid = r["response"][0]["id"]
        p = requests.get(BASKET_PRED, headers=HEADERS, params={"game": gid}).json()
        if p.get("response"):
            h = int(p["response"][0]["percent"]["home"][:-1])
            a = 100-h
            secim = "Ev Sahibi" if h>a else "Deplasman"
            guven = max(h,a)
            odds = round(1+(100/guven),2)
            return secim, guven, odds, "API"

    secim, guven = model(home, away)
    odds = round(1+(100/guven),2)
    return secim, guven, odds, "MODEL"

# =====================
# SESSION
# =====================
for k in ["chat","kupon","roi"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k!="roi" else {"win":0,"lose":0}

# =====================
# UI
# =====================
l,r = st.columns([3,1])

with l:
    st.title("💬 Tahminsor PRO – Seviye 16+")
    for m in st.session_state.chat:
        with st.chat_message(m["r"]): st.markdown(m["c"])

    q = st.chat_input("Maç yaz: Genk - Club Brugge | Road Warriors - San Miguel")

    if q:
        st.session_state.chat.append({"r":"user","c":q})
        engine = basket if any(x in q.lower() for x in ["warriors","beermen"]) else futbol
        secim, guven, odds, src = engine(q)
        val = value(guven, odds)

        msg = (
            f"👉 **{secim}**\n\n"
            f"📊 Güven: %{guven} {bar(guven)}\n"
            f"💰 Oran: {odds}\n"
            f"🎯 Value: {'🟢 VAR' if val else '🔴 YOK'}\n"
            f"🔥 Stake: {stake(guven)}\n"
            f"🧠 Kaynak: {src}\n\n"
            f"**kupon ekle** yaz"
        )

        st.session_state.last = (q, secim, odds, guven, val)
        st.session_state.chat.append({"r":"assistant","c":msg})
        with st.chat_message("assistant"): st.markdown(msg)

        if "kupon ekle" in q.lower():
            st.session_state.kupon.append(st.session_state.last)

with r:
    st.markdown("## 🧾 Kupon")
    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        tot = 1
        for i,k in enumerate(st.session_state.kupon,1):
            tot *= k[2]
            st.markdown(f"{i}. {k[0]} → {k[1]} ({k[2]})")
        st.markdown(f"### 💰 Toplam Oran: {round(tot,2)}")
