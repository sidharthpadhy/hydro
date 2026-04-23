from pathlib import Path

import geopandas as gpd
import rasterio
from shapely.geometry import box


def inspect_dem(path: str) -> dict:
    with rasterio.open(path) as src:
        return {
            "crs": str(src.crs) if src.crs else None,
            "bounds": list(src.bounds),
            "resolution": [src.res[0], src.res[1]],
            "width": src.width,
            "height": src.height,
        }


def inspect_kml(path: str) -> dict:
    gdf = gpd.read_file(path, driver="KML")
    return {
        "crs": str(gdf.crs) if gdf.crs else None,
        "feature_count": int(len(gdf)),
        "bounds": list(gdf.total_bounds),
    }


def convert_kml_to_geojson(kml_path: str, output_dir: str) -> str:
    gdf = gpd.read_file(kml_path, driver="KML")
    out = Path(output_dir) / "streams.geojson"
    gdf.to_file(out, driver="GeoJSON")
    return str(out)


def ensure_overlap(dem_bounds: list[float], stream_bounds: list[float]) -> bool:
    dem_poly = box(*dem_bounds)
    stream_poly = box(*stream_bounds)
    return dem_poly.intersects(stream_poly)
