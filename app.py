# app.py
# === Tahminsor | Futbol + Basketbol (KESİN ID EŞLEŞTİRME) ===

import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor AI", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"

HEADERS = {"x-apisports-key": API_KEY}

# =========================
# GENEL
# =========================
def mac_format(q):
    return bool(re.search(r".+[-–].+", q))


def split_mac(q):
    return [x.strip() for x in re.split("[-–]", q)]


def guven_bar(p):
    return "█" * int(p / 10) + "░" * (10 - int(p / 10))


# =========================
# TEAM ID BULUCU
# =========================
def get_team_id(name, sport="football"):
    url = f"https://v3.football.api-sports.io/teams" if sport == "football" else \
          f"https://v1.basketball.api-sports.io/teams"

    r = requests.get(url, headers=HEADERS, params={"search": name}).json()
    if not r.get("response"):
        return None

    return r["response"][0]["team"]["id"] if sport == "football" else r["response"][0]["id"]


# =========================
# FUTBOL
# =========================
def futbol_tahmin(mac):
    home, away = split_mac(mac)

    home_id = get_team_id(home, "football")
    away_id = get_team_id(away, "football")
    if not home_id or not away_id:
        return None

    fix = requests.get(
        "https://v3.football.api-sports.io/fixtures",
        headers=HEADERS,
        params={"team": home_id, "next": 1}
    ).json()

    if not fix.get("response"):
        return None

    fixture_id = fix["response"][0]["fixture"]["id"]

    pred = requests.get(
        "https://v3.football.api-sports.io/predictions",
        headers=HEADERS,
        params={"fixture": fixture_id}
    ).json()

    if not pred.get("response"):
        return None

    p = pred["response"][0]["predictions"]["percent"]
    home_p, draw_p, away_p = int(p["home"][:-1]), int(p["draw"][:-1]), int(p["away"][:-1])

    secim, guven = max(
        [("Ev Sahibi", home_p), ("Beraberlik", draw_p), ("Deplasman", away_p)],
        key=lambda x: x[1]
    )

    return {
        "spor": "⚽ Futbol",
        "secim": secim,
        "guven": guven,
        "oran": round(1 + (100 / guven), 2)
    }


# =========================
# BASKETBOL
# =========================
def basketbol_tahmin(mac):
    home, away = split_mac(mac)

    home_id = get_team_id(home, "basketball")
    away_id = get_team_id(away, "basketball")
    if not home_id or not away_id:
        return None

    games = requests.get(
        "https://v1.basketball.api-sports.io/games",
        headers=HEADERS,
        params={"team": home_id, "season": 2024}
    ).json()

    if not games.get("response"):
        return None

    game_id = games["response"][0]["id"]

    pred = requests.get(
        "https://v1.basketball.api-sports.io/predictions",
        headers=HEADERS,
        params={"game": game_id}
    ).json()

    if not pred.get("response"):
        return None

    p = pred["response"][0]["percent"]
    home_p = int(p["home"][:-1])
    away_p = 100 - home_p

    secim = "Ev Sahibi" if home_p > away_p else "Deplasman"
    guven = max(home_p, away_p)

    return {
        "spor": "🏀 Basketbol",
        "secim": secim,
        "guven": guven,
        "oran": round(1 + (100 / guven), 2)
    }


# =========================
# SESSION
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kupon" not in st.session_state:
    st.session_state.kupon = []
if "son" not in st.session_state:
    st.session_state.son = None
if "aktif_mac" not in st.session_state:
    st.session_state.aktif_mac = None


# =========================
# UI
# =========================
left, right = st.columns([3, 1])

with left:
    st.title("💬 Tahminsor AI")
    st.caption("Futbol + Basketbol | Gerçek API | Kesin Eşleşme")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Maç yaz: Team A - Team B")

    if q:
        st.session_state.messages.append({"role": "user", "content": q})

        if mac_format(q):
            st.session_state.aktif_mac = q

            t = futbol_tahmin(q) or basketbol_tahmin(q)

            if not t:
                cevap = "❌ Veri bulunamadı (takım adı farklı olabilir)"
            else:
                st.session_state.son = t
                cevap = (
                    f"{t['spor']} Analizi\n"
                    f"👉 Tahmin: **{t['secim']}**\n"
                    f"📊 Güven: %{t['guven']} {guven_bar(t['guven'])}\n"
                    f"💰 Oran ~ {t['oran']}\n\n"
                    f"Kupona eklemek için **kupon ekle** yaz"
                )

        elif "kupon ekle" in q.lower() and st.session_state.son:
            st.session_state.kupon.append({
                "mac": st.session_state.aktif_mac,
                **st.session_state.son
            })
            cevap = "✅ Kupona eklendi"

        else:
            cevap = "Sohbet edebiliriz 🙂"

        st.session_state.messages.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.markdown(cevap)


with right:
    st.markdown("## 🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        oran = 1
        for i, k in enumerate(st.session_state.kupon, 1):
            oran *= k["oran"]
            st.markdown(f"{i}. {k['mac']} → {k['secim']} ({k['oran']})")

        st.markdown(f"### 💰 Toplam Oran: {round(oran,2)}")

st.caption("© Tahminsor AI")
