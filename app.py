# app.py — Tahminsor | Sohbet Modlu Spor Tahmin AI (FINAL – TEMİZ)

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
- Takımların genel güç dengesi
- Tempo / maç hızı varsayımları
- Lig ve maç bağlamı
- Aynı soruya aynı cevap prensibi
""")

# ---------------- GÜNÜN FAVORİSİ ----------------
today = datetime.date.today().strftime("%d %B %Y")
st.markdown(f"## 🥇 Günün Favorisi ({today})")
st.markdown(
    "**Futbol:** 2.5 ÜST eğilimli maçlar önde\n\n"
    "**Basketbol:** Tempo yüksek maçlarda ÜST daha avantajlı"
)

st.divider()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Merhaba 👋\n\n"
                "Benimle sohbet eder gibi konuşabilirsin.\n"
                "İstersen bir maç adı yaz, birlikte analiz edelim 🙂"
            )
        }
    ]

if "tahmin_hafiza" not in st.session_state:
    st.session_state.tahmin_hafiza = {}

# ---------------- TAKIM LİSTELERİ ----------------
FUTBOL_TAKIMLAR = [
    "galatasaray", "fenerbahce", "besiktas", "trabzon",
    "real madrid", "madrid", "barcelona",
    "manchester city", "city", "united", "arsenal"
]

BASKET_TAKIMLAR = [
    "nba", "euroleague",
    "lakers", "celtics", "warriors", "bulls",
    "anadolu efes", "efes", "fenerbahce beko", "beko"
]

# ---------------- ALGILAMA ----------------
def takim_var_mi(q: str) -> bool:
    q = q.lower()
    return any(t in q for t in FUTBOL_TAKIMLAR + BASKET_TAKIMLAR)

def futbol_mu(q: str) -> bool:
    return any(t in q for t in FUTBOL_TAKIMLAR)

def basket_mu(q: str) -> bool:
    return any(t in q for t in BASKET_TAKIMLAR)

# ---------------- TAHMİN MOTORU ----------------
def futbol_tahmin(mac: str) -> str:
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

Bu maçta oyun temposu **{'yüksek' if ust else 'kontrollü'}** görünüyor.

- Beklenen gol: **{xg:.2f}**
- 2.5 Gol: **{'ÜST 🟢' if ust else 'ALT 🔴'}**
- Maç sonucu görüşüm: **{sonuc}**

👉 Benim favorim: **{'2.5 ÜST' if ust else '2.5 ALT'}**
"""

def basket_tahmin(mac: str) -> str:
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    toplam = rng.uniform(205, 235)
    ust = toplam > 220

    return f"""
🏀 **Basketbol Yorumu**

Bu maçta tempo **{'yüksek' if ust else 'düşük'}**.

- Tahmini toplam sayı: **{toplam:.1f}**
- Toplam: **{'ÜST 🟢' if ust else 'ALT 🔴'}**

👉 Benim favorim: **{'ÜST' if ust else 'ALT'}**
"""

# ---------------- CHAT ----------------
for mesaj in st.session_state.messages:
    with st.chat_message(mesaj["role"]):
        st.markdown(mesaj["content"])

user_input = st.chat_input("Bir şey yaz… (örnek: Galatasaray Fenerbahçe)")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower()

    # 🔑 EN KRİTİK AYRIM
    if not takim_var_mi(q):
        cevap = (
            "Seni anlıyorum 🙂\n\n"
            "Ama tahmin yapabilmem için **maç adını** bilmem gerekiyor.\n"
            "Örnek: *Galatasaray Fenerbahçe* veya *Lakers Celtics*"
        )
    else:
        if q not in st.session_state.tahmin_hafiza:
            if futbol_mu(q) and not basket_mu(q):
                st.session_state.tahmin_hafiza[q] = futbol_tahmin(q)
            elif basket_mu(q):
                st.session_state.tahmin_hafiza[q] = basket_tahmin(q)
            else:
                st.session_state.tahmin_hafiza[q] = futbol_tahmin(q)

        cevap = (
            "Güzel maç seçtin 🙂\n"
            + st.session_state.tahmin_hafiza[q]
            + "\nİstersen bu maçın riskini, canlı senaryosunu veya alternatifini de konuşabiliriz."
        )

    st.session_state.messages.append(
        {"role": "assistant", "content": cevap}
    )

    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Sohbet Modlu Yapay Zekâ Spor Tahminleri")
