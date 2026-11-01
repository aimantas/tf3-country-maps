# Delivery record

## Germany, 2026-10-31
- Mod: https://mod.io/g/transportfever3/m/deutschland-germany-island-map (mod ID 6493516), uploaded from the game's Mod Hub on 31 Oct 2026 under the mod.io account "aimantas", Set Public ticked. Admin page shows status Live, 5 platforms live. Revision 1, 9.52 MB, 5 images, tag Map.
- Verified before upload (live game, 29 Oct): 60 of 60 towns with matching capacities, positions and cargo needs; 35 of 36 industries (one farm refused by the game, dropped from the preset); heights within 0.02 m; loads in gameplay mode.
- Release build: aimantas_deutschland_island, no eim_ IDs, no .sav, identity scan passed.
- Signed-out check: confirmed 1 Nov 2026 (public page shows real title, 144 downloads). Earlier: not confirmed. Server-rendered metadata still showed the generic mod.io title about 10 minutes after upload (a new page needs time to index; Lithuania's page shows its real title). Logged-in view shows the page live.
- Source: https://github.com/aimantas/tf3-country-maps

## Switzerland, Austria, Hungary, Netherlands, 2026-11-01
Uploaded from the game's Mod Hub under the mod.io account "aimantas", Set Public ticked, validation showed warnings only. Revision 1 each. Signed-out check: all four appear in the public mod list.

| Map | mod.io ID | Page | Towns / industries | Height range (m) |
| --- | --- | --- | --- | --- |
| Schweiz: Switzerland Island Map | 6495723 | https://mod.io/g/transportfever3/m/schweiz-switzerland-island-map | 36 / 36 | -1 to 500 |
| Österreich: Austria Island Map | 6495724 | https://mod.io/g/transportfever3/m/sterreich-austria-island-map | 40 / 36 | -1 to 500 |
| Magyarország: Hungary Island Map | 6495720 | https://mod.io/g/transportfever3/m/magyarorszg-hungary-island-map | 40 / 36 | -1 to 220 |
| Nederland: Netherlands Map | 6495722 | https://mod.io/g/transportfever3/m/nederland-netherlands-map | 45 / 33 (one refused farm dropped) | -1 to 80 |

Verified in the live game before upload: town and industry counts as above, terrain read back equal to the heightmap. Release builds: no eim_ IDs, no .sav, identity scan passed. Heights were chosen with the owner (Alps about 500 m in the game, Netherlands flat).

## Ready-to-play savegames, 2026-11-01

Built in the game with every mod disabled (Disable All Mods in the new-map Mods tab; the AI MCP Bridge and the pre-order pack were off), then saved as maps and shared with the game's own Share button. Each saved map lists 0 mods; the decompressed .sav has no bridge, eim_ or pre-order references. Tag: Savegame. Public.

| Map | mod.io ID | Page |
|---|---|---|
| Deutschland | 6496424 | deutschland-ready-to-play |
| Schweiz | 6496437 | schweiz-ready-to-play |
| Osterreich | 6496455 | osterreich-ready-to-play |
| Magyarorszag | 6496465 | magyarorszag-ready-to-play |
| Nederland | 6496475 | nederland-ready-to-play |
| Lietuva | 6496481 | lietuva-ready-to-play |

Pages are at https://mod.io/g/transportfever3/m/<page>. Each save page links its map kit and both articles; each map kit page links its save. Covers: `scripts/make_listing_v2.py <id> save` (Lithuania cover drawn with PIL on the older circle cover).

Limits: all six start 1900, Temperate, Very Large. Names: German for Germany, Switzerland and Austria; Dutch for the Netherlands; European for Hungary and Lithuania. The saves still embed the Steam account id and the default company name, as every Transport Fever 3 save does. Deutschland_start (6496402, an earlier test made with the bridge enabled) lists the AI MCP Bridge in its mod list and is not one of these.
