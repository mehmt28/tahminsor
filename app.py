# app.py
# === Tahminsor | Sohbet + Spor Tahmin AI (STABLE FINAL) ===

import streamlit as st
import numpy as np
import re

st.set_page_config(page_title="Tahminsor", layout="centered")

# ------------------
# Yardımcı fonksiyonlar
# ------------------

def mac_format_var_mi(text):
    return bool(re.search(r".+\s[-–]\s.+", text))


def lig_belirtildi_mi(text):
    anahtarlar = [
        "futbol", "basketbol", "süper lig", "super lig",
        "kbl", "nba", "euroleague", "ligi", "lig"
    ]
    return any(k in text.lower() for k in anahtarlar)


def barem_sorusu_mu(text):
    return bool(re.search(r"\d+[\.,]?\d*\s*(alt|üst)", text.lower()))


def kg_sorusu_mu(text):
    return "kg" in text.lower() or "karşılıklı" in text.lower()


# ------------------
# Session State
# ------------------

for key in [
    "messages", "aktif_mac", "spor_turu",
    "son_tahmin", "kupon", "son_eklenen"
]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["messages", "kupon"] else None

# ------------------
# Başlık
# ------------------

st.title("💬 Tahminsor – Spor Tahmin Asistanı")
st.caption("Maç yaz → analiz al → kupon yap 🧾")

# ------------------
# Mesajları göster
# ------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------
# Kullanıcı girişi
# ------------------

q = st.chat_input("Mesajını yaz…")

if q:
    q = q.strip()
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

    # 2️⃣ Lig belirtildi → ana analiz
    elif st.session_state.aktif_mac and not st.session_state.spor_turu and lig_belirtildi_mi(q):
        st.session_state.spor_turu = q.lower()
        np.random.seed(abs(hash(st.session_state.aktif_mac)) % 10**6)

        # FUTBOL
        if "futbol" in q.lower() or "lig" in q.lower():
            ev = round(np.random.uniform(45, 55), 1)
            ber = round(np.random.uniform(20, 30), 1)
            dep = round(100 - ev - ber, 1)
            guven = int(ev)

            st.session_state.son_tahmin = {
                "tur": "futbol",
                "secim": "Ev Sahibi",
                "oran": round(1 + (100 / ev), 2),
                "guven": guven
            }

            cevap = (
                "⚽ **Futbol Analizi (1X2)**\n\n"
                f"🏠 Ev Sahibi: %{ev}\n"
                f"🤝 Beraberlik: %{ber}\n"
                f"🚗 Deplasman: %{dep}\n\n"
                f"👉 **Önerim:** Ev Sahibi\n"
                f"📊 **Güven:** %{guven}\n\n"
                "Devam edebiliriz:\n"
                "• 2.5 Alt/Üst?\n"
                "• KG Var mı?"
            )

        # BASKETBOL
        else:
            toplam = round(np.random.uniform(210, 225), 1)
            senaryo = "ALT" if toplam < 220 else "ÜST"
            guven = min(int(abs(220 - toplam) + 55), 85)

            st.session_state.son_tahmin = {
                "tur": "basketbol",
                "secim": senaryo,
                "oran": round(np.random.uniform(1.6, 1.9), 2),
                "guven": guven
            }

            cevap = (
                "🏀 **Basketbol Analizi**\n\n"
                f"🔢 Tahmini toplam: {toplam}\n"
                f"📌 Ana senaryo: **{senaryo}**\n"
                f"📊 **Güven:** %{guven}\n\n"
                "Barem sorabilirsin (örn: 153.5 üst olur mu?)"
            )

    # 3️⃣ Barem / KG soruları
    elif st.session_state.son_tahmin and (barem_sorusu_mu(q) or kg_sorusu_mu(q)):
        ana = st.session_state.son_tahmin["secim"]
        cevap = (
            f"🔍 **Değerlendirme**\n\n"
            f"Ana senaryom: **{ana}**\n\n"
            "Bu alternatif daha düşük olasılıklı.\n"
            "Yaklaşık ihtimal: **%35–40**\n\n"
            "🎯 Daha güvenlisi ana senaryo."
        )

    # 4️⃣ Kupona ekle (tekil kontrol)
    elif "kupon" in q.lower() and st.session_state.son_tahmin:
        secim_id = (st.session_state.aktif_mac, st.session_state.son_tahmin["secim"])
        if secim_id == st.session_state.son_eklenen:
            cevap = "⚠️ Bu tahmin zaten kuponda."
        else:
            st.session_state.kupon.append({
                "mac": st.session_state.aktif_mac,
                **st.session_state.son_tahmin
            })
            st.session_state.son_eklenen = secim_id
            cevap = "✅ Tahmin kupona eklendi. Devam edebilirsin."

    # 5️⃣ Kuponu göster
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

    # 6️⃣ Normal sohbet
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç yaz → analiz al → **kupon yap** 🧾\n"
            "Örn: Başakşehir - Gaziantep"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

# ------------------
# Güven Barı
# ------------------

if st.session_state.son_tahmin:
    st.subheader("📊 Güven Seviyesi")
    g = st.session_state.son_tahmin["guven"]
    st.progress(g / 100)
    st.markdown(f"**%{g} güven**")

st.caption("© Tahminsor • Yapay Zekâ Destekli Tahmin Sistemi")
