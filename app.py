# app.py
# === Tahminsor | Sohbet + Spor Tahmin AI (STABLE FINAL) ===

import streamlit as st
import numpy as np
import re

st.set_page_config(
    page_title="Tahminsor | Spor Tahmin AI",
    layout="centered"
)

# -------------------------------------------------
# Yardımcı Fonksiyonlar
# -------------------------------------------------

def mac_format_var_mi(text: str) -> bool:
    """Başakşehir - Gaziantep gibi maç formatı var mı"""
    return bool(re.search(r".+\s[-–]\s.+", text))


def lig_belirtildi_mi(text: str) -> bool:
    anahtarlar = [
        "futbol", "basketbol",
        "süper lig", "super lig",
        "nba", "kbl", "euroleague", "lig"
    ]
    return any(k in text.lower() for k in anahtarlar)


# -------------------------------------------------
# Session State
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "aktif_mac" not in st.session_state:
    st.session_state.aktif_mac = None

if "spor_turu" not in st.session_state:
    st.session_state.spor_turu = None

if "son_tahmin" not in st.session_state:
    st.session_state.son_tahmin = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# -------------------------------------------------
# Başlık
# -------------------------------------------------

st.title("💬 Tahminsor – Yapay Zekâ Spor Sohbeti")
st.caption("Maç yaz → analiz al → kupon oluştur 💰")

# -------------------------------------------------
# Önceki mesajlar
# -------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# Kullanıcı girişi
# -------------------------------------------------

user_input = st.chat_input("Mesajını yaz…")

if user_input:
    q = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": q})
    cevap = ""

    # 1️⃣ Maç adı girildi
    if mac_format_var_mi(q):
        st.session_state.aktif_mac = q
        st.session_state.spor_turu = None
        st.session_state.son_tahmin = None

        cevap = (
            "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
            "Ligi veya spor türünü yazar mısın?\n"
            "Örn: **Türkiye Süper Ligi** / **Güney Kore basketbol ligi**"
        )

    # 2️⃣ Lig / spor türü girildi → analiz
    elif st.session_state.aktif_mac and not st.session_state.spor_turu and lig_belirtildi_mi(q):
        st.session_state.spor_turu = q.lower()

        # Aynı maç için her zaman aynı tahmin gelsin
        np.random.seed(abs(hash(st.session_state.aktif_mac)) % 10**6)

        # FUTBOL
        if "futbol" in q.lower() or "lig" in q.lower():
            ev = round(np.random.uniform(42, 55), 1)
            ber = round(np.random.uniform(20, 28), 1)
            dep = round(100 - ev - ber, 1)

            oran = round(1 + (100 / ev), 2)
            guven = int(ev)

            st.session_state.son_tahmin = {
                "tur": "futbol",
                "secim": "Ev Sahibi",
                "oran": oran,
                "guven": guven
            }

            cevap = (
                "⚽ **Futbol Analizi (1X2)**\n\n"
                f"🏠 Ev Sahibi: **%{ev}** (Oran ~{oran})\n"
                f"🤝 Beraberlik: **%{ber}**\n"
                f"🚗 Deplasman: **%{dep}**\n\n"
                f"👉 **Önerim:** Ev Sahibi\n"
                f"📊 **Güven:** %{guven}\n\n"
                "İstersen **kupon yap** yazabilirsin 🧾"
            )

        # BASKETBOL
        else:
            toplam = round(np.random.uniform(210, 225), 1)
            senaryo = "ALT" if toplam < 220 else "ÜST"
            oran = round(np.random.uniform(1.6, 1.9), 2)
            guven = min(int(abs(220 - toplam) + 55), 85)

            st.session_state.son_tahmin = {
                "tur": "basketbol",
                "secim": senaryo,
                "oran": oran,
                "guven": guven
            }

            cevap = (
                "🏀 **Basketbol Analizi**\n\n"
                f"🔢 Tahmini toplam sayı: **{toplam}**\n"
                f"📌 Ana senaryo: **{senaryo}**\n"
                f"💰 Oran: **{oran}**\n"
                f"📊 **Güven:** %{guven}\n\n"
                "İstersen **kupon yap** yazabilirsin 🧾"
            )

    # 3️⃣ Kupona ekle
    elif "kupon" in q.lower() and st.session_state.son_tahmin:
        st.session_state.kupon.append({
            "mac": st.session_state.aktif_mac,
            **st.session_state.son_tahmin
        })
        cevap = "✅ Tahmin kupona eklendi. Aşağıda görebilirsin 🧾"

    # 4️⃣ Normal sohbet
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Bir maç yazarsan analiz ederim.\n"
            "Örn: **Başakşehir - Gaziantep**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

# -------------------------------------------------
# ALT PANEL – KU P O N
# -------------------------------------------------

st.subheader("🧾 Güncel Kupon")

if not st.session_state.kupon:
    st.info("Henüz kupona eklenmiş tahmin yok.")
else:
    toplam_oran = 1.0
    for i, k in enumerate(st.session_state.kupon, 1):
        toplam_oran *= k["oran"]
        st.markdown(
            f"**{i}.** {k['mac']} → **{k['secim']}** (Oran {k['oran']})"
        )

    st.markdown(f"💰 **Toplam Oran:** {round(toplam_oran, 2)}")

# -------------------------------------------------
# ALT PANEL – GÜVEN BAR
# -------------------------------------------------

if st.session_state.son_tahmin:
    st.subheader("📊 Güven Seviyesi")
    g = st.session_state.son_tahmin["guven"]
    st.progress(g / 100)
    st.markdown(f"**%{g} güven**")

st.caption("© tahminsor.site • Yapay Zekâ Destekli Spor Tahmin Sistemi")
