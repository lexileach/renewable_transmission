
from pathlib import Path
import rasterio
from rasterio.enums import Resampling
import numpy as np
import matplotlib.pyplot as plt

# 1. Locate the cropped solar raster
project_folder = Path(__file__).resolve().parent
raster_path = project_folder / "data" / "solar_ghi_lower48.tif"

# 2. Open the raster
with rasterio.open(raster_path) as src:

    print("Opening solar raster...", flush=True)

    # Read at reduced resolution to save memory
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

    print("Raster loaded successfully!", flush=True)
    print("GHI minimum:", float(ghi.min()))
    print("GHI maximum:", float(ghi.max()))

# 3. Convert masked pixels to NaN
ghi = ghi.astype("float32").filled(np.nan)

# 4. Create the figure
fig, ax = plt.subplots(figsize=(14, 8))

image = ax.imshow(
    ghi,
    extent=[
        bounds.left,
        bounds.right,
        bounds.bottom,
        bounds.top
    ],
    origin="upper",
    cmap="inferno",
    interpolation="nearest"
)

# 5. Add a legend
colorbar = plt.colorbar(image, ax=ax, shrink=0.75)
colorbar.set_label("Global Horizontal Irradiation (kWh/m²/day)")

# 6. Format the map
ax.set_title(
    "Solar Irradiance Across the Contiguous United States",
    fontsize=16
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.set_xlim(-125, -66)
ax.set_ylim(24, 50)

plt.tight_layout()

# 7. Save the map
output_path = project_folder / "solar_irradiance_map.png"

plt.savefig(output_path, dpi=200, bbox_inches="tight")

print("Map saved to:", output_path, flush=True)

# 8. Display the map
plt.show()
