"""Create placeholder demo pointers for docs/testing."""
from pathlib import Path

root = Path("/data/demo")
root.mkdir(parents=True, exist_ok=True)
(root / "README.txt").write_text(
    "Place a sample DEM GeoTIFF and streams KML here for interactive local demo."
)
print("Demo folder prepared:", root)
