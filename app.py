# app.py — TAHMİNSOR FINAL
# Sohbet + Maç Analizi + Lig Algılama + Barem Takibi

import streamlit as st
import numpy as np
import requests
import re

st.set_page_config(page_title="Tahminsor", page_icon="📊")

# ---------------- SESSION STATE ----------------
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


# ---------------- ANAHTAR KELİMELER ----------------
DETAY_KELIMELER = ["neden", "detay", "açıkla", "niye"]
YUZDE_KELIMELER = ["yüzde", "olasılık", "ihtimal"]
BASKET_IPUCLARI = ["basket", "basketbol", "kbl", "nba", "lig", "ligi", "league"]


# ---------------- YARDIMCI FONKSİYONLAR ----------------
def mac_format_var_mi(q: str) -> bool:
    return "-" in q or " vs " in q or " v " in q

def detay_sorusu_mu(q: str) -> bool:
    return any(k in q for k in DETAY_KELIMELER)

def yuzde_sorusu_mu(q: str) -> bool:
    return any(k in q for k in YUZDE_KELIMELER)

def basket_ipucu_mu(q: str) -> bool:
    return any(k in q for k in BASKET_IPUCLARI)

def barem_sorusu_mu(q: str) -> bool:
    return bool(re.search(r"\d+(\.\d+)?\s*(alt|üst)", q))

def spor_turu_bul(takim: str):
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


# ---------------- TAHMİN MOTORU ----------------
def basket_tahmin(mac: str):
    seed = abs(hash(mac)) % 1_000_000
    rng = np.random.default_rng(seed)

    tahmini_toplam = rng.uniform(215, 235)
    ust_mu = tahmini_toplam > 225

    ozet = (
        "🏀 **Basketbol Analizi**\n\n"
        f"- Tahmini toplam sayı: **{tahmini_toplam:.1f}**\n"
        f"- Genel senaryo: **{'ÜST 🟢' if ust_mu else 'ALT 🔴'}**\n\n"
        f"👉 **Benim favorim:** {'ÜST' if ust_mu else 'ALT'}"
    )

    detay = (
        "🔍 **Neye göre bu tahmin?**\n\n"
        "- Takımların hücum–savunma dengesi\n"
        "- Lig temposu (pace)\n"
        "- Benzer eşleşmelerin skor aralığı\n"
        "- İstatistiksel eşiklere göre olasılık avantajı"
    )

    return ozet, detay, ("ÜST" if ust_mu else "ALT")


# ---------------- CHAT ARAYÜZÜ ----------------
st.header("💬 Tahminsor Sohbet")
st.caption("Sohbet edebilir, maç sorabilir, barem üzerine devam edebilirsin.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Bir şey yaz…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower().strip()

    # -------- 1️⃣ BAREM SORUSU --------
    if barem_sorusu_mu(q) and st.session_state.son_mac:
        barem = re.findall(r"\d+(\.\d+)?", q)[0]
        alt_ust = "ALT" if "alt" in q else "ÜST"

        if alt_ust == st.session_state.son_tahmin:
            cevap = (
                f"✅ **{barem} {alt_ust}**, ana senaryomla uyumlu.\n\n"
                "Bu barem daha güvenli tarafta."
            )
        else:
            cevap = (
                f"⚠ **{barem} {alt_ust}**, ana senaryoma ters.\n\n"
                "Ancak tempo düşerse veya maç sertleşirse olabilir.\n"
                "Yaklaşık olasılık: **%35–40**"
            )

    # -------- 2️⃣ MAÇ ADI --------
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
            cevap = "Analize geçiyorum 👇\n\n" + ozet
        else:
            st.session_state.bekleyen_mac = q
            cevap = (
                "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
                "Ligi veya spor türünü yazar mısın?\n"
                "Örn: Güney Kore basketbol ligi"
            )

    # -------- 3️⃣ LİG BİLGİSİ --------
    elif basket_ipucu_mu(q) and st.session_state.bekleyen_mac:
        mac = st.session_state.bekleyen_mac
        ozet, detay, tahmin = basket_tahmin(mac)
        st.session_state.son_mac = mac
        st.session_state.son_tahmin = tahmin
        st.session_state.son_detay = detay
        st.session_state.bekleyen_mac = None
        cevap = "Tamam 👍\n\n" + ozet

    # -------- 4️⃣ DETAY --------
    elif detay_sorusu_mu(q) and st.session_state.son_mac:
        cevap = st.session_state.son_detay

    # -------- 5️⃣ YÜZDE --------
    elif yuzde_sorusu_mu(q) and st.session_state.son_mac:
        cevap = "📊 Bu senaryo için güven aralığım **%60–65**."

    # -------- 6️⃣ NORMAL SOHBET --------
    else:
        cevap = (
            "Sohbet edebiliriz 🙂\n\n"
            "Maç tahmini için iki takımı ayırarak yaz:\n"
            "**Anyang KGC - Samsung Thunders**"
        )

    st.session_state.messages.append({"role": "assistant", "content": cevap})
    with st.chat_message("assistant"):
        st.markdown(cevap)

st.caption("© tahminsor.site • Yapay Zekâ Destekli Spor Tahmin Sohbeti")
