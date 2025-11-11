# Your Python code here
print("Business Licences Vancouver Analysis")
import pandas as pd
from pandas._libs.tslibs.offsets import BusinessMixin

df = pd.read_csv("business-licences.csv", sep=";", low_memory = False)


#print(df.shape)

print(df.columns)

pd.set_option('display.max_columns', None)

#print(df.head(30))

#print(df.sample(10))

#print(df.info())

#print(df.isnull().sum())

'''
Number of null values for each variable:

FOLDERYEAR                    0
LicenceRSN                    0
LicenceNumber                 0
LicenceRevisionNumber         0
BusinessName               8669
BusinessTradeName         81937
Status                        0
IssuedDate                16819
ExpiredDate               16801
BusinessType                  0
BusinessSubType          117996
Unit                     100159
UnitType                 100328
House                     60127
Street                    60115
City                         35
Province                     48
Country                   25514
PostalCode                60628
LocalArea                  2717
NumberofEmployees             0
FeePaid                   64390
ExtractDate                   0
Geom                      65252
geo_point_2d              65252



'''

#print(df.duplicated().sum())

# Runs to 0 duplicates


#print(df['BusinessType'].unique())

# come back to maybe connect some speciifc genres later!!!


print(df['Status'].value_counts())

'''

Status
Issued                  109119
Pending                  11005
Gone Out of Business      4811
Inactive                  4112
Cancelled                 2693


'''

#print(df['NumberofEmployees'].value_counts())

#print(df['NumberofEmployees'].max())

# Max # of employees is 5876

print(df.groupby(['LocalArea', 'BusinessType']))

# Grouped by local area and business type

#print(df['LocalArea'].value_counts())

'''
LocalArea
Downtown                    31389
Fairview                    10430
Kitsilano                    8511
Mount Pleasant               8259
Out of Town                  7823
West End                     6945
Kensington-Cedar Cottage     6735
Grandview-Woodland           5605
Renfrew-Collingwood          5415
Sunset                       4790
Marpole                      4475
Hastings-Sunrise             4295
Riley Park                   4177
Strathcona                   4157
Victoria-Fraserview          2677
Killarney                    2326
Dunbar-Southlands            2245
Arbutus-Ridge                1758
Kerrisdale                   1717
West Point Grey              1659
South Cambie                 1380
Oakridge                     1318
Shaughnessy                   898
UBC                            27
Arbutus Ridge                  12

total 193136

''' 

df1 = df.filter([])
