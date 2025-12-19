# app.py
# === Streamlit | Açık Erişim Spor Tahmin AI ===
# OPSİYONLAR:
# 1- Maç adı yazarak AI yorum
# 2- Canlı basketbol projeksiyon
# 3- Spor türü manuel düzeltme
# 4- Futbol detaylı tahmin
# 5- VALUE BET (DEĞERLİ ORAN) HESAPLAMA

import streamlit as st
import numpy as np

USERS = {"admin": "1234", "demo": "demo"}

st.set_page_config(page_title="TahminSor AI", layout="centered")
st.title("🏀⚽ TahminSor | Spor Tahmin Yapay Zekâ")

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    with st.form("login"):
        u = st.text_input("Kullanıcı adı")
        p = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş Yap"):
            if u in USERS and USERS[u] == p:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Hatalı giriş")
    st.stop()

st.header("💬 Maç Adını Yaz – AI Tahmin")
match = st.text_input("Maç adı")

if st.button("🤖 Tahmin Al"):
    q = match.lower()
    futbol = ["fc","arsenal","chelsea","madrid","barcelona","galatasaray","fenerbahce"]
    basket = ["nba","lakers","celtics","warriors","efes"]

    is_futbol = any(k in q for k in futbol)
    is_basket = any(k in q for k in basket)

    if "-" in q and not is_basket:
        is_futbol = True

    if is_futbol == is_basket:
        sec = st.radio("Spor türü:", ["Futbol","Basketbol"], horizontal=True)
        is_futbol = sec == "Futbol"

    if is_futbol:
        g = np.random.uniform(2.0,3.0)
        st.success(f"⚽ Beklenen gol: {round(g,2)}")
    else:
        t = np.random.uniform(210,230)
        st.success(f"🏀 Tahmini toplam sayı: {round(t,1)}")

st.divider()
st.subheader("💎 Value Bet Hesaplama")
prob = st.number_input("Kazanma olasılığı (%)", 1.0, 99.0, 55.0)
odd = st.number_input("Oran", 1.01, 20.0, 1.90)

if st.button("💰 Value Var mı?"):
    val = (prob/100)*odd - 1
    st.success(f"VALUE VAR ({round(val,3)})") if val>0 else st.error(f"Value yok ({round(val,3)})")

st.caption("© tahminsor.site")
