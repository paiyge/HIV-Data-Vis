# Import imports:
from imports import *
import get_gdf

# Get GeoDataFrame from get_gdf.py:
gdf = get_gdf.gdf
# Get stateFIPS_df from get_gdf.py:
stateFIPS_df = get_gdf.stateFIPS_df

'''
Bubble Map 1 (US)
'''

# Plot the counties for the contiguous US:
gdf_points = gdf.copy()
gdf_points['geometry'] = gdf_points['geometry'].centroid
# Plot map outline:
fig, ax = plt.subplots(figsize=(16,16))
gdf.plot(ax=ax, 
         color="lightgray", 
         edgecolor="grey", 
         linewidth=0.4)
# Plot bubbles (colored by avg_nh_score, sized by hiv_rate)
gdf_points.plot(ax=ax, 
                #color="#07424A", 
                markersize="hiv_rate",
                alpha=0.7, 
                categorical=False, 
                legend=True,
                column = "avg_nh_score"
                )
ax.axis("off")
plt.axis('equal')
# Set title:
plt.title("Rate of Persons Living with HIV (size) vs. Average Nursing Home Quality (color) by County")


'''
Note that big, purple circles represent high-priority areas 
(Big circle = high rate of PLWH. Purple = low avg NH quality)
'''

# Save & Show the figure:
plt.savefig("figs/us_map1.png")
plt.show()
