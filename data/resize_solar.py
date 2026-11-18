
import rasterio
from rasterio.windows import from_bounds, Window
from rasterio.warp import transform_bounds
from rasterio.enums import Resampling

input_file = (
    "data/World_GHI_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF/"
    "GHI.tif"
)

output_file = "data/solar_ghi_small.tif"

# Approximate lower 48 geographic bounding box
bbox = (-125, 24, -66, 50)

with rasterio.open(input_file) as src:

    # Convert geographic bounds to source raster CRS
    bounds = transform_bounds(
        "EPSG:4326", src.crs, *bbox
    )

    # Select only the US portion
    window = from_bounds(
        *bounds,
        transform=src.transform
    )

    window = window.round_offsets().round_lengths()

    # Keep the window inside the source raster
    window = window.intersection(
        Window(0, 0, src.width, src.height)
    )

    # Resample to a manageable size
    width = max(1, round(window.width / 10))
    height = max(1, round(window.height / 10))

    data = src.read(
        1,
        window=window,
        out_shape=(height, width),
        resampling=Resampling.average,
        masked=True
    )

    # Update geographic transformation
    transform = src.window_transform(window) * (
        rasterio.Affine.scale(
            window.width / width,
            window.height / height
        )
    )

    # Preserve mask using a designated NoData value
    nodata = -9999.0

    profile = src.profile.copy()
    profile.update(
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype="float32",
        transform=transform,
        nodata=nodata,
        compress="deflate",
        tiled=True
    )

    with rasterio.open(output_file, "w", **profile) as dst:
        dst.write(data.filled(nodata).astype("float32"), 1)

print("Smaller solar raster saved:", output_file)

