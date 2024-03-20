'''
This file includes (almost) all data collection, formatting, and preprocessing. 

To be used in other files thusly:

import get_gdf

gdf = get_gdf.gdf
stateFIPS_df = get_gdf.stateFIPS_df

'''

from imports import *

''' Installs '''
%pip install geopandas
%pip install ipython
%pip install descartes

# Get data for HIV rates by county, Nursing Home Provider information:
county_url = "https://raw.githubusercontent.com/bicknarnes/DS5110Final/main/HIVdata/county.csv"
provider_url = "https://raw.githubusercontent.com/bicknarnes/DS5110Final/main/HIVdata/NH_ProviderInfo_Oct2022.csv"

'''
county.csv contains rates of persons living with HIV
by county in the year 2020.

Negative rates indicate that data could not be published
(because of a small rate or a small town -- privacy issues)
'''

'''
providerinfo csv contains data on Nursing Homes that recieve medicare/medicaid funding
importatly, it contains data on all NHs by county, and the overall quality rating out of 5 stars for each.
'''

# Import the HIV Rates dataset, drop NAs:
county_df = pd.read_csv(county_url).dropna()
# Rename features:
df2 = county_df.copy()
df2 = df2.rename(columns={'county': 'County', 'state': 'State', 'Rates of Persons Living with HIV, 2020': 'Rate'})
# Drop undefined rows (Rate='undefined') as well as all negative values (Rates containing '-'):
df2 = df2[df2.Rate.str.isnumeric()]
# Convert rates from string to numeric value:
df2['Rate'] = pd.to_numeric(df2['Rate'])

# Import the provider data set. Only want state, county, and rating features:
provider_df = pd.read_csv(provider_url, sep=",", encoding='cp1252', usecols = ['Provider County Name', 'Provider State', 'Overall Rating']).dropna()
# Rename features:
provider_df = provider_df.rename(columns={'Provider County Name': 'County', 'Provider State': 'State', 'Overall Rating': 'Rating'})

# Get average NH score by county by state:
group = provider_df.groupby(['County', 'State'])
county_nh_scores = group['Rating'].mean()
# Get number of NHs per county by state:
county_nh_count = group.size()

'''
stateFIPS contains State names, 2-letter state codes, state FIPS codes, and regions
'''
states_url = 'https://raw.githubusercontent.com/bicknarnes/DS5110Final/main/GeoData/stateFIPS.csv'
''' want to convert between 'state' and 'code' colums '''
# Import states labels data
states_df = pd.read_csv(states_url, usecols = ['state', 'code'])
#print(states_df.info)

# Convert the 'state' column in df2 (county.csv) from full name to state code:
df2['State'] = df2['State'].map(states_df.set_index('state')['code'])

'''
Merge dataframes into one:
'''
scores_index = county_nh_scores.index.to_frame(index = False)
# Get dataframe containing average nursing home scores by county:
scores_df = pd.DataFrame(data=county_nh_scores.values, columns=['avg_nh_score'])
# Get dataframe containing total nursing home counts by county:
counts_df = pd.DataFrame(data=county_nh_count.values, columns=['nh_count'])

# Merge dataframes:
df0 = pd.merge(scores_df, counts_df, left_index=True, right_index=True)

# Generate dataframe with avg NH score, county, state:
df00 = pd.merge(df0, scores_index, left_index=True, right_index=True)

# Merge with dataframe containing HIV rates by county/state:
cols = ['State', 'County']
dfX = df00.merge(df2, on=cols)
# Note that we lost a bunch of rows after this merge ^
# Because we dropped those rows without usable HIV data.




'''
                             MAPPING / GEOPANDAS:
'''

'''
Reading this shapefile from where I uploaded it locally:
(downloaded from:
https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
)
'''

counties = gpd.read_file("GeoData/cb_2018_us_county_500k.shp")

'''
NAME corresponds to county name 
STATEFP corresponds to a numeric value assigned to each state 

(FIPS -- Federal Information Processing Standards -- State Codes)

'''

# Project map coordinates to Mercator: 
counties = counties.to_crs("EPSG:3395")

