# Import imports:
from imports import *
import get_gdf

# Get GeoDataFrame from get_gdf.py:
gdf = get_gdf.gdf
# Get stateFIPS_df from get_gdf.py:
stateFIPS_df = get_gdf.stateFIPS_df

'''
Use a scatterplot to demonstrate relationship between rates of PLWH
and average nursing home quality by county (including priority jurisdictions):
'''

gdf2 = gdf.copy()

jur = pd.read_csv("https://raw.githubusercontent.com/bicknarnes/DS5110Final/main/HIVdata/jurisdictions.csv")
for i in jur.index:
    state = jur['state'][i]
    if state == "Washington, D.C.": 
        jur['state'][i] = "DC"
        continue
    row = stateFIPS_df[stateFIPS_df['state'] == state]
    code = row['code'].iloc[0]
    jur['state'][i] = code

# Assign values to column describing whether county is a priority jurisdiction:
gdf2['priority'] = 'No'
for i in gdf2.index:
    for j in jur.index:
        if ((gdf2['State'][i] == jur['state'][j]) & 
            (gdf2['County'][i] == jur['county'][j])):
            gdf2['priority'][i] = 'Yes'

# Plot the figure:

fig, ax = plt.subplots(figsize=(20, 12))

g = sns.scatterplot(data=gdf2, x='hiv_rate', y='nh_count', hue='priority', legend = True)
plt.legend(title = 'Priority Jurisdiction?')
plt.xlabel("Rate of Incidence of HIV per 100,000 people by County")
plt.ylabel("Number of Nursing Homes by County")

# Save & Show the figure:
plt.show(g)
plt.savefig('figs/scatter4.png')
