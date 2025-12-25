import streamlit as st

import logic

st.title("Vancouver Business Market Signal")

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
    rec = result["recency_momentum_score"]
    st.metric("Recency momentum", "N/A" if rec is None else f"{rec:.2f}")

    fig = logic.plot_map(business_type, local_area)

    st.plotly_chart(fig, use_container_width = True)

    