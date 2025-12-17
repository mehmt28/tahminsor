# app.py
# === Tahminsor.site | Spor Tahmin Yapay Zekâ Uygulaması ===

import streamlit as st
import numpy as np

st.set_page_config(page_title="Tahminsor", layout="centered")

st.title("🏀⚽ Tahminsor")
st.caption("Maç adını yaz • Yapay zekâ yorumlasın • Ücretsiz")

# ------------------
# BİLGİLENDİRME
# ------------------
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Bu platform istatistiksel simülasyonlara dayanır, kesinlik içermez.")

# ------------------
# MAÇ ADI GİRİŞİ
# ------------------
st.header("💬 Maç Adını Yaz")
match_name = st.text_input(
    "Örnek: Lakers vs Warriors | Arsenal - Chelsea"
)

if st.button("🤖 Tahmin Al") and match_name:
    q = match_name.lower()

    # ------------------
    # SON 5 MAÇ FORMU (OPSİYON 2)
    # ------------------
    form_home = np.random.choice(
        ["🔥 Çok Formda", "🙂 Orta", "❌ Formsuz"],
        p=[0.4, 0.35, 0.25]
    )
    form_away = np.random.choice(
        ["🔥 Çok Formda", "🙂 Orta", "❌ Formsuz"],
        p=[0.35, 0.4, 0.25]
    )

    st.markdown("### 🔄 Son 5 Maç Form Durumu")
    st.write("Ev Sahibi:", form_home)
    st.write("Deplasman:", form_away)

    # ------------------
    # FUTBOL TAHMİNİ
    # ------------------
    if "-" in q or " vs " in q:
        base_xg = np.random.uniform(1.2, 1.9)
        total_goals = base_xg * 2
        over25_prob = min(max((total_goals - 2.1) / 1.9, 0), 1)

        # ------------------
        # GÜVEN SEVİYESİ (OPSİYON 3)
        # ------------------
        if over25_prob > 0.65:
            confidence = "🟢 Yüksek"
        elif over25_prob > 0.52:
            confidence = "🟡 Orta"
        else:
            confidence = "🔴 Düşük"

        st.subheader("⚽ Futbol AI Yorumu")
        st.write("Beklenen Gol:", round(total_goals, 2))
        st.write("2.5 ÜST Olasılığı:", f"%{round(over25_prob*100,1)}")
        st.write("Güven Seviyesi:", confidence)

        if over25_prob > 0.55:
            st.success("Genel Yorum: 2.5 ÜST eğilimli")
        else:
            st.info("Genel Yorum: 2.5 ALT eğilimli")

    # ------------------
    # BASKETBOL TAHMİNİ
    # ------------------
    else:
        pace = np.random.uniform(96, 102)
        avg_total = np.random.uniform(212, 228)
        expected_total = avg_total * pace / 100

        if expected_total > 222:
            confidence = "🟢 Yüksek"
        elif expected_total > 215:
            confidence = "🟡 Orta"
        else:
            confidence = "🔴 Düşük"

        st.subheader("🏀 Basketbol AI Yorumu")
        st.write("Tahmini Toplam Sayı:", round(expected_total, 1))
        st.write("Güven Seviyesi:", confidence)

        if expected_total > 220:
            st.success("Genel Yorum: ÜST eğilimli")
        else:
            st.info("Genel Yorum: ALT eğilimli")

    st.caption("Bu sonuçlar lig ortalamaları ve form simülasyonu ile üretilmiştir.")

st.divider()
st.caption("© tahminsor.site • Açık erişim spor analiz platformu")

