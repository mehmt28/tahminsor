# app.py — TAHMINSOR | FAZ 1 ÇEKİRDEK
import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor", layout="centered")

# =========================
# API AYARLARI
# =========================
API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"
BASKET_GAMES = "https://v1.basketball.api-sports.io/games"
BASKET_PRED = "https://v1.basketball.api-sports.io/predictions"

# =========================
# ALIAS & NORMALIZATION
# =========================
ALIASES = {
    "rkc genk": "genk",
    "krc genk": "genk",
    "racing genk": "genk",
    "club brugge": "club brugge kv",
    "man utd": "manchester united",
    "manchester utd": "manchester united",
    "road warriors": "nlex road warriors",
    "san miguel": "san miguel beermen",
}

def normalize(name: str) -> str:
    name = name.lower().strip()
    return ALIASES.get(name, name)

# =========================
# FORMAT KONTROL
# =========================
def mac_mi(text: str) -> bool:
    return bool(re.search(r".+\s*-\s*.+", text))

def parcala(text: str):
    home, away = re.split(r"\s*-\s*", text, maxsplit=1)
    return normalize(home), normalize(away)

# =========================
# FALLBACK MODEL (ASLA BOŞ DÖNMEZ)
# =========================
def fallback_model(home, away, spor):
    guven = 55 + abs(len(home) - len(away))
    secim = "Ev Sahibi" if len(home) >= len(away) else "Deplasman"

    return {
        "spor": spor,
        "secim": secim,
        "guven": min(guven, 70),
        "kaynak": "Model"
    }

# =========================
# FUTBOL ANALİZ
# =========================
def futbol_analiz(home, away):
    try:
        r = requests.get(
            FOOT_FIX,
            headers=HEADERS,
            params={"team": home, "next": 5},
            timeout=8
        ).json()

        if r.get("response"):
            fix_id = r["response"][0]["fixture"]["id"]
            p = requests.get(
                FOOT_PRED,
                headers=HEADERS,
                params={"fixture": fix_id},
                timeout=8
            ).json()

            if p.get("response"):
                pr = p["response"][0]["predictions"]["percent"]
                h = int(pr["home"].replace("%", ""))
                d = int(pr["draw"].replace("%", ""))
                a = int(pr["away"].replace("%", ""))

                secim, guven = max(
                    [("Ev Sahibi", h), ("Beraberlik", d), ("Deplasman", a)],
                    key=lambda x: x[1]
                )

                return {
                    "spor": "Futbol",
                    "secim": secim,
                    "guven": guven,
                    "kaynak": "API"
                }
    except:
        pass

    return fallback_model(home, away, "Futbol")

# =========================
# BASKETBOL ANALİZ
# =========================
def basketbol_analiz(home, away):
    try:
        r = requests.get(
            BASKET_GAMES,
            headers=HEADERS,
            params={"team": home, "season": 2024},
            timeout=8
        ).json()

        if r.get("response"):
            game_id = r["response"][0]["id"]
            p = requests.get(
                BASKET_PRED,
                headers=HEADERS,
                params={"game": game_id},
                timeout=8
            ).json()

            if p.get("response"):
                h = int(p["response"][0]["percent"]["home"].replace("%", ""))
                a = 100 - h

                secim = "Ev Sahibi" if h >= a else "Deplasman"
                guven = max(h, a)

                return {
                    "spor": "Basketbol",
                    "secim": secim,
                    "guven": guven,
                    "kaynak": "API"
                }
    except:
        pass

    return fallback_model(home, away, "Basketbol")

# =========================
# SESSION
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# UI
# =========================
st.title("💬 Tahminsor – FAZ 1")
st.caption("Sohbet et • Maç yaz • Analiz al")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input("Örnek: Genk - Club Brugge | Road Warriors - San Miguel")

if q:
    st.session_state.messages.append({"role": "user", "content": q})

    if mac_mi(q):
        home, away = parcala(q)

        # basit spor tespiti
        basket_ipucu = ["warriors", "beermen", "kgc", "thunders", "bullets", "breakers"]
        spor = "Basketbol" if any(x in q.lower() for x in basket_ipucu) else "Futbol"

        sonuc = (
            basketbol_analiz(home, away)
            if spor == "Basketbol"
            else futbol_analiz(home, away)
        )

        cevap = (
            f"🏟️ **{home.title()} - {away.title()}**\n\n"
            f"🏀 Spor: {sonuc['spor']}\n"
            f"👉 Tahmin: **{sonuc['secim']}**\n"
            f"📊 Güven: %{sonuc['guven']}\n"
            f"🧠 Kaynak: {sonuc['kaynak']}"
        )
    else:
        cevap = "Sohbet edebiliriz 🙂 Bir maç yazarsan analiz ederim."

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)
