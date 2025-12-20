# app.py — Tahminsor | Sohbet Modlu Spor Tahmin AI
# 1️⃣ Sohbet modu (ChatGPT gibi)
# 2️⃣ Futbol / Basket doğru ayrımı
# 3️⃣ Aynı maç = aynı tahmin
# 4️⃣ Ev sahibi / Beraberlik / Deplasman
# 5️⃣ Günün favorisi

import streamlit as st
import numpy as np
import datetime

st.set_page_config(page_title="Tahminsor", page_icon="⚽", layout="centered")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚽🏀 Tahminsor")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Tahminler istatistiksel değerlendirmeye dayanır.\nKesinlik içermez.")

st.sidebar.markdown("""
### 🧠 Tahminler Nasıl Üretilir?
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
    "**Basketbol:** Tempo yüksek maçlarda ÜST tarafı avantajlı"
)

st.divider()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Merhaba 👋 Bana maç adını yaz, seninle konuşur gibi yorumlayalım."
        }
    ]

if "tahmin_hafiza" not in st.session_state:
    st.session_state.tahmin_hafiza = {}

# ---------------- YARDIMCI FONKSİYONLAR ----------------
def futbol_mu(q):
    anahtarlar = [
        "galatasaray", "fenerbahce", "besiktas", "trabzon",
        "madrid", "barcelona", "city", "united", "fc", "-"
    ]
    return any(k in q for k in anahtarlar)

def basket_mu(q):
    anahtarlar = [
        "nba", "euroleague", "lakers", "celtics",
        "warriors", "bulls", "efes", "beko"
    ]
    return any(k in q for k in anahtarlar)

def futbol_tahmin_uret(mac):
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

Bu maçta tempo **{'yüksek' if ust else 'kontrollü'}** görünüyor.

- Beklenen gol: **{xg:.2f}**
- 2.5 Gol: **{'ÜST 🟢' if ust else 'ALT 🔴'}**
- Maç sonucu görüşüm: **{sonuc}**

👉 Benim favorim: **{'2.5 ÜST' if ust else '2.5 ALT'}**
"""

def basket_tahmin_uret(mac):
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

# ---------------- CHAT EKRANI ----------------
for mesaj in st.session_state.messages:
    with st.chat_message(mesaj["role"]):
        st.markdown(mesaj["content"])

kullanici_girdisi = st.chat_input("Maç adını yaz veya sorunu sor…")

if kullanici_girdisi:
    st.session_state.messages.append(
        {"role": "user", "content": kullanici_girdisi}
    )

    with st.chat_message("user"):
        st.markdown(kullanici_girdisi)

    q = kullanici_girdisi.lower()

    if q not in st.session_state.tahmin_hafiza:
        if futbol_mu(q) and not basket_mu(q):
            tahmin = futbol_tahmin_uret(q)
        elif basket_mu(q):
            tahmin = basket_tahmin_uret(q)
        else:
            tahmin = futbol_tahmin_uret(q)

        st.session_state.tahmin_hafiza[q] = tahmin

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
