from pathlib import Path


def validate_dem_file(filename: str, size_bytes: int, max_mb: int) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in {".tif", ".tiff"}:
        raise ValueError("DEM must be .tif or .tiff")
    if size_bytes > max_mb * 1024 * 1024:
        raise ValueError(f"DEM exceeds max size of {max_mb} MB")


def validate_streams_file(filename: str, size_bytes: int, max_mb: int) -> None:
    ext = Path(filename).suffix.lower()
    if ext != ".kml":
        raise ValueError("Streams must be .kml")
    if size_bytes > max_mb * 1024 * 1024:
        raise ValueError(f"KML exceeds max size of {max_mb} MB")
