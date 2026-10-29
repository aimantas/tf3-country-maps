"""Build the public-safe Mod Hub package for a country map. Usage: release_country.py <id>"""
import json, os, re, shutil, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'configs' / f'{sys.argv[1]}.json').read_text())
OUTD = ROOT / 'output' / CFG['id']; ART = ROOT / 'art' / CFG['id']
MOD = ROOT / 'release' / CFG['mod_id']
# Private identity markers live outside the repo: point TF3_MARKERS at a file with one regex per line.
_extra = [l.strip() for l in Path(os.environ['TF3_MARKERS']).read_text().splitlines() if l.strip() and not l.startswith('#')] if os.environ.get('TF3_MARKERS') else []
BLOCKED = re.compile('|'.join(['/Users/'] + _extra), re.I)
shutil.rmtree(MOD, ignore_errors=True); (MOD / '_metadata').mkdir(parents=True)
(MOD / 'mod.json').write_text(json.dumps({'modId': CFG['mod_id'], 'revision': 1, 'severityAdd': 'None', 'severityRemove': 'None', 'visible': True, 'cosmetic': True}, indent=2) + '\n')
desc = (f"Build a transport company across {CFG['english']}.\n\n"
        f"The whole country as a playable island: real terrain, {CFG['rivers_text']}, {CFG['towns']} towns where they really are and sized by population, and a set of starter industries.\n\n"
        "Import the heightmap and towns into a new Map Editor map. The steps are in the README.\n\n"
        "How maps like this are made: https://aimantas.com/writing/lithuania-transport-fever-3-map/\n\n"
        "Made by Aimantas. More at aimantas.com.\n\n"
        "Map data (c) OpenStreetMap contributors (ODbL). Terrain from Mapzen Terrain Tiles, including EU-DEM (Copernicus). Full notices in ATTRIBUTION.md.")
info = {'name': CFG['name_in_game'], 'summary': CFG['summary'], 'description': desc, 'authors': [{'name': 'Aimantas', 'role': 'CREATOR'}], 'tags': ['Map'], 'url': 'https://aimantas.com/'}
assert len(info['name']) <= 32 and len(info['summary']) <= 100, (len(info['name']), len(info['summary']))
(MOD / '_metadata/modinfo.json').write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n')
for i, p in enumerate(sorted(ART.glob('[0-9]-*.png'))):
    im = Image.open(p).convert('RGB'); im.info.pop('icc_profile', None); assert im.size == (1920, 1080); im.save(MOD / '_metadata' / f'{i}.png')
kit = MOD / 'map-kit'
(kit / 'heightmaps').mkdir(parents=True); (kit / 'towns_industries').mkdir(parents=True)
shutil.copy(OUTD / f"{CFG['stem']}_4097_playable.png", kit / 'heightmaps')
for f in OUTD.glob(f"{CFG['stem']}_*towns*.lua"): shutil.copy(f, kit / 'towns_industries')
steps = f"""# {CFG['title']}: {CFG['english']} island map for Transport Fever 3

Install
1. Copy `map-kit/heightmaps/*` into the `heightmaps` folder and `map-kit/towns_industries/*` into the `towns_industries` folder of your Transport Fever 3 userdata folder (`Steam/userdata/<your id>/3493540/local`).
2. In the game: Map Editor, new map, Temperate, Very Large, 1:1. Pick the {CFG['names_set']} names if you like.
3. Import the heightmap `{CFG['stem']}_4097_playable.png` with minimum -12, maximum 180 and water level 0. Press Return after typing each number.
4. Import the towns `{CFG['stem']}_{CFG['towns']}_towns_starter_industries`. If a file called `request` is listed, don't pick it.
5. Connect your towns, save the map and start a game.

Made by Aimantas. More at aimantas.com.
"""
(MOD / 'README.md').write_text(steps)
(MOD / 'ATTRIBUTION.md').write_text("""# Data attribution

- Towns, populations and rivers: (c) OpenStreetMap contributors, Open Database Licence (ODbL) 1.0, https://www.openstreetmap.org/copyright
- Terrain: Mapzen Terrain Tiles via AWS Open Data. Europe terrain data produced using Copernicus data and information funded by the European Union (EU-DEM); SRTM courtesy of the U.S. Geological Survey; ETOPO1 courtesy of NOAA.
- Country outline, rivers and lakes: Natural Earth, public domain.
- The Transport Fever 3 logo on the listing cover is (c) Urban Games. No game files are included.
- Original work (scaling, industry layout, scripts): CC BY 4.0, credit "Aimantas".
""")
bad = [f'{p.relative_to(MOD)}: {m.group(0)}' for p in MOD.rglob('*') if p.is_file() and p.suffix in {'.json', '.lua', '.md'} for m in BLOCKED.finditer(p.read_text(errors='ignore'))]
assert not bad, bad
print('release ok', MOD, [p.name for p in sorted((MOD / '_metadata').iterdir())])
