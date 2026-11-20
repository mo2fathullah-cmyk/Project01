#!/usr/bin/env bash
# Sedia aset untuk enjin video: gred gambar, latar kabur, logo bulat, font tempatan.
# Guna: prep_assets.sh <folder_gambar_asal> <fail_logo> <folder_kerja>
set -euo pipefail
SRC="$1"; LOGO="$2"; WORK="$3"
mkdir -p "$WORK/ph" "$WORK/bg" "$WORK/fonts"

# 1) Gambar: saiz maks 1800px, gred "kamera filem" ringan (saturasi +16%, kontras sigmoid, tajam halus)
#    Latar: crop 9:16, kabur tebal, digelapkan (dipakai di belakang kad gambar)
find "$SRC" -maxdepth 1 -iname '*.jpg' -print0 | xargs -0 -P4 -I{} sh -c '
  f="{}"; n=$(basename "$f")
  convert "$f" -auto-orient -resize "1800x1800>" -modulate 103,116 -sigmoidal-contrast 2.5x50% -unsharp 0x0.9+0.6 -quality 92 "'"$WORK"'/ph/$n"
  convert "$f" -auto-orient -resize 540x960^ -gravity center -extent 540x960 -blur 0x22 -modulate 60,120 -quality 85 "'"$WORK"'/bg/$n"'

# 2) Logo: besarkan 3x (Lanczos + unsharp) dan potong bulat beralpha
convert "$LOGO" -filter Lanczos -resize 720x720 -unsharp 0x1.2+0.8 \
  \( -size 720x720 xc:black -fill white -draw "circle 360,360 360,4" -blur 0x1 \) \
  -alpha off -compose CopyOpacity -composite "$WORK/logo.png"

# 3) Font Google (Baloo 2, Nunito, Amiri) dimuat turun ke fail tempatan + local.css
cd "$WORK/fonts"
UA="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.30 (KHTML, like Gecko) Safari/534.30"
: > fonts.css
for fam in "Baloo+2:wght@600;800" "Nunito:wght@600;800;900" "Amiri:wght@700"; do
  curl -sS -A "$UA" "https://fonts.googleapis.com/css2?family=$fam" >> fonts.css
done
cp fonts.css local.css; i=0
for u in $(grep -oE "https://fonts.gstatic.com[^)]+" fonts.css | sort -u); do
  i=$((i+1)); curl -sS -o "f$i.woff" "$u"; sed -i "s#$u#f$i.woff#" local.css
done
echo "Siap: $(ls "$WORK/ph" | wc -l) gambar, logo.png, $i fail font"
