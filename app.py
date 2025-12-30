import streamlit as st

# =========================
# PAGE CONFIG
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
# HYBRID MATCHER (MOCK)
# =========================
def hybrid_matcher(user_input: str):
    text = user_input.lower().strip()

    database = {
        "genk - club brugge": {
            "match": "KRC Genk - Club Brugge",
            "pick": "E",
            "confidence": 50,
            "desc": "Dengeli maç, iç saha avantajı"
        },
        "al arabi - al batin": {
            "match": "Al Arabi - Al Batin",
            "pick": "D",
            "confidence": 46,
            "desc": "İki takım da formsuz"
        }
    }

    for k in database:
        if k in text:
            return database[k]

    return {
        "match": user_input,
        "pick": "Belirsiz",
        "confidence": 0,
        "desc": "Yeterli veri yok"
    }

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.card {
    background:#f8f9fa;
    padding:16px;
    border-radius:10px;
    border:1px solid #ddd;
    margin-bottom:12px;
}
.pick { font-weight:bold; color:#198754; }
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("⚽🏀 TahminSor – Hybrid Matcher")

left, right = st.columns([2, 1])

# =========================
# LEFT COLUMN
# =========================
with left:

    with st.form("prediction_form"):
        match_input = st.text_input(
            "Maç gir (örn: genk - club brugge)"
        )
        submit = st.form_submit_button("🔮 Tahmin Al")

    if submit:
        if match_input.strip():
            result = hybrid_matcher(match_input)

            st.session_state.last_prediction = result
            st.success("Tahmin alındı")

    # ---- TAHMİN GÖSTER ----
    if st.session_state.last_prediction:
        p = st.session_state.last_prediction
        st.markdown(
            f"""
            <div class="card">
                <b>{p['match']}</b><br>
                <span class="pick">Öneri: {p['pick']}</span><br>
                Güven: %{p['confidence']}<br>
                <i>{p['desc']}</i>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---- KUPONA EKLE ----
    if st.button("➕ Kupona Ekle"):
        if st.session_state.last_prediction:
            st.session_state.kupon.append(st.session_state.last_prediction)
            st.success("Kupona eklendi")
        else:
            st.warning("Önce tahmin al")

# =========================
# RIGHT COLUMN – KUPON
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
                    <b>{k['match']}</b><br>
                    Öneri: <b>{k['pick']}</b><br>
                    Güven: %{k['confidence']}
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("🗑️ Kuponu Temizle"):
            st.session_state.kupon = []
            st.experimental_rerun()
