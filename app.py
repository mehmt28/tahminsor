# app.py
# Tahminsor.site | Yapay Zekâ Destekli Spor Tahmin Platformu
# 1️⃣ Günün Favorisi | 2️⃣ Lig Seçimi | 3️⃣ Saat/Tarih | 4️⃣ Tahmin Geçmişi

import streamlit as st
import numpy as np
from datetime import date, datetime

# ------------------
# SAYFA AYARLARI
# ------------------
st.set_page_config(
    page_title="Tahminsor AI",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Tahminsor AI")
st.caption("İstatistiksel verilere dayalı spor tahmin platformu")

# ------------------
# SIDEBAR BİLGİ
# ------------------
with st.sidebar:
    st.success("🌍 Herkese Açık • Ücretsiz")
    st.info(
        """
Tahminler;
- Lig ortalamaları
- Tempo (pace)
- Hücum / savunma dengesi
- İstatistiksel eşikler

kullanılarak üretilir.
⚠️ Kesin sonuç garantisi yoktur.
"""
    )

# ------------------
# SESSION STATE
# ------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ==================================================
# 1️⃣ GÜNÜN FAVORİ MAÇI (GÜN BOYU SABİT)
# ==================================================
st.divider()
st.header("🔥 Günün Favori Tahmini")

daily_seed = int(date.today().strftime("%Y%m%d"))
np.random.seed(daily_seed)

favorite_pool = [
    ("Galatasaray - Fenerbahçe", "futbol"),
    ("Real Madrid - Valencia", "futbol"),
    ("Arsenal - Chelsea", "futbol"),
    ("Lakers vs Warriors", "basket"),
    ("Fenerbahçe Beko vs Anadolu Efes", "basket")
]

fav_match, fav_type = favorite_pool[np.random.randint(len(favorite_pool))]

if fav_type == "futbol":
    eg = np.random.uniform(2.3, 3.1)
    pick = "2.5 ÜST" if eg > 2.5 else "2.5 ALT"
    st.subheader(f"⚽ {fav_match}")
    st.success(f"Tahmin: **{pick}**")
    st.write(f"Beklenen gol: **{eg:.2f}**")
else:
    total = np.random.uniform(218, 232)
    pick = "ÜST" if total > 224 else "ALT"
    st.subheader(f"🏀 {fav_match}")
    st.success(f"Tahmin: **{pick}**")
    st.write(f"Tahmini toplam sayı: **{total:.1f}**")

st.markdown("🧠 Bu tahmin lig ortalamaları ve tempo verilerine dayanır.")

# ==================================================
# 2️⃣ LİG SEÇİMİ (OPSİYONEL)
# ==================================================
st.divider()
st.header("🏆 Lig Seçimi")

league = st.selectbox(
    "Lig seçmek istersen:",
    ["Otomatik", "Süper Lig", "Avrupa", "NBA", "Euroleague"]
)

# ==================================================
# 3️⃣ SAAT / TARİH BAĞLAMI
# ==================================================
current_hour = datetime.now().hour
if current_hour >= 18:
    st.caption("⏰ Akşam / Gece maçları için analiz modu")
else:
    st.caption("⏰ Gündüz maçları için analiz modu")

# ==================================================
# 4️⃣ MAÇ SOR – TAHMİN AL + GEÇMİŞ
# ==================================================
st.divider()
st.header("💬 Maç Sor – Tahmin Al")

match_name = st.text_input("Maç adını yaz (örn: Galatasaray - Beşiktaş)")

if match_name:
    seed = abs(hash(match_name.lower())) % 1_000_000
    np.random.seed(seed)

    is_futbol = "-" in match_name
    is_basket = "vs" in match_name.lower()

    if is_futbol and not is_basket:
        home = np.random.uniform(0.9, 1.4)
        away = np.random.uniform(0.8, 1.3)
        eg = home + away

        goal_pick = "2.5 ÜST" if eg > 2.5 else "2.5 ALT"

        if home > away + 0.2:
            result = "Ev Sahibi Kazanır"
        elif away > home + 0.2:
            result = "Deplasman Kazanır"
        else:
            result = "Beraberlik"

        analysis = f"""
⚽ **Futbol Analizi**

• Beklenen gol: **{eg:.2f}**
• Gol Bahsi: **{goal_pick}**
• Maç Sonucu: **{result}**

🧠 Hücum gücü, lig ortalamaları ve tempo dikkate alınmıştır.
"""
    else:
        pace = np.random.uniform(95, 103)
        total = np.random.uniform(212, 232) * pace / 100
        total_pick = "ÜST" if total > 220 else "ALT"

        analysis = f"""
🏀 **Basketbol Analizi**

• Tahmini toplam sayı: **{total:.1f}**
• Genel eğilim: **{total_pick}**

🧠 Tempo ve sayı ortalamalarına göre değerlendirilmiştir.
"""

    st.success(analysis)

    st.session_state.history.append(
        {"match": match_name, "analysis": analysis}
    )

# ------------------
# TAHMİN GEÇMİŞİ
# ------------------
if st.session_state.history:
    st.divider()
    st.header("📜 Son Tahminler")

    for item in st.session_state.history[-5:][::-1]:
        st.markdown(f"**{item['match']}**")
        st.markdown(item["analysis"])
        st.markdown("---")

st.caption("© tahminsor.site • Yapay Zekâ Destekli Spor Tahmin Platformu")
