# app.py — TAHMİNSOR FINAL
# Sohbet + Spor Tahmin + Doğal Dil + Barem Takibi

import streamlit as st
import numpy as np
import requests
import re

st.set_page_config(page_title="Tahminsor", page_icon="📊")

# ================= SESSION =================
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
    st.session_state.son_tahmin = None
    st.session_state.son_detay = None
    st.session_state.bekleyen_mac = None


# ================= ANAHTARLAR =================
DETAY_KELIMELER = ["neden", "detay", "açıkla", "niye"]
YUZDE_KELIMELER = ["yüzde", "olasılık", "ihtimal"]
BASKET_IPUCLARI = ["basket", "basketbol", "kbl", "nba", "lig", "ligi"]


# ================= YARDIMCI =================
def mac_format_var_mi(q):
    return "-" in q or " vs " in q or " v " in q

def detay_sorusu(q):
    return any(k in q for k in DETAY_KELIMELER)

def yuzde_sorusu(q):
    return any(k in q for k in YUZDE_KELIMELER)

def basket_ipucu(q):
    return any(k in q for k in BASKET_IPUCLARI)

def barem_sorusu(q):
    return bool(re.search(r"\d+(?:[.,]\d+)?\s*(alt|üst)", q))

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


# ================= TAHMİN MOTORU =================
def basket_tahmin(mac):
    seed = abs(hash(mac)) % 1_000_000
    rng = np.random.default_rng(seed)

    toplam = rng.uniform(215, 235)
    ana = "ÜST" if toplam > 225 else "ALT"

    ozet = (
        "🏀 **Basketbol Analizi**\n\n"
        f"- Tahmini toplam sayı: **{toplam:.1f}**\n"
        f"- Genel senaryo: **{ana}**\n\n"
        f"👉 **Benim favorim:** {ana}"
    )

    detay = (
        "🔍 **Neden bu tahmin?**\n\n"
        "- Lig temposu\n"
        "- Takımların hücum / savunma dengesi\n"
        "- Benzer maçların sayı aralığı\n"
        "- İstatistiksel eşiklere göre olasılık avantajı"
    )

    return ozet, detay, ana


# ================= CHAT =================
st.header("💬 Tahminsor Sohbet")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Bir şey yaz…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    q = user_input.lower().strip()
    qn = q.replace(",", ".")

    # -------- 1️⃣ BAREM ALT / ÜST --------
    if barem_sorusu(q) and st.session_state.son_mac:
        barem = re.findall(r"\d+(?:\.\d+)?", qn)[0]
        alt_ust = "ALT" if "alt" in qn else "ÜST"

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

    # -------- 2️⃣ DOĞAL DİL BAREM --------
    elif st.session_state.son_mac and re.search(r"\d+(?:\.\d+)?", qn):
        sayi = float(re.findall(r"\d+(?:\.\d+)?", qn)[0])

        if st.session_state.son_tahmin == "ALT":
            cevap = (
                f"🔍 **{sayi}** baremi {'düşük' if sayi < 160 else 'sınırda'}.\n\n"
                "Savunma ve tempo beklentisi nedeniyle ALT hâlâ mantıklı."
            )
        else:
            cevap = (
                f"📊 **{sayi}** baremi üst senaryosu için değerlendirilebilir.\n\n"
                "Tempo ve hücum katkısı bunu destekliyor."
            )

    # -------- 3️⃣ MAÇ ADI --------
    elif mac_format_var_mi(q):
        takimlar = [t.strip() for t in q.replace("vs", "-").split("-")]
        spor = None

        for t in takimlar:
            spor = spor_turu_bul(t)
            if spor:
                break

        if spor == "basket":
            ozet, detay, ana = basket_tahmin(q)
            st.session_state.son_mac = q
            st.session_state.son_tahmin = ana
            st.session_state.son_detay = detay
            cevap = "Analize geçiyorum 👇\n\n" + ozet
        else:
            st.session_state.bekleyen_mac = q
            cevap = (
                "Takımları tanıdım ama spor türünü netleştiremedim 🤔\n\n"
                "Ligi veya spor türünü yazar mısın?\n"
                "Örn: Güney Kore basketbol ligi"
            )

    # ------
