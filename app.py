# app.py
# === Tahminsor AI | KESİN TAKIM BULMA (FIXED) ===

import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor AI", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

LEAGUES = {
    "belgium": 144,
    "turkey": 203,
    "england": 39
}

# =========================
# YARDIMCI
# =========================
def normalize(name):
    return re.sub(r"[^a-z]", "", name.lower())


def mac_format(q):
    return bool(re.search(r".+[-–].+", q))


def split_mac(q):
    return [x.strip() for x in re.split("[-–]", q)]


def guven_bar(p):
    return "█" * int(p / 10) + "░" * (10 - int(p / 10))


# =========================
# KESİN TEAM ID
# =========================
def get_team_id_strict(team_name, league_id):
    r = requests.get(
        "https://v3.football.api-sports.io/teams",
        headers=HEADERS,
        params={"league": league_id, "season": 2024}
    ).json()

    if not r.get("response"):
        return None

    target = normalize(team_name)

    for t in r["response"]:
        api_name = normalize(t["team"]["name"])
        if target in api_name or api_name in target:
            return t["team"]["id"]

    return None


# =========================
# FUTBOL TAHMİN
# =========================
def futbol_tahmin(mac):
    home, away = split_mac(mac)

    # Belçika öncelikli dene
    home_id = get_team_id_strict(home, LEAGUES["belgium"])
    away_id = get_team_id_strict(away, LEAGUES["belgium"])

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

    home_p = int(p["home"][:-1])
    draw_p = int(p["draw"][:-1])
    away_p = int(p["away"][:-1])

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
# SESSION
# =========================
for k in ["messages", "kupon", "son", "aktif_mac"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k in ["messages", "kupon"] else None


# =========================
# UI
# =========================
st.title("💬 Tahminsor AI")
st.caption("KESİN TAKIM EŞLEŞTİRME | FIXED")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input("Maç yaz: Team A - Team B")

if q:
    st.session_state.messages.append({"role": "user", "content": q})

    if mac_format(q):
        st.session_state.aktif_mac = q
        t = futbol_tahmin(q)

        if not t:
            cevap = "❌ Veri bulunamadı (lig dışı veya farklı isim)"
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

st.markdown("## 🧾 Kupon")
if st.session_state.kupon:
    oran = 1
    for i, k in enumerate(st.session_state.kupon, 1):
        oran *= k["oran"]
        st.markdown(f"{i}. {k['mac']} → {k['secim']} ({k['oran']})")
    st.markdown(f"### 💰 Toplam Oran: {round(oran,2)}")
else:
    st.info("Kupon boş")
