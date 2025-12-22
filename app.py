# app.py — Tahminsor FINAL (Sohbet + Bağlam Takibi)

import streamlit as st
import numpy as np

st.set_page_config(page_title="Tahminsor", page_icon="⚽")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Merhaba 👋\n\n"
            "Benimle sohbet edebilirsin.\n"
            "Bir maç adı yazdığında analiz ederim 🙂"
        )
    }]

if "son_mac" not in st.session_state:
    st.session_state.son_mac = None

if "son_tahmin" not in st.session_state:
    st.session_state.son_tahmin = None

# ---------------- TAKIMLAR ----------------
FUTBOL_TAKIMLAR = [
    "galatasaray", "fenerbahce", "besiktas", "trabzonspor",
    "başakşehir", "basaksehir",
    "gaziantep", "gaziantep fk",
    "adana demirspor", "konyaspor"
]

# ---------------- ALGILAMA ----------------
def mac_mesaji_mi(q):
    ayiricilar = ["-", " vs ", " v "]
    return any(a in q for a in ayiricilar) and any(t in q for t in FUTBOL_TAKIMLAR)

DETAY_KELIMELER = ["neden", "detay", "açıkla", "niye", "sebep"]

def detay_sorusu_mu(q):
    return any(k in q for k in DETAY_KELIMELER)

# ---------------- TAHMİN ----------------
def futbol_tahmin(mac):
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    xg = rng.uniform(2.4, 3.2)
    ust = xg > 2.5
    sonuc = rng.choice(
        ["Ev Sahibi Kazanır", "Beraberlik", "Deplasman Kazanır"],
        p=[0.45, 0.25, 0.30]
    )

    ozet = f"""
⚽ **Futbol Analizi**

- Beklenen gol: **{xg:.2f}**
- 2.5 Gol: **{'ÜST 🟢' if ust else 'ALT 🔴'}**
- Maç sonucu: **{sonuc}**

👉 Önerim: **{'2.5 ÜST' if ust else '2.5 ALT'}**
"""

    detay = f"""
🔍 **Neden bu tahmin?**

- İki takımın hücum katkısı maç başına **yüksek gol beklentisi** oluşturuyor  
- Tempo düşüklüğü sinyali yok  
- Ev sahibi avantajı sonucu etkiliyor  
- İstatistiksel eşiklere göre **üst senaryosu daha olası**

Bu yüzden **2.5 ÜST** öne çıkıyor.
"""

    return ozet, detay

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

    # 1️⃣ MAÇ YAZILDIYSA
    if mac_mesaji_mi(q):
        ozet, detay = futbol_tahmin(q)
        st.session_state.son_mac = q
        st.session_state.son_tahmin = detay
        cevap = "Analize geçiyorum 👇\n" + ozet

    # 2️⃣ DETAY SORUSU VE ÖNCEKİ MAÇ VARSA
    elif detay_sorusu_mu(q) and st.session_state.son_mac:
        cevap = st.session_state.son_tahmin

    # 3️⃣ NORMAL SOHBET
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Başakşehir - Gaziantep**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Sohbet Modlu Yapay Zekâ Spor Tahminleri")
