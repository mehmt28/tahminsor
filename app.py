# app.py
# === Tahminsor AI | Seviye 16 FINAL ===
# Lig Otomatik | Futbol + Basketbol | Canlı | Value | Kupon

import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor AI", layout="wide")

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

FOOTBALL_LEAGUES = {
    "TR": 203,
    "BE": 144,
    "EN": 39
}

BASKETBALL_LEAGUES = {
    "KBL": 12,
    "NBL": 1,
    "PBA": 3
}

# =====================
# YARDIMCI
# =====================
def normalize(t):
    return re.sub(r"[^a-z]", "", t.lower())


def mac_format(q):
    return bool(re.search(r".+[-–].+", q))


def split_mac(q):
    return [x.strip() for x in re.split("[-–]", q)]


def guven_bar(p):
    return "█" * int(p / 10) + "░" * (10 - int(p / 10))


def implied_prob(o):
    return round((1 / o) * 100, 2)


def value_bet(model_p, o):
    return model_p > implied_prob(o)


# =====================
# TEAM BUL (GENEL)
# =====================
def find_team_football(name):
    target = normalize(name)
    for league in FOOTBALL_LEAGUES.values():
        r = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=HEADERS,
            params={"league": league, "season": 2024}
        ).json()
        for t in r.get("response", []):
            api = normalize(t["team"]["name"])
            if target in api or api in target:
                return t["team"]["id"], league
    return None, None


def find_team_basket(name):
    target = normalize(name)
    r = requests.get(
        "https://v1.basketball.api-sports.io/teams",
        headers=HEADERS
    ).json()
    for t in r.get("response", []):
        api = normalize(t["name"])
        if target in api or api in target:
            return t["id"]
    return None


# =====================
# FUTBOL TAHMİN
# =====================
def futbol_tahmin(mac):
    h, a = split_mac(mac)
    hid, league = find_team_football(h)
    aid, _ = find_team_football(a)

    if not hid or not aid:
        return None

    f = requests.get(
        "https://v3.football.api-sports.io/fixtures",
        headers=HEADERS,
        params={"team": hid, "next": 1}
    ).json()

    if not f.get("response"):
        return None

    fx = f["response"][0]
    fid = fx["fixture"]["id"]
    canli = fx["fixture"]["status"]["short"] != "NS"

    p = requests.get(
        "https://v3.football.api-sports.io/predictions",
        headers=HEADERS,
        params={"fixture": fid}
    ).json()

    pr = p["response"][0]["predictions"]["percent"]

    home = int(pr["home"][:-1])
    draw = int(pr["draw"][:-1])
    away = int(pr["away"][:-1])

    secim, guven = max(
        [("Ev Sahibi", home), ("Beraberlik", draw), ("Deplasman", away)],
        key=lambda x: x[1]
    )

    oran = round(1 + (100 / guven), 2)

    return {
        "spor": "⚽ Futbol",
        "secim": secim,
        "guven": guven,
        "oran": oran,
        "value": value_bet(guven, oran),
        "canli": canli
    }


# =====================
# BASKETBOL TAHMİN
# =====================
def basketbol_tahmin(mac):
    h, a = split_mac(mac)
    hid = find_team_basket(h)
    aid = find_team_basket(a)

    if not hid or not aid:
        return None

    g = requests.get(
        "https://v1.basketball.api-sports.io/games",
        headers=HEADERS,
        params={"team": hid, "season": 2024}
    ).json()

    if not g.get("response"):
        return None

    game = g["response"][0]
    gid = game["id"]
    canli = game["status"]["short"] != "NS"

    p = requests.get(
        "https://v1.basketball.api-sports.io/predictions",
        headers=HEADERS,
        params={"game": gid}
    ).json()

    pr = p["response"][0]
    hp = int(pr["percent"]["home"].replace("%", ""))
    ap = 100 - hp

    secim = "Ev Sahibi" if hp > ap else "Deplasman"
    guven = max(hp, ap)
    oran = round(1 + (100 / guven), 2)

    return {
        "spor": "🏀 Basketbol",
        "secim": secim,
        "guven": guven,
        "oran": oran,
        "value": value_bet(guven, oran),
        "canli": canli
    }


# =====================
# SESSION
# =====================
for k in ["messages", "kupon", "son", "aktif_mac"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k in ["messages", "kupon"] else None


# =====================
# UI
# =====================
st.title("💬 Tahminsor AI – Seviye 16")
st.caption("Gerçek API • Otomatik Lig • Futbol + Basketbol • Kupon")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input("Maç yaz: Takım A - Takım B")

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
                f"💰 Oran ~ {t['oran']}\n"
                f"🎯 Value Bet: {'🟢 VAR' if t['value'] else '🔴 YOK'}\n"
                f"⏱ Durum: {'Canlı (Cashout!)' if t['canli'] else 'Maç Önü'}\n\n"
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
    toplam_oran = 1
    for i, k in enumerate(st.session_state.kupon, 1):
        toplam_oran *= k["oran"]
        st.markdown(f"{i}. {k['mac']} → {k['secim']} ({k['oran']})")
    st.markdown(f"### 💰 Toplam Oran: {round(toplam_oran,2)}")
else:
    st.info("Kupon boş")
