# Vancouver Business Registrations: Inferences for Market Interpretation

## Introduction:

The City of Vancouver has a rich and diverse business landscape, and something that represents this is a dataset in their Open Data Portal. Said dataset holds records of the recent business registries from 2024 onwards. It is rather large, with over 130,000 registrations. I took this size as an opportunity to make inferences on the market as a whole. These inferences are based on factors such as the concentration, recency, and closures of the registrations of a certain business type and location. As with anything involving data, it was imperative to use some discretion to create the metrics that analyzed these factors. This analysis, and further cleaning and manipulation of the data, is further outlined in the .ipynb file, which can in this repository. It contains the majority of analysis and decision making.

## Metrics Used:

However, for a baseline level of clarity here, the way the metrics were calculated, and how they can be interpreted, are written below:

**Concentration Score:**

The concentration score measures how common a given business type is in a specific neighbourhood, relative to how common it is across Vancouver as a whole.

For a selected business type in a neighbourhood:

- First, compute the proportion of all issued businesses in that neighbourhood that are of the selected business type

- Then, compute the proportion of all issued businesses citywide that are of that same business type.

- The concentration score is the ratio of these two proportions.

This metric deals with the question, “How common is this business here, and how does that deal with how common it is overall?”

For this score, a lower score (1 is the baseline) would mean that a business type is less common in the neighbourhood than it is citywide, and a higher score would mean that is more concentrated than expected, indicating a competitive local market.


**Closure Risk Score:**

The closure risk score measures how likely businesses of a given type are to close or become inactive in a specific neighbourhood, relative to the citywide norm for that business type.

For a selected business type in a neighbourhood:

- Compute the closure rate as the number of businesses of that type that have closed or become inactive, divided by the number of currently issued businesses in that neighbourhood.

- Then, compute the same closure rate citywide for the same business type.

- The closure risk score is the ratio of the local closure rate to the citywide closure rate.

For this score, a lower score (1 is the baseline) would mean that businesses of this type tend to survive better than average in the neighbourhood, and a higher score would indicate that businesses of this type close at a higher-than-average rate at this location, indicating elevated risk.


**Recency Score:**

The recency score captures how recently new businesses of a given type have been opening in a neighbourhood, compared to the citywide trend.
Rather than counting all openings, this metric focuses on recent momentum.

- For a selected business type in a neighbourhood:

- To compute, first identify the most recent one-seventh (≈14%) of issued business registrations.

- Then, Compute the average issue date for the selected neighbourhood, and for the city as a whole.

The recency score compares  the proportion of these two, or how recent the neighbourhood’s openings are relative to the citywide baseline. A higher score indicates more recent openings (the specific math for this is a bit more complicated, and can be found in the .ipynb file)

The way this score is interpreted depends on the other two factors. Since it is context dependent, it works with the other two metrics to create an overall interpretation.


## Conclusive Comments:

Taken together, these three metrics provide complementary signals about market saturation, risk, and momentum. Their combination indicates some sort of narrative about the given business essay type in the given area, which this app is designed to present. 
As with anything in life, much of the decision to start a type of business at a certain location must be based on discretion and context. While this app is designed to offer support on that decision, it is meant to be used as a complementary tool, or at the very least, a presentation of concentration, recency, and risk.  Businesses can explode, and also implode based on a nearly infinite number of factors, that go beyond what can be recorded on a registry dataset. However, using this analysis on this dataset can provide information on what can generally be expected.








