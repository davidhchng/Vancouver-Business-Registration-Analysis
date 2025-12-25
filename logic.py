# Backend logic for website- for how we came to this, look
# at .ipynb for analysis walkthrough

import pandas as pd

import numpy as np

import plotly.express as px

import math

# Let's do this



df = pd.read_csv("business-licences.csv", sep=";", low_memory = False)

df1 = df.copy()

df1['LocalArea'] = df1['LocalArea'].replace({'Arbutus Ridge': 'Arbutus-Ridge'})

df1 = df1[df1['LocalArea'] != 'UBC'].copy()

df1 = df1[df1['geo_point_2d'].notnull()].copy()

df1[['lat', 'long']] = df1['geo_point_2d'].str.split(',', expand = True)

df1[['lat', 'long']] = df1[['lat', 'long']].astype(float)




drop_types = [
    'Information Communication Technology',
    'Digital Entertainment and Interactive Technology',
    'Publishing and Journalism Services',
    'Marketing Public Relations Advertising and Event Promotion Services',
    'Consulting and Management Services',
    'Business Support Services',
    'Design Services',
    'Architectural and Engineering Services',
    'Legal Services',
    'Insurance Services',
    'Financial Services',
    'Financial Institution',
    'Brokerage Services',
    'Real Estate Services',
    'Artist Agency',
    'Association or Society',
    'Mining Services',
    'Forestry Services',
    'Oil Gas and Other Fuels',
    'Logistics Services',
    'Transportation and Support Services',
    'Warehouse Operator - Food',
    'Warehouse Operator - Non-Food',
    'Wholesale Dealer - Food',
    'Wholesale Dealer - Non-Food',
    'Non-Food Manufacturer Assembler and Processor',
    'Food Manufacturer Assembler and Processor',
    'Recycling and Resource Recovery Services',
    'Waste Collection and Hauling Services',
    'Marine Service Station',
    'Soliciting For Charity',
    'Cannabis Licence Application',
    'Liquor License Application',
    'Temp Liquor Licence Amendment',
    'Adult Retail Store *Historic*'
]

df_filtered_0 = df1[~df1['BusinessType'].isin(drop_types)].copy()

infrastructure_types = [
    'Mining Services',
    'Forestry Services',
    'Oil Gas and Other Fuels',
    'Logistics Services',
    'Transportation and Support Services',
    'Warehouse Operator - Food',
    'Warehouse Operator - Non-Food',
    'Wholesale Dealer - Food',
    'Wholesale Dealer - Non-Food',
    'Non-Food Manufacturer Assembler and Processor',
    'Food Manufacturer Assembler and Processor',
    'Recycling and Resource Recovery Services',
    'Waste Collection and Hauling Services',
    'Marine Service Station',
    'Parking Area / Garage'
]


df_filtered_1 = df_filtered_0[~df_filtered_0['BusinessType'].isin(infrastructure_types)].copy()

type_counts = df_filtered_1['BusinessType'].value_counts()

big_types = type_counts[type_counts > 644]

big_types = big_types.index.tolist()

df_filtered = df_filtered_1[df_filtered_1['BusinessType'].isin(big_types)].copy()

df_issued = df_filtered[df_filtered['Status'] == "Issued"].copy()


def concentration_score(business_type, local_area):

    A = df_issued[
            (df_issued['BusinessType'] == business_type) &
            (df_issued['LocalArea'] == local_area)].shape[0]

    B = df_issued[df_issued['LocalArea'] == local_area].shape[0]

    C = df_issued[df_issued['BusinessType'] == business_type].shape[0]

    D = df_issued.shape[0]

    if B == 0 or D == 0 or C ==0:
        return 0

    location_prop = A / B

    total_prop = C / D

    if total_prop == 0:
        return 0

    return location_prop / total_prop

#print(concentration_score('Restaurant', 'Downtown'))

gone_statuses = ['Gone Out of Business', 'Inactive']

def relative_closure_risk(business_type, local_area):

    count_active = df_issued[ 
        (df_issued['BusinessType'] == business_type) &
        (df_issued['LocalArea'] == local_area)].shape[0]

    count_closure = df_filtered[
        (df_filtered['BusinessType'] == business_type) &
        (df_filtered['LocalArea'] == local_area) &
        (df_filtered['Status'].isin(gone_statuses))].shape[0]

    if count_active == 0:
        return 0

    closure_rate = count_closure / count_active

    closure_rate = count_closure / count_active

    city_active = df_issued[df_issued['BusinessType'] == business_type].shape[0]
    city_closure = df_filtered[(df_filtered['BusinessType'] == business_type) &
                            (df_filtered['Status'].isin(gone_statuses))].shape[0]

    if city_active == 0:
        return 0
    baseline_closure_rate = city_closure / city_active

    if baseline_closure_rate == 0:
        return 0

    relative_risk = closure_rate / baseline_closure_rate
    return relative_risk



#print(relative_closure_risk('Restaurant', 'West Point Grey'))

df_issued['IssuedDate_dt'] = pd.to_datetime(df_issued['IssuedDate'], errors = 'coerce', utc = True)

df_date = df_issued.dropna(subset = ['IssuedDate_dt']).copy()

today_ref = df_issued['IssuedDate_dt'].max()

