Code for reproducing results.

- imports.py: imports necessary to run the rest of the files. 
- get_gdf.py: imports all required data and formats it all into one GeoDataFrame "gdf" for use in all remaining files. Those map and scatterplot files import gdf (the GeoDataFrame containing all relevent data) from get_gdf.py. 
- To use this GeoDataFrame yourself, simply include the following code in a file in the same directory:

```
import get_gdf

gdf = get_gdf.gdf
```

