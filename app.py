# app.py
# === Tahminsor | Sohbet + Spor Tahmin AI (FINAL PRO SÜRÜM) ===

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
    anahtarlar = ["futbol", "basketbol", "kbl", "nba", "euroleague", "süper lig", "super lig", "lig"]
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

for key in ["messages", "aktif_mac", "spor_turu", "son_tahmin", "kupon"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["messages", "kupon"] else None

# ------------------
# Başlık
# ------------------

st.title("💬 Tahminsor – Yapay Zekâ Spor Sohbeti")
st.caption("Maç yaz → analiz al → oran & kupon oluştur 💰")

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
            "Örn: Türkiye Süper Ligi / Güney Kore basketbol ligi"
        )

    # 2️⃣ Lig / spor türü
    elif st.session_state.aktif_mac and not st.session_state.spor_turu and lig_belirtildi_mi(q):
        st.session_state.spor_turu = q.lower()
        np.random.seed(abs(hash(st.session_state.aktif_mac)) % 10**6)

        # FUTBOL
        if "futbol" in q.lower() or "lig" in q.lower():
            ev = round(np.random.uniform(40, 55), 1)
            ber = round(np.random.uniform(20, 30), 1)
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
                f"👉 **Öneri:** Ev Sahibi\n\n"
                f"📊 Güven Seviyesi: **%{guven}**"
            )

        # BASKETBOL
        else:
            toplam = round(np.random.uniform(210, 225), 1)
            senaryo = "ALT" if toplam < 220 else "ÜST"
            oran = round(np.random.uniform(1.6, 1.9), 2)
            guven = int(abs(220 - toplam) + 50)

            st.session_state.son_tahmin = {
                "tur": "basketbol",
                "secim": senaryo,
                "oran": oran,
                "guven": min(guven, 85)
            }

            cevap = (
                "🏀 **Basketbol Analizi**\n\n"
                f"🔢 Tahmini toplam sayı: **{toplam}**\n"
                f"📊 Ana senaryo: **{senaryo}**\n"
                f"💰 Oran: **{oran}**\n"
                f"📊 Güven Seviyesi: **%{st.session_state.son_tahmin['guven']}**"
            )

    # 3️⃣ Kupona ekle / göster
    elif "kupon" in q.lower() and st.session_state.son_tahmin:
        st.session_state.kupon.append({
            "mac": st.session_state.aktif_mac,
            **st.session_state.son_tahmin
        })
        cevap = "✅ Tahmin kupona eklendi. Aşağıda kuponunu görebilirsin 🧾"

    # 4️⃣ Kuponu göster
    elif "kuponu göster" in q.lower():
        if not st.session_state.kupon:
            cevap = "📭 Kupon boş."
        else:
            toplam_oran = 1
            metin = "🧾 **Kuponun**\n\n"
            for i, k in enumerate(st.session_state.kupon, 1):
                toplam_oran *= k["oran"]
                metin += f"{i}. {k['mac']} → {k['secim']} (Oran {k['oran']})\n"
            metin += f"\n💰 **Toplam Oran:** {round(toplam_oran,2)}"
            cevap = metin

    # 5️⃣ Normal sohbet
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç yaz → analiz al → **kupon yap** 🧾\n"
            "Örn: **Başakşehir - Gaziantep**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

# ------------------
# Alt Panel – Kupon Gösterimi

st.subheader("🧾 Güncel Kupon")

if not st.session_state.kupon:
    st.info("Henüz kupona eklenmiş tahmin yok.")
else:
    toplam_oran = 1
    for i, k in enumerate(st.session_state.kupon, 1):
        toplam_oran *= k["oran"]
        st.markdown(f"**{i}.** {k['mac']} → **{k['secim']}** (Oran {k['oran']})")
    st.markdown(f"
💰 **Toplam Oran:** {round(toplam_oran, 2)}")

# ------------------
# Alt Panel – Güven Bar
# ------------------

if st.session_state.son_tahmin:
    st.subheader("📊 Güven Barı")
    guven_degeri = st.session_state.son_tahmin.get("guven", 50)
    st.progress(guven_degeri / 100)
    st.markdown(f"**Güven Oranı:** %{guven_degeri}")

st.caption("© tahminsor.site • Yapay Zekâ Destekli Spor Tahmin & Kupon Sistemi")
