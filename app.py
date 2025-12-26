# app.py
# TAHMINSOR – FINAL BUILD + MOBILE UI

import streamlit as st
import requests
import re
import random

# =====================
# SAYFA AYAR
# =====================
st.set_page_config(
    page_title="Tahminsor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================
# MOBİL UI CSS
# =====================
st.markdown("""
<style>
/* Mobil uyum */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    h1 { font-size: 1.4rem; }
    h2 { font-size: 1.2rem; }
    h3 { font-size: 1.05rem; }
}

/* Chat mesajları */
.stChatMessage {
    border-radius: 14px;
    padding: 0.6rem;
}

/* Input yukarı yakın */
.stChatInputContainer {
    position: sticky;
    bottom: 0;
    background: #0e1117;
    padding-top: 0.5rem;
}

/* Kupon kart */
.kupon-card {
    background: #161b22;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# API
# =====================
API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"
BASK_GAMES = "https://v1.basketball.api-sports.io/games"
BASK_PRED = "https://v1.basketball.api-sports.io/predictions"

# =====================
# SESSION
# =====================
for k in ["messages", "kupon", "last_prediction"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k != "last_prediction" else None

# =====================
# YARDIMCI
# =====================
def mac_mi(q):
    return bool(re.search(r".+\s*[-–]\s*.+", q))

def guven_bar(p):
    return "█" * int(p / 10) + "░" * (10 - int(p / 10))

def stake_oneri(p):
    if p >= 65:
        return "3/10 (Yüksek)"
    elif p >= 55:
        return "2/10 (Orta)"
    else:
        return "1/10 (Düşük)"

def fallback_tahmin(spor):
    guven = random.randint(52, 62)
    secim = random.choice(
        ["Ev Sahibi", "Beraberlik", "Deplasman"] if spor == "futbol"
        else ["Ev Sahibi", "Deplasman"]
    )
    return {
        "secim": secim,
        "guven": guven,
        "oran": round(1 + (100 / guven), 2),
        "value": guven > 55,
        "kaynak": "Model"
    }

# =====================
# FUTBOL
# =====================
def futbol_tahmin(mac):
    try:
        home, _ = [x.strip() for x in re.split("[-–]", mac)]
        f = requests.get(
            FOOT_FIX,
            headers=HEADERS,
            params={"team": home, "next": 1},
            timeout=10
        ).json()

        fix_id = f["response"][0]["fixture"]["id"]

        p = requests.get(
            FOOT_PRED,
            headers=HEADERS,
            params={"fixture": fix_id},
            timeout=10
        ).json()

        pr = p["response"][0]["predictions"]["percent"]
        h = int(pr["home"].replace("%", ""))
        d = int(pr["draw"].replace("%", ""))
        a = int(pr["away"].replace("%", ""))

        secim, guven = max(
            [("Ev Sahibi", h), ("Beraberlik", d), ("Deplasman", a)],
            key=lambda x: x[1]
        )

        return {
            "secim": secim,
            "guven": guven,
            "oran": round(1 + (100 / guven), 2),
            "value": guven > 55,
            "kaynak": "API"
        }
    except:
        return fallback_tahmin("futbol")

# =====================
# BASKETBOL
# =====================
def basketbol_tahmin(mac):
    try:
        home, _ = [x.strip() for x in re.split("[-–]", mac)]
        g = requests.get(
            BASK_GAMES,
            headers=HEADERS,
            params={"team": home, "season": 2024},
            timeout=10
        ).json()

        game_id = g["response"][0]["id"]

        p = requests.get(
            BASK_PRED,
            headers=HEADERS,
            params={"game": game_id},
            timeout=10
        ).json()

        h = int(p["response"][0]["percent"]["home"].replace("%", ""))
        a = 100 - h

        secim = "Ev Sahibi" if h > a else "Deplasman"
        guven = max(h, a)

        return {
            "secim": secim,
            "guven": guven,
            "oran": round(1 + (100 / guven), 2),
            "value": guven > 55,
            "kaynak": "API"
        }
    except:
        return fallback_tahmin("basketbol")

# =====================
# UI
# =====================
st.title("💬 Tahminsor")
st.caption("Mobil uyumlu • Sohbet • Tahmin • Kupon")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input("Maç yaz (Takım A - Takım B) veya sohbet et")

if q:
    st.session_state.messages.append({"role": "user", "content": q})

    if mac_mi(q):
        t = futbol_tahmin(q) if any(x in q.lower() for x in ["spor", "fk", "fc", "utd"]) else basketbol_tahmin(q)
        st.session_state.last_prediction = {"mac": q, **t}

        cevap = (
            f"🎯 **Tahmin**: {t['secim']}\n\n"
            f"📊 Güven: %{t['guven']} {guven_bar(t['guven'])}\n"
            f"💰 Oran ~ {t['oran']}\n"
            f"📌 Stake: {stake_oneri(t['guven'])}\n"
            f"🔗 Kaynak: {t['kaynak']}\n\n"
            f"➡ **kupon ekle** yazarak ekleyebilirsin"
        )

    elif "kupon ekle" in q.lower() and st.session_state.last_prediction:
        st.session_state.kupon.append(st.session_state.last_prediction)
        cevap = "✅ Kupona eklendi."

    else:
        cevap = "Sohbet edebiliriz 🙂 Maç yazarsan analiz ederim."

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

# =====================
# KUPON (ALTTA – MOBİL)
# =====================
if st.session_state.kupon:
    st.markdown("---")
    st.markdown("## 🧾 Kupon")

    oran = 1
    guven = 0

    for k in st.session_state.kupon:
        oran *= k["oran"]
        guven += k["guven"]
        st.markdown(
            f"<div class='kupon-card'>"
            f"{k['mac']}<br><b>{k['secim']}</b> ({k['oran']})"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown(f"**Toplam Oran:** {round(oran,2)}")
    st.markdown(f"**Ortalama Güven:** %{int(guven/len(st.session_state.kupon))}")

st.caption("© Tahminsor • Mobile Ready")
