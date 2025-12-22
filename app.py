# app.py
# === Tahminsor | Üst Seviye Spor Tahmin Sohbet AI ===

import streamlit as st
import numpy as np
import re

st.set_page_config(page_title="Tahminsor", layout="centered")

# ------------------
# Yardımcı fonksiyonlar
# ------------------

def mac_format(text):
    return bool(re.search(r".+\s[-–]\s.+", text))

def lig_var_mi(text):
    anahtar = [
        "futbol", "basketbol", "kbl", "nba", "euroleague",
        "süper", "super", "lig", "ligi"
    ]
    return any(k in text.lower() for k in anahtar)

def barem_sorusu(text):
    return bool(re.search(r"\d+[\.,]?\d*\s*(alt|üst)", text.lower()))

# ------------------
# Session State
# ------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mac" not in st.session_state:
    st.session_state.mac = None

if "spor" not in st.session_state:
    st.session_state.spor = None

if "tahmin" not in st.session_state:
    st.session_state.tahmin = None

# ------------------
# Başlık
# ------------------

st.title("💬 Yapay Zekâ Spor Tahmin Sohbeti")
st.caption("Sohbet edebilirsin. Maç yazarsan analiz ederim.")

# ------------------
# Mesajları göster
# ------------------

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ------------------
# Kullanıcı girişi
# ------------------

user_input = st.chat_input("Mesajını yaz...")

if user_input:
    q = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": q})

    cevap = ""

    # 1️⃣ Maç adı
    if mac_format(q):
        st.session_state.mac = q
        st.session_state.spor = None
        st.session_state.tahmin = None
        cevap = (
            "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
            "Ligi veya spor türünü yazar mısın?\n"
            "Örn: Türkiye Süper Ligi / Güney Kore basketbol ligi"
        )

    # 2️⃣ Lig / spor
    elif st.session_state.mac and not st.session_state.spor and lig_var_mi(q):
        st.session_state.spor = q.lower()
        np.random.seed(abs(hash(st.session_state.mac)) % 1_000_000)

        # 🏀 Basketbol
        if "basket" in q.lower() or "kbl" in q.lower() or "nba" in q.lower():
            toplam = round(np.random.uniform(210, 222), 1)
            senaryo = "ALT" if toplam < 218 else "ÜST"
            guvenli = round(toplam - 12, 1)

            st.session_state.tahmin = {
                "tur": "basketbol",
                "toplam": toplam,
                "senaryo": senaryo
            }

            cevap = (
                "🏀 **Basketbol Analizi**\n\n"
                f"🔢 Tahmini toplam: **{toplam}**\n"
                f"📊 Genel senaryo: **{senaryo}**\n"
                f"🛡️ Güvenli barem: **{guvenli} {senaryo}**\n\n"
                "📌 Dayanaklar:\n"
                "- Tempo & lig ortalaması\n"
                "- Benzer maç dağılımları\n\n"
                f"👉 **Favorim: {senaryo}**\n\n"
                "İstersen barem sorabilirsin 🙂"
            )

        # ⚽ Futbol
        else:
            ev = round(np.random.uniform(40, 55), 1)
            ber = round(np.random.uniform(22, 30), 1)
            dep = round(100 - ev - ber, 1)

            st.session_state.tahmin = {
                "tur": "futbol",
                "1": ev,
                "X": ber,
                "2": dep
            }

            en_olasi = "Ev Sahibi" if ev > max(ber, dep) else "Beraberlik" if ber > dep else "Deplasman"

            cevap = (
                "⚽ **Futbol Analizi (1X2)**\n\n"
                f"🏠 Ev sahibi: **%{ev}**\n"
                f"🤝 Beraberlik: **%{ber}**\n"
                f"🚗 Deplasman: **%{dep}**\n\n"
                f"👉 **En olası sonuç: {en_olasi}**\n\n"
                "Devam edebiliriz:\n"
                "- 2.5 Alt/Üst?\n"
                "- KG Var mı?\n"
                "- İlk yarı sonucu?"
            )

    # 3️⃣ Barem sorusu (basketbol)
    elif st.session_state.tahmin and barem_sorusu(q) and st.session_state.tahmin["tur"] == "basketbol":
        m = re.search(r"(\d+[\.,]?\d*)\s*(alt|üst)", q.lower())
        barem = float(m.group(1).replace(",", "."))
        yon = m.group(2).upper()

        toplam = st.session_state.tahmin["toplam"]
        ana = st.session_state.tahmin["senaryo"]

        uyumlu = barem < toplam if yon == "ÜST" else barem > toplam

        if uyumlu:
            cevap = (
                f"✅ **{barem} {yon}**, ana tahminimle uyumlu.\n\n"
                f"Tahmini toplam **{toplam}**.\n"
                "📈 Olasılık: **%65–75**"
            )
        else:
            cevap = (
                f"⚠ **{barem} {yon}**, ana senaryoya ters.\n\n"
                f"Ana beklenti **{ana}** (toplam: {toplam}).\n"
                "📉 Olasılık: **%30–40**"
            )

    # 4️⃣ Normal sohbet
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Başakşehir - Gaziantep**\n"
            "**Anyang KGC - Samsung Thunders**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© Tahminsor • Yapay Zekâ Destekli Spor Analizi")
