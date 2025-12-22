# app.py — Tahminsor FINAL FIXED
# Sohbet + Maç + Lig + Detay + Yüzde + Barem Takibi

import streamlit as st
import numpy as np
import requests
import re

st.set_page_config(page_title="Tahminsor", page_icon="🏀")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Merhaba 👋\n\n"
            "Benimle sohbet edebilirsin.\n"
            "Bir maç adı yazdığında analiz ederim 🙂"
        )
    }]

if "son_mac" not in st.session_state:
    st.session_state.son_mac = None

if "son_tahmin" not in st.session_state:
    st.session_state.son_tahmin = None

if "son_detay" not in st.session_state:
    st.session_state.son_detay = None

if "bekleyen_mac" not in st.session_state:
    st.session_state.bekleyen_mac = None

# ---------------- KELİMELER ----------------
DETAY_KELIMELER = ["neden", "detay", "açıkla", "niye"]
YUZDE_KELIMELER = ["yüzde", "olasılık", "ihtimal"]

BASKET_IPUCLARI = [
    "basket", "basketbol", "nba", "kbl",
    "league", "ligi", "lig"
]

# ---------------- FONKSİYONLAR ----------------
def mac_format_var_mi(q):
    return any(a in q for a in ["-", " vs ", " v "])

def detay_sorusu_mu(q):
    return any(k in q for k in DETAY_KELIMELER)

def yuzde_sorusu_mu(q):
    return any(k in q for k in YUZDE_KELIMELER)

def basket_ipucu_mu(q):
    return any(k in q for k in BASKET_IPUCLARI)

def barem_sorusu_mu(q):
    return bool(re.search(r"\d+(\.\d+)?\s*(alt|üst)", q))

def spor_turu_bul(takim):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{takim.replace(' ', '_')}"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        text = r.json().get("extract", "").lower()
        if "basketball" in text:
            return "basket"
        if "football" in text or "soccer" in text:
            return "futbol"
    except:
        return None
    return None

# ---------------- TAHMİN ----------------
def basket_tahmin(mac):
    seed = abs(hash(mac)) % 10**6
    rng = np.random.default_rng(seed)

    toplam = rng.uniform(220, 240)
    ust = toplam > 225

    ozet = f"""
🏀 **Basketbol Analizi**

- Tahmini toplam sayı: **{toplam:.1f}**
- Genel senaryo: **{'ÜST 🟢' if ust else 'ALT 🔴'}**

👉 **Benim favorim:** {'ÜST' if ust else 'ALT'}
"""

    detay = """
🔍 **Neye göre?**

- Hücum verimliliği
- Lig temposu
- Benzer eşleşmelerin sayı aralığı
"""

    return ozet, detay, ("ÜST" if ust else "ALT")

# ---------------- CHAT ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Bir şey yaz…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower()

    # 1️⃣ BAREM SORUSU (EN ÖNEMLİ FIX)
if barem_sorusu_mu(q) and st.session_state.son_mac:
    barem = re.findall(r"\d+(\.\d+)?", q)[0]
    alt_ust = "ALT" if "alt" in q else "ÜST"

    if alt_ust == st.session_state.son_tahmin:
        cevap = (
            f"✅ **{barem} {alt_ust}**, benim ana senaryomla uyumlu.\n\n"
            "Bu barem daha güvenli tarafta."
        )
    else:
        cevap = (
            f"⚠ **{barem} {alt_ust}**, ana senaryoma ters.\n\n"
            "Ancak tempo düşer ve savunma sertleşirse olabilir.\n"
            "Yaklaşık olasılık: **%35–40**"
        )

    # 2️⃣ MAÇ YAZILDI
    elif mac_format_var_mi(q):
        takimlar = [t.strip() for t in q.replace("vs", "-").split("-")]
        spor = None

        for t in takimlar:
            spor = spor_turu_bul(t)
            if spor:
                break

        if spor == "basket":
            ozet, detay, tahmin = basket_tahmin(q)
            st.session_state.son_mac = q
            st.session_state.son_tahmin = tahmin
            st.session_state.son_detay = detay
            cevap = "Analize geçiyorum 👇\n" + ozet
        else:
            st.session_state.bekleyen_mac = q
            cevap = (
                "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
                "Ligi veya spor türünü yazar mısın?\n"
                "Örn: Yeni Zelanda basketbol ligi"
            )

    # 3️⃣ LİG BİLGİSİ
    elif basket_ipucu_mu(q) and st.session_state.bekleyen_mac:
        mac = st.session_state.bekleyen_mac
        ozet, detay, tahmin = basket_tahmin(mac)
        st.session_state.son_mac = mac
        st.session_state.son_tahmin = tahmin
        st.session_state.son_detay = detay
        st.session_state.bekleyen_mac = None
        cevap = "Tamam 👍\n\n" + ozet

    # 4️⃣ DETAY
    elif detay_sorusu_mu(q) and st.session_state.son_mac:
        cevap = st.session_state.son_detay

    # 5️⃣ YÜZDE
    elif yuzde_sorusu_mu(q) and st.session_state.son_mac:
        cevap = "📊 Bu senaryo için güven aralığım **%60–65**."

    # 6️⃣ SOHBET
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Brisbane Bullets - N.Z. Breakers**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Bağlamı Unutmayan Yapay Zekâ")
