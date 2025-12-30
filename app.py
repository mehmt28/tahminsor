import streamlit as st

# =========================
# SAYFA AYARLARI
# =========================
st.set_page_config(
    page_title="TahminSor - Hybrid Matcher",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

if "kupon" not in st.session_state:
    st.session_state.kupon = []

# =========================
# SAHTE HYBRID MATCHER (API YERİNE)
# =========================
def hybrid_matcher(user_input: str):
    name = user_input.lower().strip()

    known_matches = {
        "genk - club brugge": {
            "match": "KRC Genk - Club Brugge",
            "pick": "E",
            "confidence": 50
        },
        "al arabi - al batin": {
            "match": "Al Arabi - Al Batin",
            "pick": "D",
            "confidence": 46
        }
    }

    for k in known_matches:
        if k in name:
            return known_matches[k]

    return {
        "match": user_input,
        "pick": "Belirsiz",
        "confidence": 0
    }

# =========================
# STIL (BEYAZ ARKA PLAN)
# =========================
st.markdown("""
<style>
.card {
    background-color: #f8f9fa;
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 12px;
    border: 1px solid #e0e0e0;
}
.good { color: green; font-weight: bold; }
.bad { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =========================
# BAŞLIK
# =========================
st.title("⚽🏀 TahminSor – Hybrid Matcher")

# =========================
# LAYOUT
# =========================
left, right = st.columns([2, 1])

# =========================
# SOL TARAF
# =========================
with left:
    match_input = st.text_input(
        "Maç gir (örn: genk - club brugge)",
        key="match_input"
    )

    # ENTER veya TAHMİN AL
    if st.button("🔮 Tahmin Al") or match_input:
        if match_input.strip():
            result = hybrid_matcher(match_input)

            st.session_state.last_prediction = {
                "match": result.get("match", ""),
                "pick": result.get("pick", ""),
                "confidence": result.get("confidence", 0)
            }

            st.success("Tahmin alındı")

    # KUPONA EKLE (AYRI)
    if st.button("➕ Kupona Ekle"):
        if st.session_state.last_prediction:
            st.session_state.kupon.append(st.session_state.last_prediction)
            st.success("Kupona eklendi")
        else:
            st.warning("Önce tahmin al")

# =========================
# SAĞ TARAF – KUPON
# =========================
with right:
    st.subheader("🧾 Kupon")

    if not st.session_state.kupon:
        st.info("Kupon boş")
    else:
        for k in st.session_state.kupon:
            st.markdown(
                f"""
                <div class="card">
                    <b>{k.get('match','')}</b><br>
                    <span class="good">Öneri: {k.get('pick','')}</span><br>
                    Güven: %{k.get('confidence',0)}
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon = []
            st.experimental_rerun()
