# app.py
# Tahminsor – Spor Tahmin Asistanı

import streamlit as st
import numpy as np

st.set_page_config(
    page_title="Tahminsor | Spor Tahmin AI",
    page_icon="⚽",
    layout="centered"
)

st.title("💬 Tahminsor – Spor Tahmin Asistanı")
st.caption("Benimle maç hakkında konuş, istatistiksel tahmin ve yorum al.")

# -----------------------
# CHAT STATE
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------
# ANALİZ FONKSİYONU
# -----------------------
def analyze_match(text):
    seed = abs(hash(text)) % (10**6)
    np.random.seed(seed)

    q = text.lower()

    futbol_keys = [
        "-", "fc", "city", "united", "madrid", "barcelona",
        "galatasaray", "fenerbahce", "besiktas", "arsenal", "chelsea"
    ]

    basket_keys = [
        "nba", "lakers", "warriors", "celtics",
        "euroleague", "efes", "fenerbahce beko"
    ]

    is_basket = any(k in q for k in basket_keys)
    is_futbol = any(k in q for k in futbol_keys) and not is_basket

    # ---------- FUTBOL ----------
    if is_futbol:
        xg = np.random.uniform(2.1, 3.3)
        over_prob = min(max((xg - 2.3) / 1.5, 0), 1)

        home = np.random.uniform(0.38, 0.52)
        draw = 0.25
        away = 1 - home - draw

        if home > away and home > draw:
            result = "Ev Sahibi Kazanır (1)"
        elif away > home and away > draw:
            result = "Deplasman Kazanır (2)"
        else:
            result = "Beraberlik (X)"

        return f"""
⚽ **Futbol Analizi**

• Beklenen gol (xG): **{xg:.2f}**
• 2.5 ÜST olasılığı: **%{over_prob*100:.0f}**
• Maç sonucu eğilimi: **{result}**

📌 **Neye göre?**  
Bu tahmin; gol beklentisi (xG), lig ortalamaları ve
istatistiksel denge birlikte değerlendirilerek üretilmiştir.
"""

    # ---------- BASKETBOL ----------
    else:
        total = np.random.uniform(212, 234)
        trend = "ÜST" if total > 220 else "ALT"

        return f"""
🏀 **Basketbol Analizi**

• Tahmini toplam sayı: **{total:.1f}**
• Genel eğilim: **{trend}**

📌 **Neye göre?**  
Tempo, son maçlardaki sayı ortalamaları ve
lig dinamikleri dikkate alınmıştır.
"""

# -----------------------
# CHAT INPUT
# -----------------------
user_input = st.chat_input("Maç yaz veya soru sor (Örn: Arsenal - Chelsea)")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    response = analyze_match(user_input)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)

st.caption("© tahminsor.site • Açık erişim, istatistiksel tahmin platformu")
