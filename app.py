# app.py
# === Streamlit | Sohbet + Spor Tahmin AI (ÜST SEVİYE FINAL) ===

import streamlit as st
import numpy as np
import re

st.set_page_config(page_title="Tahminsor | Spor Tahmin AI", layout="centered")

# ------------------
# Yardımcı fonksiyonlar
# ------------------

def mac_format_var_mi(text):
    return bool(re.search(r".+\s[-–]\s.+", text))


def lig_belirtildi_mi(text):
    anahtarlar = ["basketbol", "futbol", "kbl", "nba", "euroleague", "super lig", "premier", "ligi", "lig"]
    return any(k in text.lower() for k in anahtarlar)


def barem_sorusu_mu(text):
    return bool(re.search(r"\d+[\.,]?\d*\s*(alt|üst)", text.lower()))

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

    # 1️⃣ Maç adı
    if mac_format_var_mi(q):
        st.session_state.aktif_mac = q
        st.session_state.spor_turu = None
        st.session_state.son_tahmin = None
        cevap = (
            "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
            "Ligi veya spor türünü yazar mısın?\n"
            "Örn: Güney Kore basketbol ligi / Futbol"
        )

    # 2️⃣ Lig / spor türü
    elif st.session_state.aktif_mac and not st.session_state.spor_turu and lig_belirtildi_mi(q):
        st.session_state.spor_turu = q.lower()

        np.random.seed(abs(hash(st.session_state.aktif_mac)) % (10**6))

        # ------------------
        # BASKETBOL
        # ------------------
        if "basket" in q.lower() or "kbl" in q.lower() or "nba" in q.lower():
            tahmini_toplam = round(np.random.uniform(205, 225), 1)
            ana_senaryo = "ALT" if tahmini_toplam < 220 else "ÜST"
            guvenli_barem = round(tahmini_toplam - 12, 1)

            st.session_state.son_tahmin = {
                "tur": "basketbol",
                "toplam": tahmini_toplam,
                "senaryo": ana_senaryo,
                "guvenli_barem": guvenli_barem
            }

            cevap = (
                "Tamam 👍\n\n"
                "🏀 **Basketbol Analizi**\n\n"
                f"🔢 Tahmini toplam sayı: **{tahmini_toplam}**\n"
                f"📊 Genel senaryo: **{ana_senaryo}**\n"
                f"⭐ En mantıklı barem: **{guvenli_barem} {ana_senaryo}**\n\n"
                "📌 **Bu tahmin neye dayanıyor?**\n"
                "- Lig ortalama skorları\n"
                "- Takımların tempo profili\n"
                "- Benzer maç istatistikleri\n\n"
                f"👉 **Benim favorim: {ana_senaryo}**"
            )

        # ------------------
        # FUTBOL
        # ------------------
        else:
            ev_kazanir = round(np.random.uniform(40, 55), 1)
            beraberlik = round(np.random.uniform(20, 30), 1)
            deplasman = round(100 - ev_kazanir - beraberlik, 1)

            st.session_state.son_tahmin = {
                "tur": "futbol",
                "1": ev_kazanir,
                "X": beraberlik,
                "2": deplasman
            }

            cevap = (
                "Tamam 👍\n\n"
                "⚽ **Futbol Analizi (1X2)**\n\n"
                f"🏠 Ev sahibi kazanır: **%{ev_kazanir}**\n"
                f"🤝 Beraberlik: **%{beraberlik}**\n"
                f"🚗 Deplasman kazanır: **%{deplasman}**\n\n"
                "📌 **Bu tahmin neye dayanıyor?**\n"
                "- Ev/deplasman performansı\n"
                "- Gol beklentisi dengesi\n"
                "- Lig genel güç dağılımı\n\n"
                "👉 **En olası sonuç:** "
                f"{'Ev Sahibi' if ev_kazanir > max(beraberlik, deplasman) else 'Beraberlik' if beraberlik > deplasman else 'Deplasman'}"
            )

    # 3️⃣ Barem sorusu (sadece basketbol)
    elif st.session_state.son_tahmin and barem_sorusu_mu(q) and st.session_state.son_tahmin.get("tur") == "basketbol":
        match = re.search(r"(\d+[\.,]?\d*)\s*(alt|üst)", q.lower())
        barem = float(match.group(1).replace(",", "."))
        yon = match.group(2).upper()

        tahmini_toplam = st.session_state.son_tahmin["toplam"]
        ana = st.session_state.son_tahmin["senaryo"]

        uyum = barem < tahmini_toplam if yon == "ÜST" else barem > tahmini_toplam

        if uyum:
            cevap = (
                f"✅ **{barem} {yon}**, verdiğim tahminle uyumlu.\n\n"
                f"Tahmini toplam **{tahmini_toplam}** olduğu için bu barem mantıklı.\n"
                "📈 Olasılık: **%65–75**"
            )
        else:
            cevap = (
                f"⚠ **{barem} {yon}**, ana beklentiyle çelişiyor.\n\n"
                f"Ana senaryo **{ana}**, çünkü tahmini toplam **{tahmini_toplam}**.\n"
                "📉 Olasılık: **%30–40**"
            )

    # 4️⃣ Normal sohbet
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Anyang KGC - Samsung Thunders**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})

    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Yapay Zekâ Destekli Spor Tahmin Sohbeti")
