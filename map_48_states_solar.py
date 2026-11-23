from pathlib import Path
import rasterio
from rasterio.enums import Resampling
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

# --------------------------------------------------
# 1. File paths
# --------------------------------------------------
project_folder = Path(__file__).resolve().parent
raster_path = project_folder / "data" / "solar_ghi_lower48.tif"

# U.S. Census state boundaries shapefile (reads directly from URL)
states_url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip"

# --------------------------------------------------
# 2. Read the solar raster
# --------------------------------------------------
with rasterio.open(raster_path) as src:
    print("Opening solar raster...", flush=True)

    scale = max(src.width / 1600, src.height / 1000, 1)
    new_width = int(src.width / scale)
    new_height = int(src.height / scale)

    ghi = src.read(
        1,
        out_shape=(new_height, new_width),
        resampling=Resampling.average,
        masked=True
    )

    bounds = src.bounds
    raster_crs = src.crs

    print("Raster loaded successfully!", flush=True)
    print("Raster CRS:", raster_crs, flush=True)

# Convert masked values to NaN
ghi = ghi.astype("float32").filled(np.nan)

# --------------------------------------------------
# 3. Read state boundaries
# --------------------------------------------------
print("Loading state boundaries...", flush=True)
states = gpd.read_file(states_url)

# Reproject states to match the raster CRS if needed
if states.crs != raster_crs:
    states = states.to_crs(raster_crs)

# Keep only the contiguous U.S. + DC
exclude = ["Alaska", "Hawaii", "Puerto Rico", "United States Virgin Islands", "Commonwealth of the Northern Mariana Islands", "Guam", "American Samoa"]
states = states[~states["NAME"].isin(exclude)]

# --------------------------------------------------
# 4. Plot
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 8))

img = ax.imshow(
    ghi,
    extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
    origin="upper",
    cmap="inferno",
    interpolation="nearest"
)

# Add state boundaries
states.boundary.plot(ax=ax, linewidth=0.6, edgecolor="white")

# Colorbar
cbar = plt.colorbar(img, ax=ax, shrink=0.75)
cbar.set_label("Global Horizontal Irradiation (kWh/m²/day)")

# Titles and labels
ax.set_title("Solar Irradiance Across the Contiguous United States", fontsize=16)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.set_xlim(-125, -66)
ax.set_ylim(24, 50)

plt.tight_layout()

# --------------------------------------------------
# 5. Save the figure
# --------------------------------------------------
output_path = project_folder / "solar_irradiance_map_with_states.png"
plt.savefig(output_path, dpi=200, bbox_inches="tight")

print("Map saved to:", output_path, flush=True)

plt.show()