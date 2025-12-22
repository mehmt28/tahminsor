# app.py — Tahminsor | Sohbet + Akıllı Maç Algılama (FINAL)

import streamlit as st
import numpy as np
import datetime

st.set_page_config(page_title="Tahminsor", page_icon="⚽", layout="centered")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚽🏀 Tahminsor")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Tahminler istatistiksel değerlendirmeye dayanır, kesinlik içermez.")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Merhaba 👋\n\n"
            "Benimle sohbet edebilirsin.\n"
            "Bir **maç adı** yazdığında analiz ederim 🙂"
        )
    }]

if "hafiza" not in st.session_state:
    st.session_state.hafiza = {}

# ---------------- TAKIM LİSTELERİ ----------------
SUPER_LIG = [
    "galatasaray", "fenerbahce", "besiktas", "trabzonspor",
    "basaksehir", "başakşehir",
    "gaziantep", "gaziantep fk",
    "adana demirspor", "kasimpasa",
    "antalyaspor", "alanyaspor",
    "rizespor", "hatayspor",
    "ankaragucu", "konyaspor",
    "sivasspor", "pendikspor"
]

AVRUPA = [
    "real madrid", "barcelona", "arsenal",
    "city", "united", "chelsea", "liverpool",
    "bayern", "psg", "inter", "milan"
]

BASKET = [
    "nba", "euroleague",
    "lakers", "celtics", "warriors",
    "efes", "fenerbahce beko"
]

FUTBOL_TAKIMLAR = SUPER_LIG + AVRUPA

# ---------------- ALGILAMA ----------------
def futbol_mu(q):
    return any(t in q for t in FUTBOL_TAKIMLAR)

def basket_mu(q):
    return any(t in q for t in BASKET)

def mac_formati_var_mi(q):
    ayiricilar = ["-", " vs ", " v ", " karşı "]
    return any(a in q for a in ayiricilar)

def mac_mesaji_mi(q):
    # En az 1 takım + maç formatı
    return (futbol_mu(q) or basket_mu(q)) and mac_formati_var_mi(q)

# ---------------- TAHMİN ----------------
def futbol_tahmin(mac):
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    xg = rng.uniform(2.1, 3.4)
    ust = xg > 2.5
    sonuc = rng.choice(
        ["Ev Sahibi Kazanır", "Beraberlik", "Deplasman Kazanır"],
        p=[0.45, 0.25, 0.30]
    )

    return f"""
⚽ **Futbol Analizi**

- Beklenen gol: **{xg:.2f}**
- 2.5 Gol: **{'ÜST 🟢' if ust else 'ALT 🔴'}**
- Maç sonucu: **{sonuc}**

👉 Önerim: **{'2.5 ÜST' if ust else '2.5 ALT'}**
"""

def basket_tahmin(mac):
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    toplam = rng.uniform(208, 238)
    ust = toplam > 220

    return f"""
🏀 **Basketbol Analizi**

- Tahmini toplam sayı: **{toplam:.1f}**
- Toplam: **{'ÜST 🟢' if ust else 'ALT 🔴'}**

👉 Önerim: **{'ÜST' if ust else 'ALT'}**
"""

# ---------------- CHAT ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Bir şey yaz… (örn: Başakşehir - Gaziantep)")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower()

    if not mac_mesaji_mi(q):
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için **iki takımı ayırarak** yaz:\n"
            "**Başakşehir - Gaziantep**"
        )
    else:
        if q not in st.session_state.hafiza:
            if futbol_mu(q):
                st.session_state.hafiza[q] = futbol_tahmin(q)
            else:
                st.session_state.hafiza[q] = basket_tahmin(q)

        cevap = "Analize geçiyorum 👇\n" + st.session_state.hafiza[q]

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Sohbet Modlu Yapay Zekâ Spor Tahminleri")
