#!/usr/bin/env bash
# Gabung video + muzik, normalisasi bunyi (-14 LUFS), hasilkan versi TikTok & WhatsApp, kulit, dan helaian QC.
# Guna: finish.sh <folder_kerja> <folder_output> <nama_asas>   (jalankan selepas render.js full + music.py)
set -euo pipefail
W="$1"; OUT="$2"; NAME="$3"; mkdir -p "$OUT" "$W/qc"
cd "$W"
ffmpeg -y -loglevel error -i video_noaudio.mp4 -i music.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart final.mp4
# TikTok: kualiti tinggi (~100MB untuk 2.5 min)
ffmpeg -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -crf 21 -maxrate 10M -bufsize 20M \
  -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT/${NAME}_TikTok.mp4"
# WhatsApp: 2 laluan ~2.3Mbps (~50MB)
ffmpeg -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v 2300k -pass 1 -an -f null /dev/null
ffmpeg -y -loglevel error -i final.mp4 -c:v libx264 -preset slow -b:v 2300k -pass 2 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart "$OUT/${NAME}_WhatsApp.mp4"
# Kulit TikTok (bingkai tajuk)
ffmpeg -y -loglevel error -ss 4.9 -i final.mp4 -frames:v 1 -q:v 2 "$OUT/kulit_tiktok.jpg"
# Helaian QC: 12 bingkai sepanjang video
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4)
for k in $(seq 0 11); do t=$(python3 -c "print(round($D*($k+.5)/12,2))")
  ffmpeg -y -loglevel error -ss "$t" -i final.mp4 -frames:v 1 -vf scale=270:480 "qc/f$(printf %02d $k).jpg"; done
montage qc/f*.jpg -tile 6x2 -geometry +4+4 -background '#222' qc_sheet.jpg
ffmpeg -hide_banner -i final.mp4 -af ebur128=framelog=quiet -f null - 2>&1 | grep -E " I:" | head -1
ls -la "$OUT"
