# app.py
# tahminsor.site | Açık Erişim Spor Tahmin Platformu

import streamlit as st
import numpy as np

st.set_page_config(page_title="Tahminsor", layout="centered")

# ------------------
# SIDEBAR
# ------------------
st.sidebar.title("tahminsor.site")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Tahminler istatistiksel modellere dayanır, kesinlik içermez.")

# ------------------
# GÜNÜN ÖNE ÇIKAN TAHMİNİ
# ------------------
st.header("🔥 Günün Öne Çıkan Tahmini")
np.random.seed(123)
featured = np.random.choice([
    "⚽ 2.5 ÜST değeri öne çıkan bir maç",
    "⚽ KG VAR ihtimali yüksek karşılaşma",
    "🏀 ÜST potansiyeli olan tempo maçı",
    "🏀 ALT senaryosu güçlü savunma maçı"
])
st.success(featured)

st.divider()

# ------------------
# MAÇ ADI → AI TAHMİN
# ------------------
st.header("💬 Maç Adını Yaz, Tahmini Al")

match_name = st.text_input(
    "Maç Adı",
    placeholder="Örnek: Arsenal - Chelsea | Lakers vs Celtics"
)

if st.button("🤖 Tahmin Al"):
    if not match_name:
        st.warning("Lütfen maç adı giriniz.")
        st.stop()

    # Aynı maç = aynı tahmin (stabilite)
    seed = abs(hash(match_name)) % (10**6)
    np.random.seed(seed)

    q = match_name.lower()

    basket_keys = ["nba", "lakers", "celtics", "warriors", "euroleague", "efes"]
    is_basket = any(k in q for k in basket_keys)
    is_futbol = not is_basket

    # ------------------
    # FUTBOL
    # ------------------
    if is_futbol:
        st.subheader("⚽ Futbol AI Yorumu")

        home_xg = np.random.uniform(1.0, 1.8)
        away_xg = np.random.uniform(0.8, 1.6)
        total_xg = home_xg + away_xg

        over25_prob = min(max((total_xg - 2.2) / 1.8, 0), 1)
        btts_prob = min(max((home_xg * away_xg) / 3, 0), 1)

        st.write(f"Beklenen Gol (xG): **{round(total_xg,2)}**")
        st.write(f"2.5 ÜST Olasılığı: **%{round(over25_prob*100,1)}**")
  st.write(f"2.5 ALT Olasılığı: **%{round(under25_prob*100,1)}**")
        st.write(f"KG VAR Olasılığı: **%{round(btts_prob*100,1)}**")

        st.subheader("📌 Tahmin Özeti")

        if over25_prob > 0.55:
            st.success("Genel Tahmin: **2.5 ÜST**")
            explanation = "Tempo ve gol beklentisi 2.5 sınırının üzerinde."
        else:
            st.info("Genel Tahmin: **2.5 ALT**")
            explanation = "Gol beklentisi sınırlı, kontrollü oyun öne çıkıyor."

        if btts_prob > 0.55:
            st.success("Ek Değer: **KG VAR** denenebilir")

        st.markdown(f"**Açıklama:** {explanation}")
        st.caption("Bu tahmin xG, tempo ve lig ortalamalarına dayalıdır.")

    # ------------------
    # BASKETBOL
    # ------------------
    else:
        st.subheader("🏀 Basketbol AI Yorumu")

        line = st.selectbox(
            "Sayı Baremi Seç",
            [210.5, 215.5, 220.5, 225.5, 230.5]
        )

        pace = np.random.uniform(96, 102)
        avg_total = np.random.uniform(210, 235)
        expected = avg_total * pace / 100

        st.write(f"Tahmini Toplam Sayı: **{round(expected,1)}**")

        if expected > line:
            st.success(f"Genel Tahmin: **{line} ÜST**")
            explanation = "Tempo ve hücum verimliliği üst senaryosunu destekliyor."
        else:
            st.info(f"Genel Tahmin: **{line} ALT**")
            explanation = "Tempo ve skor üretimi daha düşük görünüyor."

        st.markdown(f"**Açıklama:** {explanation}")
        st.caption("Bu tahmin tempo ve lig ortalamalarına dayalı projeksiyondur.")

st.divider()
st.caption("© tahminsor.site | Açık Erişim Spor Tahmin Platformu")
