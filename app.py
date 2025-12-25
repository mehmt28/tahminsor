# app.py — Tahminsor HYBRID ENGINE (FINAL)

import streamlit as st
import requests
import re
from difflib import get_close_matches

st.set_page_config(page_title="Tahminsor Hybrid", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"

HEADERS = {"x-apisports-key": API_KEY}

FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"

# =====================
# TEAM ALIAS / NORMALIZER
# =====================
TEAM_ALIASES = {
    "rkc genk": "genk",
    "krc genk": "genk",
    "club brugge": "club brugge kv",
    "man utd": "manchester united",
    "newcastle utd": "newcastle",
}

def normalize_team(name):
    name = name.lower().strip()
    return TEAM_ALIASES.get(name, name)

def parse_match(q):
    if "-" not in q:
        return None, None
    h, a = q.split("-", 1)
    return normalize_team(h), normalize_team(a)

# =====================
# FALLBACK MODEL (KESİN)
# =====================
def model_predict(home, away):
    base = 55
    diff = abs(len(home) - len(away)) * 2

    if len(home) > len(away):
        return {
            "secim": "Ev Sahibi",
            "guven": min(65, base + diff),
            "kaynak": "MODEL"
        }
    else:
        return {
            "secim": "Deplasman",
            "guven": min(65, base + diff),
            "kaynak": "MODEL"
        }

# =====================
# FOOTBALL API + HYBRID
# =====================
def football_predict(q):
    home, away = parse_match(q)
    if not home or not away:
        return None

    # 1️⃣ FIXTURE SEARCH
    r = requests.get(
        FOOT_FIX,
        headers=HEADERS,
        params={"team": home, "next": 5}
    ).json()

    if r.get("response"):
        for f in r["response"]:
            teams = f["teams"]
            if away in teams["away"]["name"].lower() or away in teams["home"]["name"].lower():
                fix_id = f["fixture"]["id"]

                p = requests.get(
                    FOOT_PRED,
                    headers=HEADERS,
                    params={"fixture": fix_id}
                ).json()

                if p.get("response"):
                    perc = p["response"][0]["predictions"]["percent"]
                    h = int(perc["home"].replace("%", ""))
                    d = int(perc["draw"].replace("%", ""))
                    a = int(perc["away"].replace("%", ""))

                    best = max(
                        [("Ev Sahibi", h), ("Beraberlik", d), ("Deplasman", a)],
                        key=lambda x: x[1]
                    )

                    return {
                        "secim": best[0],
                        "guven": best[1],
                        "kaynak": "API"
                    }

    # 2️⃣ FALLBACK
    return model_predict(home, away)

# =====================
# UI
# =====================
st.title("⚽ Tahminsor Hybrid (API + MODEL)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input("Maç yaz: Genk - Club Brugge")

if q:
    st.session_state.messages.append({"role": "user", "content": q})

    t = football_predict(q)

    if not t:
        msg = "❌ Format hatası"
    else:
        msg = (
            f"### ⚽ Maç Analizi\n"
            f"👉 Tahmin: **{t['secim']}**\n"
            f"📊 Güven: **%{t['guven']}**\n"
            f"🧠 Kaynak: **{t['kaynak']}**"
        )

    st.session_state.messages.append({"role": "assistant", "content": msg})
    with st.chat_message("assistant"):
        st.markdown(msg)
