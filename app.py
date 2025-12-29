# ===============================
# Tahminsor – FAZ 7 FINAL
# Hybrid Fixture • Futbol + Basket
# ===============================

import streamlit as st
import requests
import re
from datetime import datetime, timedelta

# -------------------------------
# AYARLAR
# -------------------------------
st.set_page_config(
    page_title="Tahminsor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_KEY = "2aafffec4c31cf146173e2064c6709d1"
HEADERS = {"x-apisports-key": API_KEY}

# -------------------------------
# YARDIMCI
# -------------------------------
def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())

def mac_format(q):
    return bool(re.search(r".+[-–].+", q))

def guven_bar(p):
    dolu = int(p / 10)
    return "█" * dolu + "░" * (10 - dolu)

# -------------------------------
# FUTBOL FIXTURE BUL (HYBRID)
# -------------------------------
def find_football_fixture(home, away):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "from": datetime.now().strftime("%Y-%m-%d"),
        "to": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    }

    r = requests.get(url, headers=HEADERS, params=params).json()
    if not r.get("response"):
        return None

    h, a = norm(home), norm(away)

    for f in r["response"]:
        fh = norm(f["teams"]["home"]["name"])
        fa = norm(f["teams"]["away"]["name"])
        if (h in fh and a in fa) or (h in fa and a in fh):
            return f
    return None

def football_predict(fix):
    fid = fix["fixture"]["id"]
    p = requests.get(
        "https://v3.football.api-sports.io/predictions",
        headers=HEADERS,
        params={"fixture": fid}
    ).json()

    if not p.get("response"):
        return None

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
        "tahmin": secim,
        "guven": guven,
        "oran": round(1 + (100 / guven), 2)
    }

# -------------------------------
# BASKET FIXTURE BUL (HYBRID)
# -------------------------------
def find_basket_fixture(home, away):
    url = "https://v1.basketball.api-sports.io/games"
    params = {"season": 2024}

    r = requests.get(url, headers=HEADERS, params=params).json()
    if not r.get("response"):
        return None

    h, a = norm(home), norm(away)

    for g in r["response"]:
        gh = norm(g["teams"]["home"]["name"])
        ga = norm(g["teams"]["away"]["name"])
        if (h in gh and a in ga) or (h in ga and a in gh):
            return g
    return None

def basket_predict(game):
    gid = game["id"]
    p = requests.get(
        "https://v1.basketball.api-sports.io/predictions",
        headers=HEADERS,
        params={"game": gid}
    ).json()

    if not p.get("response"):
        return None

    pr = p["response"][0]["percent"]
    h = int(pr["home"].replace("%", ""))
    a = 100 - h

    secim = "Ev Sahibi" if h > a else "Deplasman"
    guven = max(h, a)

    return {
        "spor": "Basketbol",
        "tahmin": secim,
        "guven": guven,
        "oran": round(1 + (100 / guven), 2)
    }

# -------------------------------
# SESSION
# -------------------------------
if "kupon" not in st.session_state:
    st.session_state.kupon = []

# -------------------------------
# UI
# -------------------------------
sol, sag = st.columns([3, 1])

with sol:
    st.title("💬 Tahminsor")
    st.caption("Hybrid Fixture • Futbol & Basketbol")

    q = st.chat_input("Maç yaz → Takım A - Takım B")

    if q and mac_format(q):
        home, away = [x.strip() for x in re.split("[-–]", q)]

        # Önce futbol dene
        fix = find_football_fixture(home, away)
        if fix:
            t = football_predict(fix)
        else:
            game = find_basket_fixture(home, away)
            t = basket_predict(game) if game else None

        if not t:
            st.error("❌ Veri bulunamadı (lig / isim uyuşmuyor)")
        else:
            st.success(f"✅ {t['spor']} Maçı Bulundu")
            st.markdown(
                f"""
**Tahmin:** {t['tahmin']}  
**Oran:** {t['oran']}  
**Güven:** %{t['guven']} {guven_bar(t['guven'])}
"""
            )
            if st.button("🧾 Kupona Ekle"):
                st.session_state.kupon.append({
                    "mac": q,
                    "spor": t["spor"],
                    "tahmin": t["tahmin"],
                    "oran": t["oran"],
                    "guven": t["guven"]
                })

with sag:
    st.markdown("## 🧾 Kupon")
    st.markdown(
        "<div style='background:#f5f5f5;padding:10px;border-radius:10px'>",
        unsafe_allow_html=True
    )

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        toplam_oran = 1
        toplam_guven = 0

        for i, k in enumerate(st.session_state.kupon, 1):
            toplam_oran *= k["oran"]
            toplam_guven += k["guven"]
            st.markdown(
                f"**{i}. {k['mac']}**  \n{k['tahmin']} | {k['oran']}"
            )

        st.markdown("---")
        st.markdown(f"**Toplam Oran:** {round(toplam_oran,2)}")
        st.markdown(f"**Kupon Güveni:** %{int(toplam_guven/len(st.session_state.kupon))}")

    st.markdown("</div>", unsafe_allow_html=True)

st.caption("© Tahminsor • FAZ 7")
