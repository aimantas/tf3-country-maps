# Transport Fever 3 country maps

Countries as playable Transport Fever 3 islands: real terrain, real rivers, real towns sized by population, and starter industries. Made by Aimantas. More at aimantas.com.

| Map | Mod Hub |
| --- | --- |
| Lithuania | https://mod.io/g/transportfever3/m/lietuva-lithuania-island-map (source: https://github.com/aimantas/tf3-lithuania-map) |
| Germany | https://mod.io/g/transportfever3/m/deutschland-germany-island-map |
| Switzerland | https://mod.io/g/transportfever3/m/schweiz-switzerland-island-map |
| Austria | https://mod.io/g/transportfever3/m/sterreich-austria-island-map |
| Hungary | https://mod.io/g/transportfever3/m/magyarorszg-hungary-island-map |
| Netherlands | https://mod.io/g/transportfever3/m/nederland-netherlands-map |

How the maps are made: https://aimantas.com/writing/lithuania-transport-fever-3-map/

## Layout

- `configs/<country>.json`: one config per country (outline code, map square, town count, relief scale, rivers).
- `scripts/build_country.py <id>`: builds the heightmap and the town and industry presets.
- `scripts/validate_country.py <id>`, `preview_country.py <id>`, `make_country_art.py <id>`, `release_country.py <id>`.
- `data/`: Natural Earth outline, rivers and lakes, plus OpenStreetMap place snapshots in `data/osm/`. Elevation tiles are fetched on demand.
- `output/<id>/`: the built kit. `release/<mod id>/`: the exact package uploaded to the Mod Hub.

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_country.py germany
.venv/bin/python scripts/validate_country.py germany
```

## Licence and data

Original work: CC BY 4.0, credit "Aimantas". Map data derived from OpenStreetMap stays under the ODbL: (c) OpenStreetMap contributors. Terrain: Mapzen Terrain Tiles, including EU-DEM (Copernicus data funded by the European Union), SRTM (USGS) and ETOPO1 (NOAA). Natural Earth is public domain. No Transport Fever 3 game files are included.
