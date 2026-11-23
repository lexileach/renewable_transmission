
from pathlib import Path
import rasterio
from rasterio.windows import from_bounds, Window

# 1. Define file paths
project_folder = Path(__file__).resolve().parent

input_file = (
    project_folder
    / "data"
    / "World_GHI_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF"
    / "GHI.tif"
)

output_file = project_folder / "data" / "solar_ghi_lower48.tif"

# 2. Define geographic boundaries
west = -125
south = 24
east = -66
north = 50

# 3. Open the original raster
with rasterio.open(input_file) as src:

    print("Original CRS:", src.crs, flush=True)

    if src.crs is None or src.crs.to_epsg() != 4326:
        raise ValueError(
            "Expected EPSG:4326. Check the original raster CRS."
        )

    # 4. Select the Lower 48 region
    window = from_bounds(
        west, south, east, north,
        transform=src.transform
    )

    # Round to whole pixels and stay inside raster bounds
    col_start = max(0, int(window.col_off))
    row_start = max(0, int(window.row_off))
    col_end = min(src.width, int(window.col_off + window.width + 1))
    row_end = min(src.height, int(window.row_off + window.height + 1))

    window = Window(
        col_start,
        row_start,
        col_end - col_start,
        row_end - row_start
    )

    print("Crop width:", window.width, flush=True)
    print("Crop height:", window.height, flush=True)

    # 5. Update metadata for the smaller raster
    profile = src.profile.copy()
    profile.update(
        driver="GTiff",
        height=int(window.height),
        width=int(window.width),
        transform=src.window_transform(window),
        compress="lzw",
        tiled=True
    )

    # 6. Save the smaller raster in manageable chunks
    with rasterio.open(output_file, "w", **profile) as dst:

        chunk_size = 1024

        for row in range(0, int(window.height), chunk_size):
            for col in range(0, int(window.width), chunk_size):

                chunk = Window(
                    col,
                    row,
                    min(chunk_size, window.width - col),
                    min(chunk_size, window.height - row)
                )

                source_chunk = Window(
                    window.col_off + chunk.col_off,
                    window.row_off + chunk.row_off,
                    chunk.width,
                    chunk.height
                )

                data = src.read(window=source_chunk)

                dst.write(data, window=chunk)

            print(
                f"Processed {min(row + chunk_size, int(window.height))}"
                f" of {int(window.height)} rows",
                flush=True
            )

print("Cropping complete!", flush=True)
print("Saved to:", output_file, flush=True)
