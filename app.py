# app.py
import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOT_TEAMS = "https://v3.football.api-sports.io/teams"
FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
FOOT_PRED = "https://v3.football.api-sports.io/predictions"

BASK_TEAMS = "https://v1.basketball.api-sports.io/teams"
BASK_GAMES = "https://v1.basketball.api-sports.io/games"
BASK_PRED = "https://v1.basketball.api-sports.io/predictions"


# ---------------------------
# UTIL
# ---------------------------
def mac_format(q):
    return bool(re.search(r".+\s*[-–]\s*.+", q))


def search_team_football(name):
    r = requests.get(
        FOOT_TEAMS,
        headers=HEADERS,
        params={"search": name}
    ).json()
    if r.get("response"):
        return r["response"][0]["team"]["id"]
    return None


def search_team_basket(name):
    r = requests.get(
        BASK_TEAMS,
        headers=HEADERS,
        params={"search": name}
    ).json()
    if r.get("response"):
        return r["response"][0]["id"]
    return None


# ---------------------------
# FUTBOL
# ---------------------------
def futbol_tahmin(mac):
    home, away = [x.strip() for x in re.split("[-–]", mac)]

    home_id = search_team_football(home)
    if not home_id:
        return None

    f = requests.get(
        FOOT_FIX,
        headers=HEADERS,
        params={"team": home_id, "next": 1}
    ).json()

    if not f.get("response"):
        return None

    fix = f["response"][0]
    fid = fix["fixture"]["id"]

    p = requests.get(
        FOOT_PRED,
        headers=HEADERS,
        params={"fixture": fid}
    ).json()

    if not p.get("response"):
        return None

    pr = p["response"][0]["predictions"]["percent"]
    h = int(pr["home"].replace("%", ""))
    d = int(pr["draw"].replace("%", ""))
    a = int(pr["away"].replace("%", ""))

    secim = max(
        [("Ev Sahibi", h), ("Beraberlik", d), ("Deplasman", a)],
        key=lambda x: x[1]
    )

    return {
        "spor": "futbol",
        "secim": secim[0],
        "guven": secim[1]
    }


# ---------------------------
# BASKETBOL
# ---------------------------
def basketbol_tahmin(mac):
    home, away = [x.strip() for x in re.split("[-–]", mac)]

    home_id = search_team_basket(home)
    if not home_id:
        return None

    g = requests.get(
        BASK_GAMES,
        headers=HEADERS,
        params={"team": home_id, "season": 2024}
    ).json()

    if not g.get("response"):
        return None

    game = g["response"][0]
    gid = game["id"]

    p = requests.get(
        BASK_PRED,
        headers=HEADERS,
        params={"game": gid}
    ).json()

    if not p.get("response"):
        return None

    pr = p["response"][0]["percent"]
    h = int(pr["home"].replace("%", ""))
    a = 100 - h

    secim = "Ev Sahibi" if h > a else "Deplasman"

    return {
        "spor": "basketbol",
        "secim": secim,
        "guven": max(h, a)
    }


# ---------------------------
# SESSION
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kupon" not in st.session_state:
    st.session_state.kupon = []
if "son" not in st.session_state:
    st.session_state.son = None
if "aktif_mac" not in st.session_state:
    st.session_state.aktif_mac = None


# ---------------------------
# UI
# ---------------------------
left, right = st.columns([3, 1])

with left:
    st.title("💬 Tahminsor")
    st.caption("Takım yaz • Sistem bulsun • Tahmin üretelim")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Örnek: Genk - Club Brugge")

    if q:
        st.session_state.messages.append({"role": "user", "content": q})

        cevap = "Sohbet edebiliriz 🙂"

        if mac_format(q):
            st.session_state.aktif_mac = q

            t = futbol_tahmin(q)
            if not t:
                t = basketbol_tahmin(q)

            if not t:
                cevap = "❌ Veri bulunamadı (lig / takım adı uyuşmuyor)"
            else:
                st.session_state.son = t
                cevap = (
                    f"🏟 Spor: **{t['spor'].upper()}**\n\n"
                    f"👉 Tahmin: **{t['secim']}**\n"
                    f"📊 Güven: %{t['guven']}\n\n"
                    f"Kupona eklemek için **kupon ekle** yaz"
                )

        elif "kupon ekle" in q.lower() and st.session_state.son:
            st.session_state.kupon.append({
                "mac": st.session_state.aktif_mac,
                **st.session_state.son
            })
            cevap = "✅ Tahmin kupona eklendi"

        st.session_state.messages.append({"role": "assistant", "content": cevap})
        with st.chat_message("assistant"):
            st.markdown(cevap)

with right:
    st.markdown("## 🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for i, k in enumerate(st.session_state.kupon, 1):
            st.markdown(
                f"**{i}. {k['mac']}**  \n"
                f"{k['spor']} → {k['secim']} (%{k['guven']})"
            )

st.caption("© Tahminsor | Faz 1 – Hybrid Team Matching")
