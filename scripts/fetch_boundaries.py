import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "geo" / "local_authorities.geojson"
LAYER = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "Local_Authority_Districts_May_2023_EW_BUC/FeatureServer/0/query"
)
CODE_ALIASES = {
    "E08000016": "E08000038",  # Barnsley
    "E08000019": "E08000039",  # Sheffield
}


def round_coordinates(coordinates):
    if isinstance(coordinates, list) and coordinates and isinstance(coordinates[0], (int, float)):
        return [round(value) for value in coordinates]
    return [round_coordinates(value) for value in coordinates]


def main():
    params = urlencode({
        "where": "1=1",
        "outFields": "LAD23CD,LAD23NM",
        "returnGeometry": "true",
        "outSR": "27700",
        "maxAllowableOffset": "250",
        "geometryPrecision": "0",
        "f": "geojson",
    })
    request = Request(f"{LAYER}?{params}", headers={"User-Agent": "housing-affordability-report/1.0"})
    with urlopen(request, timeout=60) as response:
        source = json.load(response)

    features = []
    for feature in source.get("features", []):
        properties = feature.get("properties", {})
        source_code = properties.get("LAD23CD")
        if not source_code:
            raise ValueError("Boundary response is missing LAD23CD.")
        features.append({
            "type": "Feature",
            "properties": {
                "code": CODE_ALIASES.get(source_code, source_code),
                "name": properties.get("LAD23NM", ""),
            },
            "geometry": {
                **feature["geometry"],
                "coordinates": round_coordinates(feature["geometry"]["coordinates"]),
            },
        })

    codes = [feature["properties"]["code"] for feature in features]
    if len(features) != 318 or len(set(codes)) != len(codes):
        raise ValueError(f"Expected 318 unique local-authority boundaries, received {len(features)}.")

    payload = {
        "type": "FeatureCollection",
        "name": "Local Authority Districts May 2023 England and Wales, ultra-generalised",
        "crs": {"type": "name", "properties": {"name": "EPSG:27700"}},
        "features": features,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(features)} boundaries to {OUTPUT} ({OUTPUT.stat().st_size:,} bytes).")


if __name__ == "__main__":
    main()