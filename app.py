# app.py
# TAHMINSOR – FINAL STABLE BUILD
# Sohbet + Futbol & Basketbol Tahmin + Kupon + Value Bet

import streamlit as st
import requests
import re
import random

# =====================
# AYARLAR
# =====================
st.set_page_config(page_title="Tahminsor", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"

HEADERS = {"x-apisports-key": API_KEY}

FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"
BASK_GAMES = "https://v1.basketball.api-sports.io/games"
BASK_PRED = "https://v1.basketball.api-sports.io/predictions"

# =====================
# SESSION STATE
# =====================
for k in ["messages", "kupon", "last_prediction"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k != "last_prediction" else None

# =====================
# YARDIMCI FONKSİYONLAR
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

# =====================
# FALLBACK (API YOKSA)
# =====================
def fallback_tahmin(spor):
    guven = random.randint(52, 62)
    if spor == "futbol":
        secim = random.choice(["Ev Sahibi", "Beraberlik", "Deplasman"])
    else:
        secim = random.choice(["Ev Sahibi", "Deplasman"])

    return {
        "secim": secim,
        "guven": guven,
        "oran": round(1 + (100 / guven), 2),
        "value": guven > 55,
        "kaynak": "Model"
    }

# =====================
# FUTBOL TAHMİN
# =====================
def futbol_tahmin(mac):
    try:
        home, away = [x.strip() for x in re.split("[-–]", mac)]
        f = requests.get(
            FOOT_FIX,
            headers=HEADERS,
            params={"team": home, "next": 1},
            timeout=10
        ).json()

        if not f.get("response"):
            raise Exception("fixture yok")

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
# BASKETBOL TAHMİN
# =====================
def basketbol_tahmin(mac):
    try:
        home, away = [x.strip() for x in re.split("[-–]", mac)]
        g = requests.get(
            BASK_GAMES,
            headers=HEADERS,
            params={"team": home, "season": 2024},
            timeout=10
        ).json()

        if not g.get("response"):
            raise Exception("game yok")

        game_id = g["response"][0]["id"]

        p = requests.get(
            BASK_PRED,
            headers=HEADERS,
            params={"game": game_id},
            timeout=10
        ).json()

        pr = p["response"][0]["percent"]
        h = int(pr["home"].replace("%", ""))
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
left, right = st.columns([3, 1])

with left:
    st.title("💬 Tahminsor")
    st.caption("Sohbet et • Maç yaz • Tahmin & Kupon üret")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Maç yaz (Takım A - Takım B) veya sohbet et")

    if q:
        st.session_state.messages.append({"role": "user", "content": q})

        if mac_mi(q):
            # spor türünü sezgisel ayır
            if any(k in q.lower() for k in ["fc", "spor", "utd", "fk", "sk"]):
                t = futbol_tahmin(q)
                spor_emoji = "⚽"
            else:
                t = basketbol_tahmin(q)
                spor_emoji = "🏀"

            st.session_state.last_prediction = {"mac": q, **t}

            cevap = (
                f"{spor_emoji} **Maç Analizi**\n\n"
                f"👉 Tahmin: **{t['secim']}**\n"
                f"📊 Güven: **%{t['guven']}** {guven_bar(t['guven'])}\n"
                f"💰 Oran ~ {t['oran']}\n"
                f"🎯 Value Bet: {'VAR 🟢' if t['value'] else 'YOK 🔴'}\n"
                f"📌 Stake: {stake_oneri(t['guven'])}\n"
                f"🔗 Kaynak: {t['kaynak']}\n\n"
                f"➡ Kupona eklemek için **kupon ekle** yaz"
            )

        elif "kupon ekle" in q.lower() and st.session_state.last_prediction:
            st.session_state.kupon.append(st.session_state.last_prediction)
            cevap = "✅ Tahmin kupona eklendi."

        else:
            cevap = "Sohbet edebiliriz 🙂 Maç yazarsan analiz ederim."

        st.session_state.messages.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.markdown(cevap)

with right:
    st.markdown("## 🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        toplam_oran = 1
        toplam_guven = 0

        for i, k in enumerate(st.session_state.kupon, 1):
            toplam_oran *= k["oran"]
            toplam_guven += k["guven"]
            st.markdown(f"{i}. **{k['mac']}** → {k['secim']} ({k['oran']})")

        st.markdown(f"### 💰 Toplam Oran: {round(toplam_oran,2)}")
        st.markdown(f"### 📊 Ortalama Güven: %{int(toplam_guven/len(st.session_state.kupon))}")

st.caption("© Tahminsor • FINAL BUILD")
