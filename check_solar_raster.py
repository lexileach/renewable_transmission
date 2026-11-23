
from pathlib import Path
import rasterio

# Locate the solar irradiance raster
raster_path = (
    Path(__file__).resolve().parent
    / "data"
    / "World_GHI_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF"
    / "GHI.tif"
)

# Open and inspect the raster
with rasterio.open(raster_path) as src:
    print("Coordinate system:", src.crs)
    print("Width:", src.width)
    print("Height:", src.height)
    print("Number of bands:", src.count)
    print("Geographic bounds:", src.bounds)
    print("NoData value:", src.nodata)

print("Raster opened successfully!")

