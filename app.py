# app.py
# === Streamlit | Sohbet + Spor Tahmin AI (Temiz Final) ===

import streamlit as st
import numpy as np
import re

st.set_page_config(page_title="Spor Tahmin AI", layout="centered")

# ------------------
# Yardımcı fonksiyonlar
# ------------------
def mac_format_var_mi(text):
    return bool(re.search(r"\b.+\s[-–]\s.+\b", text))


def barem_sorusu_mu(text):
    return bool(re.search(r"\d+[\.,]?\d*\s*(alt|üst)", text.lower()))


def lig_belirtildi_mi(text):
    anahtarlar = ["basketbol", "futbol", "kbl", "nba", "euroleague", "ligi"]
    return any(k in text.lower() for k in anahtarlar)


# ------------------
# Session state
# ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "aktif_mac" not in st.session_state:
    st.session_state.aktif_mac = None

if "spor_turu" not in st.session_state:
    st.session_state.spor_turu = None

if "son_tahmin" not in st.session_state:
    st.session_state.son_tahmin = None

# ------------------
# Başlık
# ------------------
st.title("💬 Yapay Zekâ Spor Tahmin Sohbeti")
st.caption("Benimle sohbet edebilirsin. Maç adı yazarsan analiz ederim.")

# ------------------
# Mesajları göster
# ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------
# Kullanıcı girişi
# ------------------
user_input = st.chat_input("Mesajını yaz…")

if user_input:
    q = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": q})

    cevap = None

    # 1️⃣ Maç formatı yazıldıysa
    if mac_format_var_mi(q):
        st.session_state.aktif_mac = q
        st.session_state.spor_turu = None
        st.session_state.son_tahmin = None
        cevap = (
            "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
            "Ligi veya spor türünü yazar mısın?\n"
            "Örn: Güney Kore basketbol ligi"
        )

    # 2️⃣ Lig / spor türü yazıldıysa
    elif st.session_state.aktif_mac and not st.session_state.spor_turu and lig_belirtildi_mi(q):
        st.session_state.spor_turu = q.lower()

        np.random.seed(abs(hash(st.session_state.aktif_mac)) % (10**6))
        tahmini_toplam = round(np.random.uniform(210, 225), 1)
        senaryo = "ALT" if tahmini_toplam < 220 else "ÜST"

        st.session_state.son_tahmin = {
            "toplam": tahmini_toplam,
            "senaryo": senaryo
        }

        cevap = (
            "Tamam 👍\n\n"
            "🏀 **Basketbol Analizi**\n\n"
            f"Tahmini toplam sayı: **{tahmini_toplam}**\n"
            f"Genel senaryo: **{senaryo}**\n"
            f"👉 Benim favorim: **{senaryo}**"
        )

    # 3️⃣ Barem sorusu
    elif st.session_state.son_tahmin and barem_sorusu_mu(q):
        match = re.search(r"(\d+[\.,]?\d*)\s*(alt|üst)", q.lower())
        barem = float(match.group(1).replace(",", "."))
        yon = match.group(2).upper()

        ana = st.session_state.son_tahmin["senaryo"]

        if yon != ana:
            cevap = (
                f"⚠ **{barem} {yon}**, ana senaryoma ters.\n\n"
                "Tempo düşerse veya maç sertleşirse olabilir.\n"
                "Yaklaşık olasılık: **%35–40**"
            )
        else:
            cevap = (
                f"✅ **{barem} {yon}**, ana senaryomla uyumlu.\n\n"
                "Yaklaşık olasılık: **%60–65**"
            )

    # 4️⃣ Sohbet / genel mesaj
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Anyang KGC - Samsung Thunders**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})

    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor • Yapay Zekâ Destekli Spor Tahmin Sohbeti")
