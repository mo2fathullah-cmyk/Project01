#!/usr/bin/env bash
# One command to voice, score, mix and render an episode.
#   shared/produce.sh <episode_dir> <voice> [accent: none|my] [output_suffix]
# Voices (Kokoro): female  af_heart (young, warm) | af_bella | bf_emma (British)
#                  male    am_michael | am_fenrir | bm_lewis (British)
# Needs <episode_dir>/audio/lines.json and audio/cues_base.json ({"base": <seconds>, "lift", "break", "riser", "drop"}).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
EP=$1; VOICE=$2; ACCENT=${3:-none}; SUF=${4:-$VOICE}
KDIR=${KOKORO_DIR:-$HOME/.cache/kokoro}
if [ ! -f "$KDIR/kokoro-v1.0.onnx" ]; then
  mkdir -p "$KDIR"
  for f in kokoro-v1.0.onnx voices-v1.0.bin; do
    curl -sSL -o "$KDIR/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
  done
fi
CLIPS=$(mktemp -d)
BASE=$(python3 -c "import json;print(json.load(open('$EP/audio/cues_base.json'))['base'])")
python3 "$HERE/tts.py" "$EP/audio/lines.json" "$CLIPS" "$KDIR" "$VOICE" 1.0 "$ACCENT" 2>&1 | grep -v -i warn
python3 "$HERE/build_vo.py" "$EP/audio/lines.json" "$CLIPS" "$BASE" "$EP/timing.js" "$EP/audio/voice.wav" \
  "$EP/audio/cues_base.json" "$EP/audio/cues.json" | tail -1
DUR=$(python3 -c "import json;print(json.load(open('$EP/audio/cues.json'))['duration'])")
python3 "$HERE/music.py" "$EP/audio/music.wav" "$DUR" "$EP/audio/cues.json"
ffmpeg -loglevel error -y -i "$EP/audio/voice.wav" -i "$EP/audio/music.wav" -filter_complex "
[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=90,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,asplit=2[v][key];
[1:a]volume=0.58[m];
[m][key]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=400:makeup=1[md];
[v][md]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=11:linear=true[out]" \
  -map "[out]" -ar 48000 "$EP/audio/mix.wav"
NAME=$(basename "$EP")
node "$HERE/render.js" "$EP/index.html" video "$EP/${NAME}_${SUF}.mp4" 4 "$EP/audio/mix.wav" | tail -1
rm -rf "$CLIPS"
