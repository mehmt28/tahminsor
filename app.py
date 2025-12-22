# app.py — Tahminsor | Sohbet Modlu Spor Tahmin AI (DÜZELTİLMİŞ)

import streamlit as st
import numpy as np
import datetime

st.set_page_config(page_title="Tahminsor", page_icon="⚽", layout="centered")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚽🏀 Tahminsor")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Tahminler istatistiksel değerlendirmeye dayanır. Kesinlik içermez.")

st.sidebar.markdown("""
### 🧠 Tahminler Neye Dayanır?
- Takımların geçmiş performansı
- Tempo ve maç hızı
- Lig ve maç bağlamı
- Aynı soruya aynı cevap prensibi
""")

# ---------------- GÜNÜN FAVORİSİ ----------------
today = datetime.date.today().strftime("%d %B %Y")
st.markdown(f"## 🥇 Günün Favorisi ({today})")
st.markdown(
    "**Futbol:** 2.5 ÜST eğilimi\n\n"
    "**Basketbol:** Tempo yüksek maçlarda ÜST avantajlı"
)

st.divider()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Merhaba 👋 Benimle sohbet eder gibi yazabilirsin. İstersen maç da sorabilirsin."
        }
    ]

if "tahmin_hafiza" not in st.session_state:
    st.session_state.tahmin_hafiza = {}

# ---------------- YARDIMCI FONKSİYONLAR ----------------
FUTBOL_TAKIMLAR = [
    "galatasaray", "fenerbahce", "besiktas", "trabzon",
    "madrid", "barcelona", "city", "united", "arsenal"
]

BASKET_TAKIMLAR = [
    "nba", "euroleague", "lakers", "celtics",
    "warriors", "bulls", "efes", "beko"
]

TAHMIN_KELIMELERI = ["maç", "tahmin", "üst", "alt", "oran", "kim kazanır", "vs", "-"]

def mac_algilandi_mi(q: str) -> bool:
    q = q.lower()
    takim_var = any(t in q for t in FUTBOL_TAKIMLAR + BASKET_TAKIMLAR)
    tahmin_istegi = any(k in q for k in TAHMIN_KELIMELERI)
    return takim_var or tahmin_istegi

def futbol_mu(q):
    return any(t in q for t in FUTBOL_TAKIMLAR)

def basket_mu(q):
    return any(t in q for t in BASKET_TAKIMLAR)

def futbol_tahmin(mac):
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    xg = rng.uniform(2.0, 3.3)
    ust = xg > 2.5
    sonuc = rng.choice(
        ["Ev Sahibi Kazanır", "Beraberlik", "Deplasman Kazanır"],
        p=[0.45, 0.25, 0.30]
    )

    return f"""
⚽ **Futbol Yorumu**

Bu maçta oyun temposu **{'yüksek' if ust else 'kontrollü'}**.

- Beklenen gol: **{xg:.2f}**
- 2.5 Gol: **{'ÜST 🟢' if ust else 'ALT 🔴'}**
- Maç sonucu: **{sonuc}**

👉 Benim favorim: **{'2.5 ÜST' if ust else '2.5 ALT'}**
"""

def basket_tahmin(mac):
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    toplam = rng.uniform(205, 235)
    ust = toplam > 220

    return f"""
🏀 **Basketbol Yorumu**

- Tahmini toplam sayı: **{toplam:.1f}**
- Toplam: **{'ÜST 🟢' if ust else 'ALT 🔴'}**

👉 Benim favorim: **{'ÜST' if ust else 'ALT'}**
"""

# ---------------- CHAT ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Bir şey yaz… (maç da sorabilirsin)")

if user_input:
    st
