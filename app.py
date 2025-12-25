import streamlit as st

import logic

# Let's make some color helpers

LEVEL_COLORS = {
    "Low": ("#c3e6cb", "#155724"),      # stronger green
    "Typical": ("#f2f2f2", "#333333"),  # unchanged
    "High": ("#f5c6cb", "#721c24")      # stronger red
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

# Now on to the actual UI:

st.title("Vancouver Business Registrations: Inferences for Market Interpretation")

st.image("https://images.pexels.com/photos/29072584/pexels-photo-29072584.jpeg",
            caption="Vancouver Skyline (Credit: Luke Lawreszuk)",
            use_container_width= True)



# Dropdown menu

business_type = st.selectbox("Business Type", sorted(logic.big_types))

local_area = st.selectbox(
    "Neighbourhood (LocalArea)",
    sorted(logic.df_filtered["LocalArea"].dropna().unique()))


# Below has features to classify colors for metrics, classes, and has a button to go to the methods behind calculation.

if st.button("Run"):

    result = logic.market_interpretation(business_type, local_area)
    st.subheader(result["interpretation_title"])
    st.write(result["interpretation_summary"])

    st.subheader("Scores")

    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.metric("Concentration score", f"{result['concentration_score']:.2f}")
    with c2:
        st.markdown(render_level(result["concentration_level"]), unsafe_allow_html=True)
    with c3:
        st.markdown(
    """
    <a href="#concentration" style="
        display:inline-block;
        padding:6px 10px;
        border-radius:8px;
        background:#f2f2f2;
        color:#666;
        text-decoration:none;
        border:1px solid rgba(0,0,0,0.08);
        font-size:0.85rem;
    ">How was this calculated?</a>
    """,
    unsafe_allow_html=True)

    c4, c5, c6 = st.columns([2, 1, 2])
    with c4:
        st.metric("Closure risk score", f"{result['closure_risk_score']:.2f}")
    with c5:
        st.markdown(render_level(result["closure_risk_level"]), unsafe_allow_html=True)
    with c6:
        st.markdown(
    """
    <a href="#closure-risk" style="
        display:inline-block;
        padding:6px 10px;
        border-radius:8px;
        background:#f2f2f2;
        color:#666;
        text-decoration:none;
        border:1px solid rgba(0,0,0,0.08);
        font-size:0.85rem;
    ">How was this calculated?</a>
    """,
    unsafe_allow_html=True)

    c7, c8, c9 = st.columns([2, 1, 2])
    with c7:
        rec = result["recency_score"]
        st.metric("Recency Score", "N/A" if rec is None else f"{rec:.2f}")
    with c8:
        st.markdown(render_level("Typical"), unsafe_allow_html=True)  # always neutral
    with c9:
        st.markdown(
    """
    <a href="#recency" style="
        display:inline-block;
        padding:6px 10px;
        border-radius:8px;
        background:#f2f2f2;
        color:#666;
        text-decoration:none;
        border:1px solid rgba(0,0,0,0.08);
        font-size:0.85rem;
    ">How was this calculated?</a>
    """,
    unsafe_allow_html=True)


  

    fig = logic.plot_map(business_type, local_area)

    st.plotly_chart(fig, use_container_width = True)

    st.divider()
    st.header("About this Project")


# Now we will give the reader a quick summary of what we've done here.

st.markdown("""
The City of Vancouver has a rich and diverse business landscape, and something that represents this
is a dataset in their Open Data Portal. Said dataset holds records of the recent business registries
from 2024 onwards. It is rather large, with over 130,000 registrations. I took this size as an
opportunity to make inferences on the market as a whole.

These inferences are based on factors such as the concentration, recency, and closures of the
registrations of a certain business type and location. As with anything involving data, it was
imperative to use some discretion to create the metrics that analyzed these factors. This analysis,
and further cleaning and manipulation of the data, is further outlined in the .ipynb file, which can
be found in the linked GitHub repository for this project below.

However, for a baseline level of clarity here, the way the metrics were calculated, and how they can
be interpreted, are written below:
""")

st.markdown('<div id="concentration"></div>', unsafe_allow_html=True)
st.markdown("""
**Concentration Score:**

The concentration score measures how common a given business type is in a specific neighbourhood,
relative to how common it is across Vancouver as a whole.

For a selected business type in a neighbourhood:

First, compute the proportion of all issued businesses in that neighbourhood that are of the selected
business type.

Then, compute the proportion of all issued businesses citywide that are of that same business type.

The concentration score is the ratio of these two proportions.

This metric deals with the question, “How common is this business here, and how does that deal with
how common it is overall?”

For this score, a lower score (1 is the baseline) would mean that a business type is less common in
the neighbourhood than it is citywide, and a higher score would mean that it is more concentrated
than expected, indicating a competitive local market.
""")

st.markdown('<div id="closure-risk"></div>', unsafe_allow_html=True)
st.markdown("""
**Closure Risk Score:**

The closure risk score measures how likely businesses of a given type are to close or become
inactive in a specific neighbourhood, relative to the citywide norm for that business type.

For a selected business type in a neighbourhood:

Compute the closure rate as the number of businesses of that type that have closed or become
inactive, divided by the number of currently issued businesses in that neighbourhood.

Then, compute the same closure rate citywide for the same business type.

The closure risk score is the ratio of the local closure rate to the citywide closure rate.

For this score, a lower score (1 is the baseline) would mean that businesses of this type tend to
survive better than average in the neighbourhood, and a higher score would indicate that businesses
of this type close at a higher-than-average rate at this location, indicating elevated risk.
""")

st.markdown('<div id="recency"></div>', unsafe_allow_html=True)
st.markdown("""
**Recency Score:**

The recency score captures how recently new businesses of a given type have been opening in a
neighbourhood, compared to the citywide trend. Rather than counting all openings, this metric
focuses on recent momentum.

For a selected business type in a neighbourhood:

To compute, first identify the most recent one-seventh (≈14%) of issued business registrations.

Then, compute the average issue date for the selected neighbourhood, and for the city as a whole.

The recency score compares the proportion of these two, or how recent the neighbourhood’s openings
are relative to the citywide baseline. A higher score indicates more recent openings (the specific
math for this is a bit more complicated, and can be found in the .ipynb file).

The way this score is interpreted depends on the other two factors. Since it is context dependent,
it works with the other two metrics to create an overall interpretation.
""")

st.markdown("""
Taken together, these three metrics provide complementary signals about market saturation, risk,
and momentum. Their combination indicates some sort of narrative about the given business essay type
in the given area, which this app is designed to present.

As with anything in life, much of the decision to start a type of business at a certain location
must be based on discretion and context. While this app is designed to offer support on that
decision, it is meant to be used as a complementary tool, or at the very least, a presentation of
concentration, recency, and risk.

Businesses can explode, and also implode based on a nearly infinite number of factors that go beyond
what can be recorded on a registry dataset. However, using this analysis on this dataset can provide
information on what can generally be expected.
""")










