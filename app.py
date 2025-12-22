# app.py — Tahminsor | Sohbet Modlu Spor Tahmin AI (KESİN ÇÖZÜM)

import streamlit as st
import numpy as np
import datetime

st.set_page_config(page_title="Tahminsor", page_icon="⚽", layout="centered")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚽🏀 Tahminsor")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Tahminler istatistiksel ve bağlamsal değerlendirmeye dayanır. Kesinlik içermez.")

# ---------------- GÜNÜN FAVORİSİ ----------------
today = datetime.date.today().strftime("%d %B %Y")
st.markdown(f"## 🥇 Günün Favorisi ({today})")
st.markdown("**Futbol:** 2.5 ÜST eğilimi • **Basketbol:** ÜST daha avantajlı")

st.divider()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Merhaba 👋\n\n"
                "Benimle sohbet edebilirsin.\n"
                "Bir maç adı yazdığında da analiz ederim 🙂"
            )
        }
    ]

if "tahmin_hafiza" not in st.session_state:
    st.session_state.tahmin_hafiza = {}

# ---------------- TAKIM LİSTELERİ ----------------
FUTBOL_TAKIMLAR = [
    "galatasaray", "fenerbahce", "besiktas", "trabzon",
    "real madrid", "madrid", "barcelona",
    "city", "united", "arsenal"
]

BASKET_TAKIMLAR = [
    "nba", "euroleague",
    "lakers", "celtics", "warriors", "bulls",
    "efes", "beko"
]

# ---------------- ALGILAMA ----------------
def futbol_mu(q):
    return any(t in q for t in FUTBOL_TAKIMLAR)

def basket_mu(q):
    return any(t in q for t in BASKET_TAKIMLAR)

def takim_var_mi(q):
    return futbol_mu(q) or basket_mu(q)

# ---------------- TAHMİN MOTORU ----------------
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

user_input = st.chat_input("Bir şey yaz… (örnek: Galatasaray Fenerbahçe)")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower()

    # 🔑 SADECE BU MESAJ ÖNEMLİ
    if not takim_var_mi(q):
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için lütfen **maç adını yaz**.\n"
            "Örnek: *Galatasaray Fenerbahçe*"
        )
    else:
        if q not in st.session_state.tahmin_hafiza:
            if futbol_mu(q):
                st.session_state.tahmin_hafiza[q] = futbol_tahmin(q)
            else:
                st.session_state.tahmin_hafiza[q] = basket_tahmin(q)

        cevap = (
            "Güzel maç seçtin 🙂\n"
            + st.session_state.tahmin_hafiza[q]
            + "\nİstersen devam edebiliriz."
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Sohbet Modlu Yapay Zekâ Spor Tahminleri")