def relative_recency(business_type, local_area):

    def mean_of_recent_fraction(sub):
        n= sub.shape[0]

        if n == 0:
            return 0, None


        k = int(math.ceil(1/7 * n))

        recent = sub.sort_values('IssuedDate_dt', ascending = False).head(k)

        
        mean_dt = pd.to_datetime(recent['IssuedDate_dt'].astype('int64').mean(), utc = True)

        return k, mean_dt

    local_sub  = df_date[
                         (df_date['BusinessType'] == business_type) &
                         (df_date['LocalArea'] == local_area)]
    k_local, local_mean_dt = mean_of_recent_fraction(local_sub)
    if local_mean_dt is None:
        return None


    city_sub = df_date[df_date['BusinessType'] == business_type]
    k_city, city_mean_dt = mean_of_recent_fraction(city_sub)
    if city_mean_dt is None:
        return None


    local_age_days = (today_ref - local_mean_dt).days
    baseline_age_days = (today_ref - city_mean_dt).days

    if baseline_age_days == 0:
        return 0

    if local_age_days == 0:
        return 0    

    rel = local_age_days / baseline_age_days
    
    rel = 1/rel

    return rel

#print(relative_recency('Restaurant', 'Marpole'))

def classify_score(x):

    if x is None:
        return "Typical"

    if x < 0.9:

        return "Low"

    if x > 1.1:
        return "High"

    return "Typical"


def market_interpretation(business_type, local_area):

    conc_score = concentration_score(business_type, local_area)
    
    risk_score = relative_closure_risk(business_type, local_area)

    recency_score = relative_recency(business_type, local_area)


    conc_level = classify_score(conc_score)

    risk_level = classify_score(risk_score)

    recency_level = classify_score(recency_score)


    if risk_level == "High":
        title = "High Risk"
        summary = (
            "Businesses of this type close or become inactive here at an unusually high rate. "
            "Even if demand appears strong, survivability is poor, making entry risky."
        )

    elif conc_level == "Low" and recency_level == "Low":

         title = "Underserved and Healthy"
         summary = (
            "Few competitors and little recent entry activity, with no elevated closure risk. "
            "This may indicate unmet demand or white space, though discretion is still required."
        )


    elif conc_level == "Low" and recency_level == "High":
        title = "Emerging Market"
        summary = (
            "Historically sparse market with strong recent entry momentum. "
            "This suggests early growth, offering opportunity, but not without uncertainty."
        )

    elif conc_level == "High" and recency_level == "High":
        title = "Competitive Growth"
        summary = (
            "Crowded market with many recent entrants. Demand may be strong, "
            "but competition is intense and success depends on differentiation."
        )

    elif conc_level == "High" and recency_level == "Low":
        title = "Saturated / Mature"
        summary = (
            "Crowded market with few recent openings. "
            "The market appears mature or slowing, making entry difficult without a clear differentiating factor."
        )

    elif conc_level == "Typical":
        title = "Typical / Stable Market"
        summary = (
            "Market size and structure closely resemble the citywide norm for this business type. "
            "No strong directional signals are present, so full discretion must be used."
        )

    else:
        title = "Mixed / Ambiguous"
        summary = (
            "Signals conflict or are weak. Quantitative metrics alone do not point to a clear conclusion, "
            "and qualitative context or external data may be necessary."
        )


    return {
        "business_type": business_type,
        "local_area": local_area,

        "concentration_score": conc_score,
        "concentration_level": conc_level,

        "closure_risk_score": risk_score,
        "closure_risk_level": risk_level,

        "recency_score": recency_score,
        "recency_level": recency_level,

        "interpretation_title": title,
        "interpretation_summary": summary
    }


#print(market_interpretation("Restaurant", "Sunset"))


def plot_map(business_type, local_area):


    df_plot = df_filtered[['BusinessType', 'LocalArea', 'Status', 'lat', 'long']].copy()

    df_plot = df_plot[df_plot['BusinessType'] == business_type].copy()


    df_plot['Status Group'] = np.where(df_plot['Status'] == 'Issued',
                                        'Issued',
                                    np.where(df_plot['Status'].isin(['Gone Out of Business', 'Inactive']),
                                             'Closure/Inactive',
                                             'Other'
                                            )
                                       )


    
    df_plot['Group'] = 'Background'

    is_type = df_plot["BusinessType"] == business_type
    is_type_and_area = is_type & (df_plot["LocalArea"] == local_area)

    df_plot.loc[is_type, "Group"] = "Citywide Registration"
    df_plot.loc[is_type_and_area, "Group"] = f"{local_area} Registration"


    fig = px.scatter(
        df_plot,
        x = "long",
        y = "lat",
        color = "Group",
        symbol = "Status Group",
        opacity = 0.7,
        hover_data = ["BusinessType", "LocalArea"],
        title = f"{business_type} in {local_area} vs Vancouver",
        color_discrete_map = {
            'Background': '#d9d9d9',
            'Citywide Registration': '#9f9f9c',
            f'{local_area} Registration': '#0C06F7' # Distinct colors
        },
        symbol_map = {
            'Issued': 'circle',
            'Exit': 'x',
            'Other': 'triangle-up' # Distinct shapes
    }
            
    )

    fig.update_layout(
        height = 1700,
        width = 2500,
        xaxis_title = "Longitude",
        yaxis_title = "Latitude",
        legend = dict(
            orientation = "h",
            yanchor = "top",
            y = -0.05,
            xanchor = "center",
            x = 0.5,
            title_text = "" # remove default combined title
        ),
        margin = dict(l = 40, r = 40, t = 80, b = 40)
    )
            
                      
        

    return fig


#fig = plot_map("Restaurant", "Downtown")
#fig.show()
