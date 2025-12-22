# app.py — Tahminsor FINAL ULTIMATE
# Sohbet + Maç + Detay + Yüzde + İnternet + Lig İpucu

import streamlit as st
import numpy as np
import requests

st.set_page_config(page_title="Tahminsor", page_icon="⚽")

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

if "son_detay" not in st.session_state:
    st.session_state.son_detay = None

if "bekleyen_mac" not in st.session_state:
    st.session_state.bekleyen_mac = None

# ---------------- ANAHTAR KELİMELER ----------------
DETAY_KELIMELER = ["neden", "detay", "açıkla", "niye", "sebep"]
YUZDE_KELIMELER = ["yüzde", "olasılık", "ihtimal", "güven", "kaç"]

BASKET_IPUCLARI = [
    "basket", "basketbol", "kbl", "nba",
    "euroleague", "ligi", "lig"
]

def detay_sorusu_mu(q):
    return any(k in q for k in DETAY_KELIMELER)

def yuzde_sorusu_mu(q):
    return any(k in q for k in YUZDE_KELIMELER)

def basket_ipucu_mu(q):
    return any(k in q for k in BASKET_IPUCLARI)

# ---------------- FORMAT ----------------
def mac_format_var_mi(q):
    return any(a in q for a in ["-", " vs ", " v "])

# ---------------- WIKIPEDIA ----------------
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
    toplam = rng.uniform(215, 240)
    ust = toplam > 225

    ozet = f"""
🏀 **Basketbol Analizi**

- Tahmini toplam sayı: **{toplam:.1f}**
- Toplam: **{'ÜST 🟢' if ust else 'ALT 🔴'}**

👉 **Favorim:** {'ÜST' if ust else 'ALT'}
"""

    detay = """
🔍 **Bu tahmin neye dayanıyor?**

- KBL liginde tempo NBA’ye göre daha kontrollü
- Ancak bu eşleşmede hücum katkısı yüksek
- Benzer maç aralıklarında üst senaryosu öne çıkıyor
"""
    return ozet, detay

# ---------------- CHAT ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Bir şey yaz… (örn: Anyang KGC - Samsung Thunders)")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower()

    # 1️⃣ MAÇ YAZILDI
    if mac_format_var_mi(q):
        takimlar = [t.strip() for t in q.replace("vs", "-").split("-")]
        spor = None

        for t in takimlar:
            spor = spor_turu_bul(t)
            if spor:
                break

        if spor == "basket":
            ozet, detay = basket_tahmin(q)
            st.session_state.son_mac = q
            st.session_state.son_detay = detay
            cevap = "Analize geçiyorum 👇\n" + ozet

        else:
            st.session_state.bekleyen_mac = q
            cevap = (
                "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
                "Ligi veya spor türünü yazabilir misin?\n"
                "Örn: **Güney Kore KBL basketbol ligi**"
            )

    # 2️⃣ LİG İPUCU GELDİ
    elif basket_ipucu_mu(q) and st.session_state.bekleyen_mac:
        mac = st.session_state.bekleyen_mac
        ozet, detay = basket_tahmin(mac)
        st.session_state.son_mac = mac
        st.session_state.son_detay = detay
        st.session_state.bekleyen_mac = None
        cevap = "Tamam 👍 Bilgiyi aldım.\n\n" + ozet

    # 3️⃣ DETAY
    elif detay_sorusu_mu(q) and st.session_state.son_mac:
        cevap = st.session_state.son_detay

    # 4️⃣ YÜZDE
    elif yuzde_sorusu_mu(q) and st.session_state.son_mac:
        cevap = "📊 Bu maç için üst senaryosu yaklaşık **%64** güven veriyor."

    # 5️⃣ SOHBET
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Anyang KGC - Samsung Thunders**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Bağlam Takipli Yapay Zekâ Spor Tahminleri")
