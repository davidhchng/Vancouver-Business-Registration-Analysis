import streamlit as st

import logic

# Let's make some color helpers

LEVEL_COLORS = {
    "Low": ("#d4edda", "#155724"),      # green
    "Typical": ("#f2f2f2", "#333333"),  # white
    "High": ("#f8d7da", "#721c24")      # red
}

def render_level(level):
    bg, fg = LEVEL_COLORS.get(level, ("#f2f2f2", "#333333"))
    return f"""
    <span style="
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        background:{bg};
        color:{fg};
        font-weight:600;
        font-size:0.9rem;
        border:1px solid rgba(0,0,0,0.08);
    ">{level}</span>
    """



st.title("Vancouver Business Registrations: Inferences for Market Interpretation")

# Dropdown menu

business_type = st.selectbox("Business Type", sorted(logic.big_types))

local_area = st.selectbox(
    "Neighbourhood (LocalArea)",
    sorted(logic.df_filtered["LocalArea"].dropna().unique()))


# Below is to classify colors for metrics, and classes:

if st.button("Run"):

    result = logic.market_interpretation(business_type, local_area)
    st.subheader(result["interpretation_title"])
    st.write(result["interpretation_summary"])

    st.subheader("Scores")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.metric("Concentration score", f"{result['concentration_score']:.2f}")
    with c2:
        st.markdown(render_level(result["concentration_level"]), unsafe_allow_html=True)

    c3, c4 = st.columns([2, 1])
    with c3:
        st.metric("Closure risk score", f"{result['closure_risk_score']:.2f}")
    with c4:
        st.markdown(render_level(result["closure_risk_level"]), unsafe_allow_html=True)

    c5, c6 = st.columns([2, 1])
    with c5:
        rec = result["recency_momentum_score"]
        st.metric("Recency momentum", "N/A" if rec is None else f"{rec:.2f}")
    with c6:
        st.markdown(render_level("Typical"), unsafe_allow_html=True)  # always neutral

  

    fig = logic.plot_map(business_type, local_area)

    st.plotly_chart(fig, use_container_width = True)