# Remove Alaska and Hawaii (02 and 15):
# and apparently a bunch of other stuff (anything over 56 isn't a US state)
contig = counties[counties['STATEFP'] != '02']
contig = contig[contig['STATEFP'] != '15']
# Remove American Samoa:
contig = contig[contig['STATEFP'] != '60']
# Remove Guam:
contig = contig[contig['STATEFP'] != '66']
# Remove Northern Marianas:
contig = contig[contig['STATEFP'] != '69']
# Remove Puerto Rico:
contig = contig[contig['STATEFP'] != '72'] 
# Remove Virgin Islands:
contig = contig[contig['STATEFP'] != '78']




'''
stateFIPS contains State names, 2-letter state codes, state FIPS codes, and regions
'''

stateFIPS_url = 'https://raw.githubusercontent.com/bicknarnes/DS5110Final/main/GeoData/stateFIPS.csv'

'''
Originally got this data from:

https://www.bls.gov/respondents/mwr/electronic-data-interchange/appendix-d-usps-state-abbreviations-and-fips-codes.htm
'''
# EDIT: Added 'region' as a column in this data for later use
'''
    Basically, the geodataframe 'contig' above has counties listed by name
    (NAME) as well as state FIPS code (STATEFP). Therefore, we can match up
    each county in our HIV data to the corresponding county in the geo data
    by comparing 2-letter state code to state FIPS code and matching up the
    county names. 

    In this manner, we can assign HIV rate / NH quality/availability scores 
    to each county within the geodataframe by comparing to the HIV data. 
'''
# EDIT: Added 'region' as a column in this data for later use

# Import stateFIPS dataset
stateFIPS_df = pd.read_csv(stateFIPS_url, usecols = ['state', 'code', 'fips', 'region'])
# Get state FIPS codes as strings:
stateFIPS_df['STATEFP'] = stateFIPS_df['fips'].astype(str)

# Add '0' before single-digit fips nums (to make all 2-digit codes):
for index in stateFIPS_df.index:
    # get FIPS code:
    fips = stateFIPS_df['STATEFP'][index]
    # If 1-digit, add a 0 prefix:
    if len(fips) == 1:
        fips = '0' + fips
    # Reassign value:
    stateFIPS_df['STATEFP'][index] = fips
    
'''
Add State, nh_score, nh_count, HIV rate columns to geodataframe:
'''

# Add state codes:
gdf = contig.copy()
gdf = gdf.rename(columns={"NAME":"County"})
gdf['State'] = np.nan

for i in gdf.index:
    statefp = gdf['STATEFP'][i]
    state_code = stateFIPS_df[stateFIPS_df['STATEFP'] == statefp]['code']
    state_code = state_code.iloc[0]
    gdf['State'][i] = state_code

# Add nh_score, nh_count, HIV rate columns
gdf['avg_nh_score'] = np.nan
gdf['nh_count'] = np.nan
gdf['hiv_rate'] = np.nan # In dfX, this is "Rate"
# dfX has "County" and "State"

for i in gdf.index:
    state = gdf['State'][i]
    county = gdf['County'][i]
    row = dfX[dfX['County'] == county][dfX['State'] == state]

    # Because we dropped certain counties in the HIV dataframe, 
    # we must likewise skip those counties here:
    if (row.shape[0] == 0) : continue

    nh_score = row['avg_nh_score'].iloc[0]
    
    nh_count = row['nh_count'].iloc[0]
    hiv_rate = row['Rate'].iloc[0]
    #state_code = stateFIPS_df[stateFIPS_df['STATEFP'] == statefp]['code']
    #state_code = state_code.iloc[0]
    #gdf['State'][i] = state_code
    gdf['avg_nh_score'][i] = nh_score
    gdf['nh_count'][i] = nh_count
    gdf['hiv_rate'][i] = hiv_rate

'''
gdf now contains everything we need!
'''

'''
Add 'region' column to dataframe:
'''

gdf['Region'] = np.nan

for i in gdf.index:
    state = gdf['State'][i]
    row = stateFIPS_df[stateFIPS_df['code'] == state]
    region = row['region'].iloc[0] 
    gdf['Region'][i] = region

