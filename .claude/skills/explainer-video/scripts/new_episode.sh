#!/usr/bin/env bash
# Scaffold a series folder and a new episode from the EP1 reference.
#   new_episode.sh <series_dir> <epNN>
# Creates <series_dir>/shared (engine + brand assets, once) and <series_dir>/<epNN>/{index.html,audio/lines.json,audio/cues_base.json}
set -euo pipefail
SK=$(cd "$(dirname "$0")/.." && pwd)
SER=$1; EP=$2
mkdir -p "$SER/shared" "$SER/$EP/audio"
for f in render.js tts.py build_vo.py music.py produce.sh; do cp -n "$SK/scripts/$f" "$SER/shared/"; done
for f in gsap.min.js logo-unimap.png three.min.js orbit.js; do cp -n "$SK/assets/$f" "$SER/shared/"; done
chmod +x "$SER/shared/produce.sh"
cp -n "$SK/templates/episode.html" "$SER/$EP/index.html"
cp -n "$SK/templates/lines.json" "$SER/$EP/audio/lines.json"
cp -n "$SK/templates/cues_base.json" "$SER/$EP/audio/cues_base.json"
echo "ready: $SER/$EP  (edit index.html scenes + CAPS, audio/lines.json, audio/cues_base.json)"
