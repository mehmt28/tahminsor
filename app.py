# app.py
# === Tahminsor | Sohbet + Spor Tahmin AI (FINAL STABLE) ===

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
    anahtarlar = [
        "basketbol", "futbol", "kbl", "nba", "euroleague",
        "süper lig", "super lig", "lig"
    ]
    return any(k in text.lower() for k in anahtarlar)


def barem_sorusu_mu(text):
    return bool(re.search(r"\d+[\.,]?\d*\s*(alt|üst)", text.lower()))


def kg_sorusu_mu(text):
    return "kg" in text.lower() or "karşılıklı" in text.lower()


def iki_bucuk_sorusu_mu(text):
    return "2.5" in text or "2,5" in text


# ------------------
# Session State
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

st.title("💬 Tahminsor – Yapay Zekâ Spor Sohbeti")
st.caption("Benimle sohbet edebilirsin. Maç adı yazarsan analiz ederim 🙂")

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

    # 1️⃣ Maç adı yazıldı
    if mac_format_var_mi(q):
        st.session_state.aktif_mac = q
        st.session_state.spor_turu = None
        st.session_state.son_tahmin = None

        cevap = (
            "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
            "Ligi veya spor türünü yazar mısın?\n"
            "Örn: **Türkiye Süper Ligi / Güney Kore basketbol ligi**"
        )

    # 2️⃣ Spor türü belirtildi
    elif st.session_state.aktif_mac and not st.session_state.spor_turu and lig_belirtildi_mi(q):
        st.session_state.spor_turu = q.lower()

        # Aynı maç = aynı tahmin
        np.random.seed(abs(hash(st.session_state.aktif_mac)) % 10**6)

        # -------- FUTBOL --------
        if "futbol" in q.lower() or "lig" in q.lower():
            ev = round(np.random.uniform(40, 55), 1)
            ber = round(np.random.uniform(20, 30), 1)
            dep = round(100 - ev - ber, 1)

            st.session_state.son_tahmin = {
                "tur": "futbol",
                "ev": ev,
                "ber": ber,
                "dep": dep
            }

            cevap = (
                "⚽ **Futbol Analizi (1X2)**\n\n"
                f"🏠 Ev Sahibi: **%{ev}**\n"
                f"🤝 Beraberlik: **%{ber}**\n"
                f"🚗 Deplasman: **%{dep}**\n\n"
                f"👉 **En olası sonuç:** "
                f"{'Ev Sahibi' if ev > max(ber, dep) else 'Beraberlik' if ber > dep else 'Deplasman'}\n\n"
                "Devam edebiliriz:\n"
                "- **KG var mı?**\n"
                "- **2.5 Alt/Üst?**\n"
                "- **İlk yarı sonucu?**"
            )

        # -------- BASKETBOL --------
        else:
            toplam = round(np.random.uniform(210, 225), 1)
            senaryo = "ALT" if toplam < 220 else "ÜST"

            st.session_state.son_tahmin = {
                "tur": "basketbol",
                "toplam": toplam,
                "senaryo": senaryo
            }

            cevap = (
                "🏀 **Basketbol Analizi**\n\n"
                f"🔢 Tahmini toplam sayı: **{toplam}**\n"
                f"📊 Genel senaryo: **{senaryo}**\n\n"
                "İstersen barem sorabilirsin:\n"
                "Örn: **181.5 alt olur mu?**"
            )

    # 3️⃣ FUTBOL – KG VAR MI
    elif st.session_state.son_tahmin and st.session_state.son_tahmin.get("tur") == "futbol" and kg_sorusu_mu(q):
        ev = st.session_state.son_tahmin["ev"]
        dep = st.session_state.son_tahmin["dep"]
        kg_oran = round((ev + dep) / 2, 1)

        cevap = (
            "⚽ **Karşılıklı Gol (KG) Analizi**\n\n"
            f"KG Var: **%{kg_oran}**\n"
            f"KG Yok: **%{round(100-kg_oran,1)}**\n\n"
            f"👉 **Önerim:** {'KG VAR' if kg_oran >= 50 else 'KG YOK'}"
        )

    # 4️⃣ FUTBOL – 2.5 ALT / ÜST
    elif st.session_state.son_tahmin and st.session_state.son_tahmin.get("tur") == "futbol" and iki_bucuk_sorusu_mu(q):
        ust_oran = round(np.random.uniform(45, 60), 1)

        cevap = (
            "⚽ **2.5 Gol Analizi**\n\n"
            f"2.5 ÜST: **%{ust_oran}**\n"
            f"2.5 ALT: **%{round(100-ust_oran,1)}**\n\n"
            f"👉 **Önerim:** {'2.5 ÜST' if ust_oran > 50 else '2.5 ALT'}"
        )

    # 5️⃣ BASKETBOL – BAREM
    elif st.session_state.son_tahmin and st.session_state.son_tahmin.get("tur") == "basketbol" and barem_sorusu_mu(q):
        match = re.search(r"(\d+[\.,]?\d*)\s*(alt|üst)", q.lower())
        barem = float(match.group(1).replace(",", "."))
        yon = match.group(2).upper()

        toplam = st.session_state.son_tahmin["toplam"]
        uyum = barem < toplam if yon == "ÜST" else barem > toplam

        cevap = (
            f"{'✅' if uyum else '⚠'} **{barem} {yon}**\n\n"
            f"Tahmini toplam: **{toplam}**\n"
            f"👉 {'Uyumlu' if uyum else 'Riskli'} seçim"
        )

    # 6️⃣ Normal sohbet
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Başakşehir - Gaziantep** veya **Anyang KGC - Samsung Thunders**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})

    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Yapay Zekâ Destekli Spor Tahmin Sohbeti")
