#!/bin/zsh
# Fetch place=city/town nodes with population tags per country from Overpass, retrying on busy servers.
UA="aimantas-tf3-country-maps/1.0 (https://aimantas.com)"
cd "${0:A:h}"
for iso in "$@"; do
  [ -s $iso.json ] && head -c 1 $iso.json | grep -q '{' && continue
  q="[out:json][timeout:120];area[\"ISO3166-1\"=\"$iso\"][admin_level=2]->.a;(node[\"place\"=\"city\"](area.a);node[\"place\"=\"town\"][\"population\"](area.a););out tags center;"
  for try in 1 2 3 4 5 6; do
    for ep in https://overpass-api.de/api/interpreter https://overpass.kumi.systems/api/interpreter https://overpass.private.coffee/api/interpreter; do
      curl -s -m 150 -A "$UA" --data-urlencode "data=$q" $ep -o $iso.json
      if head -c 1 $iso.json | grep -q '{'; then echo "$iso ok via $ep"; break 2; fi
    done
    sleep $((try*15))
  done
done
