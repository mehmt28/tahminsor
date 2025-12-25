# app.py
import streamlit as st
import requests
import re

st.set_page_config(page_title="Tahminsor | Gerçek Tahmin", layout="wide")

# =====================
# API
# =====================
API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

API_FOOT_FIX = "https://v3.football.api-sports.io/fixtures"
API_FOOT_PRED = "https://v3.football.api-sports.io/predictions"
API_BASKET_GAMES = "https://v1.basketball.api-sports.io/games"
API_BASKET_PRED = "https://v1.basketball.api-sports.io/predictions"

# =====================
# TAKIM ALIAS (ÇOK KRİTİK)
# =====================
TEAM_ALIASES = {
    "man utd": "Manchester United",
    "man.utd": "Manchester United",
    "newcastle utd": "Newcastle United",
    "genk": "KRC Genk",
    "club brugge": "Club Brugge KV",
    "road warriors": "NLEX Road Warriors",
    "san miguel": "San Miguel Beermen",
    "al jabalin": "Al-Jabalain",
    "al ula": "Al-Ula FC"
}

def normalize_team(name):
    n = name.lower().strip()
    return TEAM_ALIASES.get(n, name)

# =====================
# YARDIMCI
# =====================
def mac_format(q):
    return bool(re.search(r"\w+\s*[-–]\s*\w+", q))

def implied_prob(oran):
    return round((1 / oran) * 100, 2)

def value_bet(model_pct, oran):
    return model_pct > implied_prob(oran)

def guven_bar(pct):
    bars = int(pct / 10)
    return "█" * bars + "░" * (10 - bars)

def spor_belirle(mac):
    basket_ipucu = ["kgc", "thunders", "bullets", "breakers", "warriors"]
    m = mac.lower()
    return "basketbol" if any(x in m for x in basket_ipucu) else "futbol"

# =====================
# FUTBOL
# =====================
def futbol_tahmin(mac):
    home, _ = [normalize_team(x.strip()) for x in re.split("[-–]", mac)]

    f = requests.get(API_FOOT_FIX, headers=HEADERS, params={"team": home, "next": 1}).json()
    if not f.get("response"):
        return None

    fix_id = f["response"][0]["fixture"]["id"]

    p = requests.get(API_FOOT_PRED, headers=HEADERS, params={"fixture": fix_id}).json()
    if not p.get("response"):
        return None

    perc = p["response"][0]["predictions"]["percent"]
    home_pct = int(perc["home"].replace("%", ""))
    draw_pct = int(perc["draw"].replace("%", ""))
    away_pct = int(perc["away"].replace("%", ""))

    secim, guven = max(
        [("Ev Sahibi", home_pct), ("Beraberlik", draw_pct), ("Deplasman", away_pct)],
        key=lambda x: x[1]
    )

    oran = round(1 + (100 / guven), 2)
    value = value_bet(guven, oran)

    return {
        "spor": "futbol",
        "secim": secim,
        "guven": guven,
        "oran": oran,
        "value": value
    }

# =====================
# BASKETBOL
# =====================
def basketbol_tahmin(mac):
    home, _ = [normalize_team(x.strip()) for x in re.split("[-–]", mac)]

    g = requests.get(
        API_BASKET_GAMES,
        headers=HEADERS,
        params={"team": home, "season": 2024}
    ).json()

    if not g.get("response"):
        return None

    game_id = g["response"][0]["id"]

    p = requests.get(API_BASKET_PRED, headers=HEADERS, params={"game": game_id}).json()
    if not p.get("response"):
        return None

    pr = p["response"][0]
    home_pct = int(pr["percent"]["home"].replace("%", ""))
    away_pct = 100 - home_pct

    secim = "Ev Sahibi" if home_pct > away_pct else "Deplasman"
    guven = max(home_pct, away_pct)
    oran = round(1 + (100 / guven), 2)
    value = value_bet(guven, oran)

    return {
        "spor": "basketbol",
        "secim": secim,
        "guven": guven,
        "oran": oran,
        "value": value
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
left, right = st.columns([3, 1])

with left:
    st.title("💬 Tahminsor")
    st.caption("Alias Destekli • Gerçek API • Stabil Final")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    q = st.chat_input("Maç yaz: Takım A - Takım B")

    if q:
        st.session_state.messages.append({"role": "user", "content": q})

        if mac_format(q):
            st.session_state.aktif_mac = q
            spor = spor_belirle(q)
            t = basketbol_tahmin(q) if spor == "basketbol" else futbol_tahmin(q)

            if not t:
                cevap = "❌ Veri bulunamadı (takım adı farklı olabilir)"
            else:
                st.session_state.son = t
                cevap = (
                    f"🔍 {t['spor'].upper()} ANALİZİ\n\n"
                    f"👉 Tahmin: **{t['secim']}**\n"
                    f"📊 Güven: %{t['guven']} {guven_bar(t['guven'])}\n"
                    f"💰 Oran: {t['oran']}\n"
                    f"🎯 Value Bet: {'🟢 VAR' if t['value'] else '🔴 YOK'}\n\n"
                    f"Kupona eklemek için **kupon ekle** yaz"
                )

        elif "kupon ekle" in q.lower() and st.session_state.son:
            st.session_state.kupon.append({
                "mac": st.session_state.aktif_mac,
                "secim": st.session_state.son["secim"],
                "oran": st.session_state.son["oran"],
                "guven": st.session_state.son["guven"],
                "value": st.session_state.son.get("value", False)
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
        toplam_oran = 1
        for i, k in enumerate(st.session_state.kupon, 1):
            toplam_oran *= k["oran"]
            st.markdown(
                f"{i}. {k['mac']} → {k['secim']} ({k['oran']}) "
                f"{'🟢' if k.get('value') else ''}"
            )

        st.markdown(f"### 💰 Toplam Oran: {round(toplam_oran, 2)}")

st.caption("© Tahminsor | Final Stabil")
