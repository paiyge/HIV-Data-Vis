# Import imports:
from imports import *
import get_gdf

# Get GeoDataFrame from get_gdf.py:
gdf = get_gdf.gdf
# Get stateFIPS_df from get_gdf.py:
stateFIPS_df = get_gdf.stateFIPS_df

'''
Bubble Mapping!

By STATE = Texas, with overlay of [riority jurisdictions in red
'''

state_name = 'TX'

# Plot the counties for the contiguous US:
gdf2 = gdf[gdf['State'] == state_name].copy()
gdf_points = gdf2.copy()

gdf_points['geometry'] = gdf_points['geometry'].centroid

fig, ax = plt.subplots(figsize=(16,16))
gdf2.plot(ax=ax, 
         color="lightgray", 
         edgecolor="grey", 
         linewidth=0.4)
# Plot bubble map:
gdf_points.plot(ax=ax, 
                #color="#07424A", 
                #c=gdf["avg_nh_score"], # I don't know what these colors mean but they're doing something
                markersize="hiv_rate",
                alpha=0.7, 
                categorical=False, 
                legend=True,
                column = "avg_nh_score"
                )
ax.axis("off")
plt.axis('equal')

# Plot priority jurisdictions in red over bubble map:
for i in jur.index:
    county = jur['county'][i]
    state = jur['state'][i]
    if state != state_name: continue
    if type(county) != str: # if no county is listed (use whole state)
        data = gdf[gdf['State'] == state]
        data.plot(ax=ax,
              color = 'red')
        continue
    
    data1 = gdf[gdf['County'] == county]
    data2 = data1[data1['State'] == state]

    # Exception for San Juan, PR (since we don't have any AIDs data there)
    if data2.shape[0] == 0:
        continue
    
    # Plot the county/state:
    data2.plot(ax=ax,
              color = 'red',
              alpha = .6);
    
plt.title("Rate of Persons Living with HIV (size) vs. Average Nursing Home Quality (color) by County\nOverlayed with Identified Priority Jurisdictions (in red)\nState = Texas")

# Save & Show the figure:
plt.savefig("figs/texas_map2.png")
plt.show()
