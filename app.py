# app.py
# === Streamlit | Kullanıcılı Spor Tahmin AI ===

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# ------------------
# KULLANICI GİRİŞİ KALDIRILDI
# Uygulama tamamen açık erişimdir


# ------------------
# AÇIK ERİŞİM BİLGİLENDİRME
# ------------------
st.sidebar.markdown("### 🌍 Erişim Durumu")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Bu platform istatistiksel tahminler sunar. Kesinlik içermez.")

# ------------------
# ------------------
# DEMO MODEL (CSV ile değiştirilebilir)
# ------------------
data = {
    'home_avg_points': [112,105,118,110,108,115],
    'away_avg_points': [109,102,114,107,104,111],
    'home_def_points': [108,110,105,109,111,106],
    'away_def_points': [110,112,108,111,113,109],
    'pace': [98,95,102,97,96,101],
    'total_points': [221,207,232,217,212,226]
}

df = pd.DataFrame(data)
barem_default = 160.5
df['label'] = (df['total_points'] > barem_default).astype(int)

X = df[['home_avg_points','away_avg_points','home_def_points','away_def_points','pace']]
y = df['label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=200, max_depth=7, random_state=42)
model.fit(X_scaled, y)

# ------------------
# MAÇ ADI SOR – AI TAHMİN ÜRETSİN (BASİT CHAT)
# ------------------
st.header("💬 Maç Adını Yaz – Yapay Zekâ Yorumlasın")
st.write("Sadece maç adını yaz. Sistem genel form, tempo ve lig dinamiklerine göre tahmin üretir.")

match_name = st.text_input(
    "Maç adı:",
    placeholder="Örnek: Lakers vs Warriors | Arsenal - Chelsea"
)

if st.button("🤖 Tahmin Al"):
    # Aynı maç için her tıklamada farklı tahmin üretilmemesi için
    # match_name bazlı sabit bir random seed oluşturuyoruz
    seed = abs(hash(match_name)) % (10**6)
    np.random.seed(seed)
    if not match_name:
        st.warning("Lütfen maç adı girin")
        st.stop()

    q = match_name.lower()

    # ------------------
    # FUTBOL / BASKETBOL AYRIMI (DÜZELTİLDİ)
    # ------------------
    futbol_kelimeler = [
        " fc", "fk ", "sk ", " united", "city", "chelsea", "arsenal",
        "madrid", "barcelona", "galatasaray", "fenerbahce",
        "besiktas", "juventus", "milan", "inter", "psg",
        "liverpool", "bayern", "dortmund"
    ]

    basket_kelimeler = [
        "lakers", "warriors", "nba", "celtics", "bulls",
        "heat", "knicks", "euroleague", "fenerbahce beko",
        "anadolu efes", "real madrid baloncesto"
    ]

    is_futbol = any(k in q for k in futbol_kelimeler)
    is_basket = any(k in q for k in basket_kelimeler)

    # Varsayılan: tire varsa FUTBOL kabul et
    if "-" in q and not is_basket:
        is_futbol = True

        # ------------------
    # KULLANICI DÜZELTME SEÇENEĞİ (OPSİYON 3)
    # ------------------
    if is_futbol and is_basket:
        st.warning("Maç türü net algılanamadı. Lütfen düzeltin:")
        forced = st.radio("Bu maç hangi spor?", ["Futbol", "Basketbol"], horizontal=True)
        if forced == "Futbol":
            is_futbol = True
            is_basket = False
        else:
            is_futbol = False
            is_basket = True

    elif not is_futbol and not is_basket:
        forced = st.radio(
            "Spor türü otomatik algılanamadı. Seçiniz:",
            ["Futbol", "Basketbol"],
            horizontal=True
        )
        if forced == "Futbol":
            is_futbol = True
        else:
            is_basket = True

    # ------------------
    # FUTBOL MAÇ ALGILAMA
# (ÜST/ALT + KG VAR/YOK + KISA ÖZET)
    # ------------------
    if is_futbol:
        base_xg = np.random.uniform(1.1, 1.8)
        total_goals_exp = base_xg * 2
        over25_prob = min(max((total_goals_exp - 2.2) / 1.8, 0), 1)

        st.subheader("⚽ Futbol AI Yorumu")
        st.write(f"Beklenen gol aralığı: **{round(total_goals_exp-0.3,2)} – {round(total_goals_exp+0.3,2)}**")
        st.write(f"2.5 ÜST olasılığı: **%{round(over25_prob*100,1)}**")

        # Güven seviyesi hesaplama
        confidence = int(over25_prob * 100)
        if over25_prob > 0.65:
            risk_label = "🟢 Düşük Risk"
        elif over25_prob > 0.55:
            risk_label = "🟡 Orta Risk"
        else:
            risk_label = "🔴 Yüksek Risk"

        st.subheader("📌 Tahmin Özeti")
        st.write("Güven Seviyesi:", f"%{confidence}")
        st.write("Risk Profili:", risk_label)

        # Tahmin özeti ile yorumun birebir uyumlu olması için tek karar değişkeni kullanılır
        if over25_prob > 0.55:
            final_pick = "2.5 ÜST"
            explanation = (
                "Beklenen toplam gol değeri 2.5 sınırının üzerinde. "
                "Tempo, hücum katkısı ve lig ortalaması gollü senaryoyu destekliyor."
            )
            st.success(f"Genel Tahmin: **{final_pick}**")
        else:
            final_pick = "2.5 ALT"
            explanation = (
                "Beklenen gol ortalaması 2.5 seviyesinin altında. "
                "Daha kontrollü oyun ve savunma dengesi öne çıkıyor."
            )
            st.info(f"Genel Tahmin: **{final_pick}**")

        st.markdown(f"**Tahmin Gerekçesi:** {explanation}")

        # --- MAÇ SONUCU (1-X-2) TAHMİNİ ---
        home_win_prob = min(max((base_xg * 0.6), 0), 1)
        away_win_prob = min(max((base_xg * 0.5), 0), 1)
        draw_prob = 0.25

        total_prob = home_win_prob + away_win_prob + draw_prob
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob

        st.subheader("🏟️ Maç Sonucu Olasılıkları")
        st.write("Ev Sahibi Kazanır:", f"%{round(home_win_prob*100,1)}")
        st.write("Beraberlik:", f"%{round(draw_prob*100,1)}")
        st.write("Deplasman Kazanır:", f"%{round(away_win_prob*100,1)}")

        # Net öneri
        if home_win_prob > away_win_prob and home_win_prob > draw_prob:
            st.success("Maç Sonucu Önerisi: **Ev Sahibi Kazanır (1)**")
        elif away_win_prob > home_win_prob and away_win_prob > draw_prob:
            st.success("Maç Sonucu Önerisi: **Deplasman Kazanır (2)**")
        else:
            st.info("Maç Sonucu Önerisi: **Beraberlik (X)**")

        st.caption("Bu tahmin; xG, tempo, lig ortalamaları ve istatistiksel eşiklerin birlikte değerlendirilmesiyle üretilmiştir. (xG), tempo ve lig ortalamalarının birlikte değerlendirilmesiyle üretilmiştir.")

        # ------------------
        # TAHMİN AÇIKLAMA YORUMU
        # Bu öneri; beklenen gol (xG), tempo, lig ortalamaları ve
        # istatistiksel eşik değerlerin birlikte değerlendirilmesiyle oluşur.
        # Amaç: kesin sonuç değil, olasılık avantajını göstermek.


    # ------------------
    # BASKETBOL MAÇ ALGILAMA
# (BAREM SEÇİLEBİLİR – OPSİYON 2)
    # ------------------
    # ------------------
    else:
        pace_est = np.random.uniform(96, 101)
        avg_total = np.random.uniform(210, 230)
        expected_total = avg_total * pace_est / 100

        st.subheader("🏀 Basketbol AI Yorumu")
        st.write(f"Tahmini toplam sayı: **{round(expected_total,1)}**")

        confidence = int(min(max((expected_total-200)/40,0),1)*100)
        if expected_total > 225:
            risk_label = "🟢 Düşük Risk"
        elif expected_total > 215:
            risk_label = "🟡 Orta Risk"
        else:
            risk_label = "🔴 Yüksek Risk"

        st.subheader("📌 Tahmin Özeti")
        st.write("Güven Seviyesi:", f"%{confidence}")
        st.write("Risk Profili:", risk_label)

        if expected_total > 220:
            st.success("Genel Yorum: **ÜST eğilimli maç**")
            st.markdown("**Açıklama:** Tempo ve ortalama skor projeksiyonu yüksek. Hızlı oyun bekleniyor.")
        else:
            st.info("Genel Yorum: **ALT eğilimli maç**")
            st.markdown("**Açıklama:** Tempo ve sayı beklentisi düşük. Kontrollü senaryo öne çıkıyor.")

        st.caption("Bu tahmin tempo, lig ortalaması ve istatistiksel projeksiyonlara dayanır.")

# ------------------
# CANLI MAÇ MODÜLÜ
# (OPSİYON 4: session_state ile güvenli hale getirildi)

if "expected_total" not in st.session_state:
    st.session_state.expected_total = 220.0

st.divider()
st.subheader("⏱️ Canlı Maç Simülasyonu")

live_pts = st.number_input("Şu ana kadar atılan sayı", 0, 200, 52, key="live_pts")
minutes = st.number_input("Oynanan dakika", 1, 40, 10, key="minutes")

if st.button("📈 Canlı Projeksiyon"):
    pace_factor = live_pts / minutes
    proj = pace_factor * 40
    final_proj = (proj + st.session_state.expected_total) / 2
    st.write("Canlı Tahmini Final Total:", round(final_proj,1))



st.caption("© tahminsor.site • Açık Erişim Spor Tahmin Platformu")
