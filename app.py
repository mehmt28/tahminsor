import streamlit as st
import requests
import os
import re

st.set_page_config(page_title="TahminSor", layout="wide")

# ==================================================
# API KEY (ASLA KEYERROR VERMEZ)
# ==================================================
API_KEY = None
try:
    API_KEY = st.secrets.get("API_SPORTS_KEY")
except Exception:
    API_KEY = None

if not API_KEY:
    API_KEY = os.getenv("API_SPORTS_KEY")

API_ACTIVE = API_KEY is not None

HEADERS = {
    "x-apisports-key": API_KEY
} if API_ACTIVE else {}

# ==================================================
# SESSION STATE
# ==================================================
if "tahmin" not in st.session_state:
    st.session_state.tahmin = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# ==================================================
# YARDIMCI
# ==================================================
def mac_format(text):
    return bool(re.search(r".+\s*-\s*.+", text))

def futbol_tahmin(mac):
    home, away = [x.strip() for x in mac.split("-")]

    # 1️⃣ Fixture bul
    fix_res = requests.get(
        "https://v3.football.api-sports.io/fixtures",
        headers=HEADERS,
        params={"team": home, "next": 1}
    ).json()

    if not fix_res.get("response"):
        return None

    fixture = fix_res["response"][0]
    fixture_id = fixture["fixture"]["id"]

    # 2️⃣ Prediction çek
    pred_res = requests.get(
        "https://v3.football.api-sports.io/predictions",
        headers=HEADERS,
        params={"fixture": fixture_id}
    ).json()

    if not pred_res.get("response"):
        return None

    p = pred_res["response"][0]["predictions"]["percent"]

    home_p = int(p["home"].replace("%", ""))
    draw_p = int(p["draw"].replace("%", ""))
    away_p = int(p["away"].replace("%", ""))

    best = max(
        [("Ev Sahibi", home_p), ("Beraberlik", draw_p), ("Deplasman", away_p)],
        key=lambda x: x[1]
    )

    return {
        "match": mac,
        "prediction": best[0],
        "confidence": best[1],
        "detail": f"Ev %{home_p} | Ber %{draw_p} | Dep %{away_p}"
    }

# ==================================================
# UI
# ==================================================
st.title("⚽ TahminSor – Gerçek API Destekli")

left, right = st.columns([2, 1])

with left:
    mac = st.text_input("Maç gir (örn: Genk - Club Brugge)", key="mac")

    col1, col2 = st.columns(2)
    tahmin_btn = col1.button("🔮 Tahmin Al")
    kupon_btn = col2.button("➕ Kupona Ekle")

    if tahmin_btn and mac_format(mac):
        if not API_ACTIVE:
            st.error("❌ API KEY aktif değil")
        else:
            t = futbol_tahmin(mac)
            if not t:
                st.error("❌ Veri bulunamadı (lig / isim uyuşmuyor)")
            else:
                st.session_state.tahmin = t

    if st.session_state.tahmin:
        t = st.session_state.tahmin
        st.markdown(f"""
### 📊 Tahmin

**Maç:** {t['match']}  
**Öneri:** {t['prediction']}  
**Güven:** %{t['confidence']}  
_{t['detail']}_
""")

    if kupon_btn and st.session_state.tahmin:
        st.session_state.kupon.append(st.session_state.tahmin)
        st.success("✅ Kupona eklendi")

with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for i, k in enumerate(st.session_state.kupon, 1):
            st.markdown(
                f"**{i}. {k['match']}**  \n"
                f"{k['prediction']} | %{k['confidence']}"
            )

        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon.clear()
            st.success("Kupon temizlendi")

st.caption("TahminSor • Gerçek API • Stabil Build")
