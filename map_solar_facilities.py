
from pathlib import Path
import rasterio
from rasterio.enums import Resampling
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. File paths
project_folder = Path(__file__).resolve().parent

raster_path = project_folder / "data"/ "solar_ghi_lower48.tif"
solar_csv = project_folder / "output"/ ".csv"

states_url = (
    "https://www2.census.gov/geo/tiger/GENZ2023/shp/"
    "cb_2023_us_state_20m.zip"
)

# 2. Load solar irradiation raster
with rasterio.open(raster_path) as src:

    scale = max(src.width / 1600, src.height / 1000, 1)

    width = int(src.width / scale)
    height = int(src.height / scale)

    ghi = src.read(
        1,
        out_shape=(height, width),
        resampling=Resampling.average,
        masked=True
    )

    bounds = src.bounds
    raster_crs = src.crs

ghi = ghi.astype("float32").filled(np.nan)

# 3. Load state boundaries
print("Loading state boundaries...", flush=True)

states = gpd.read_file(states_url)
states = states.to_crs(raster_crs)

exclude = [
    "Alaska",
    "Hawaii",
    "Puerto Rico",
    "United States Virgin Islands",
    "Commonwealth of the Northern Mariana Islands",
    "Guam",
    "American Samoa"
]

states = states[~states["NAME"].isin(exclude)]

# 4. Load solar facility data
print("Loading solar facilities...", flush=True)

solar = pd.read_csv(solar_csv)

print("Columns:", solar.columns.tolist())

solar["latitude"] = pd.to_numeric(
    solar["latitude"], errors="coerce"
)
solar["longitude"] = pd.to_numeric(
    solar["longitude"], errors="coerce"
)

solar = solar.dropna(subset=["latitude", "longitude"])

# 5. Convert facility coordinates into map geometry
solar_points = gpd.GeoDataFrame(
    solar,
    geometry=gpd.points_from_xy(
        solar["longitude"],
        solar["latitude"]
    ),
    crs="EPSG:4326"
).to_crs(raster_crs)

# 6. Keep facilities in the contiguous U.S.
us_area = states.geometry.union_all()
solar_points = solar_points[
    solar_points.geometry.intersects(us_area)
]

print("Facilities mapped:", len(solar_points))

# 7. Plot the map
fig, ax = plt.subplots(figsize=(15, 9))

img = ax.imshow(
    ghi,
    extent=[
        bounds.left,
        bounds.right,
        bounds.bottom,
        bounds.top
    ],
    origin="upper",
    cmap="inferno"
)

states.boundary.plot(
    ax=ax,
    edgecolor="white",
    linewidth=0.6
)

solar_points.plot(
    ax=ax,
    color="cyan",
    markersize=4,
    alpha=0.65,
    marker="o",
    label="Existing solar facilities"
)

# 8. Add legend and labels
cbar = plt.colorbar(img, ax=ax, shrink=0.75)
cbar.set_label(
    "Global Horizontal Irradiation (kWh/m²/day)"
)

ax.legend(loc="lower left")

ax.set_title(
    "Solar Irradiance and Existing Solar Facilities "
    "in the Contiguous United States",
    fontsize=15
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.set_xlim(-125, -66)
ax.set_ylim(24, 50)

plt.tight_layout()

# 9. Save
output_path = (
    project_folder / "solar_irradiance_with_facilities.png"
)

plt.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

print("Map saved to:", output_path, flush=True)

plt.show()

