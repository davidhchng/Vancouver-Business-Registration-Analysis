import streamlit as st

import logic


# Let's make the colors for each score level, for each metric:

LEVEL_COLORS = {
    "Low": ("#d4edda", "#155724"),      # green
    "Typical": ("#f2f2f2", "#333333"),  # white
    "High": ("#f8d7da", "#721c24")       # red
}

def render_level(level):

    bg, fg = LEVEL_COLORS.get(level, ("#f2f2f2", "#333333"))

    return f"""
    <span style="
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background:{bg};
        color:{fg};
        font-weight: 600;
        font-size: 0.9rem;
        border; 1 px solid rgba(0,0,0,0.08);
        ">
        {level}
    </span>
    """

st.metric(
    "Concentration score",
    f"{result['concentration_score']:.2f}"
)
st.markdown(
    render_level(result["concentration_level"]),
    unsafe_allow_html=True
)

st.metric(
    "Closure risk score",
    f"{result['closure_risk_score']:.2f}"
)
st.markdown(
    render_level(result["closure_risk_level"]),
    unsafe_allow_html=True
)

rec = result["recency_score"]

st.metric(
    "Recency Score",
    "N/A" if rec is None else f"{rec:.2f}"
)
st.markdown(
    render_level("Typical"),
    unsafe_allow_html=True
)




    
   



st.title("Vancouver Business Registrations: Inferences for Market Interpretation")

# Dropdown menu

business_type = st.selectbox("Business Type", sorted(logic.big_types))

local_area = st.selectbox(
    "Neighbourhood (LocalArea)",
    sorted(logic.df_filtered["LocalArea"].dropna().unique()))

if st.button("Run"):

    result = logic.market_interpretation(business_type, local_area)
    st.subheader(result["interpretation_title"])
    st.write(result["interpretation_summary"])
    st.write("Scores")
    st.metric("Concentration", f"{result['concentration_score']:.2f}")
    st.metric("Closure risk", f"{result['closure_risk_score']:.2f}")
    rec = result["recency_score"]
    st.metric("Recency momentum", "N/A" if rec is None else f"{rec:.2f}")

    fig = logic.plot_map(business_type, local_area)

    st.plotly_chart(fig, use_container_width = True)

