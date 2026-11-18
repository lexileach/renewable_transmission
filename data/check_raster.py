import rasterio

with rasterio.open("data/solar_ghi_small.tif") as src:
    print("Width:", src.width)
    print("Height:", src.height)
    print("CRS:", src.crs)
    print("Bounds:", src.bounds)