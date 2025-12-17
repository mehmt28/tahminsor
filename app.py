# app.py
# === Streamlit | Açık Erişim Spor Tahmin AI ===

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# ------------------
# SAYFA AYARLARI
# ------------------
st.set_page_config(page_title="tahminsor.site", layout="centered")

st.title("🏀⚽ Spor Tahmin Yapay Zekâ Sistemi")
st.caption("Basketbol & Futbol • İstatistiksel Olasılık Analizi")

# ------------------
# BİLGİLENDİRME
# ------------------
st.sidebar.markdown("### 🌍 Erişim Durumu")
st.sidebar.success("Herkese Açık • Ücretsiz")
st.sidebar.info("Bu platform istatistiksel tahminler sunar. Kesinlik içermez.")

# ------------------
# DEMO BASKETBOL MODELİ
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
# BASKETBOL TAHMİN PANELİ
# ------------------
st.header("🏀 Basketbol Tahmin Modülü")

home_avg = st.number_input("Ev Ort. Sayı", 80.0, 130.0, 110.0)
away_avg = st.number_input("Dep. Ort. Sayı", 80.0, 130.0, 108.0)
home_def = st.number_input("Ev Savunma", 90.0, 130.0, 109.0)
away_def = st.number_input("Dep. Savunma", 90.0, 130.0, 111.0)
pace = st.number_input("Tempo (Pace)", 85.0, 105.0, 98.0)
barem = st.number_input("Barem", 140.5, 200.5, 160.5)
odd = st.number_input("Oran", 1.50, 3.50, 1.90)

if st.button("🔍 Basketbol Tahmini Al"):
    match = pd.DataFrame({
        'home_avg_points':[home_avg],
        'away_avg_points':[away_avg],
        'home_def_points':[home_def],
        'away_def_points':[away_def],
        'pace':[pace]
    })

    scaled = scaler.transform(match)
    prob = model.predict_proba(scaled)[0][1]
    expected_total = (home_avg + away_avg) * pace / 100

    implied_prob = 1 / odd
    value = prob - implied_prob

    st.subheader("📊 Sonuç")
    st.write("Tahmini Total:", round(expected_total,1))
    st.write("ÜST Olasılığı:", f"%{round(prob*100,1)}")

    if expected_total > barem:
        st.success("Tahmin: ÜST")
    else:
        st.info("Tahmin: ALT")

    if value > 0:
        st.success(f"Value VAR ✅ (Value: {round(value,3)})")
    else:
        st.warning(f"Value YOK ❌ (Value: {round(value,3)})")

# ------------------
# FUTBOL TAHMİN MODÜLÜ
# ------------------
st.divider()
st.header("⚽ Futbol Tahmin Modülü")

col1, col2 = st.columns(2)
with col1:
    home_xg = st.number_input("Ev Sahibi xG", 0.1, 4.0, 1.5)
    home_goals_avg = st.number_input("Ev Gol Ort.", 0.1, 4.0, 1.6)
with col2:
    away_xg = st.number_input("Deplasman xG", 0.1, 4.0, 1.2)
    away_goals_avg = st.number_input("Dep. Gol Ort.", 0.1, 4.0, 1.3)

league_strength = st.selectbox("Lig Seviyesi", ["Düşük", "Orta", "Yüksek"])
league_factor = {"Düşük":0.9, "Orta":1.0, "Yüksek":1.1}[league_strength]

if st.button("⚽ Futbol Tahmini Al"):
    total_goals_exp = (home_xg + away_xg + home_goals_avg + away_goals_avg) / 2 * league_factor

    over25_prob = min(max((total_goals_exp - 2.0) / 2, 0), 1)
    under25_prob = 1 - over25_prob

    st.subheader("📊 Futbol Sonuçları")
    st.write("Beklenen Gol:", round(total_goals_exp,2))
    st.write("2.5 ÜST:", f"%{round(over25_prob*100,1)}")
    st.write("2.5 ALT:", f"%{round(under25_prob*100,1)}")

    if over25_prob > 0.55:
        st.success("Öneri: 2.5 ÜST")
    else:
        st.info("Öneri: 2.5 ALT")

st.caption("© tahminsor.site • Açık Erişim Spor Tahmin Platformu")
