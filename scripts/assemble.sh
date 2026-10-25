#!/usr/bin/env bash
# Assemble the 9:16 kids short from clips/scene1..6.mp4 into output/.
# Each clip is normalised to 1080x1920 @30fps, gets its caption/hook text burned in,
# then all scenes are concatenated.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLIPS="$ROOT/clips"
OUT="$ROOT/output"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FONT="/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

# scene | top hook text (big, yellow; ^ starts a second line) | bottom caption (white)
SCENES=(
  "1|UH-OH!!^WATCH TILL THE END!|Tiny babies playing ball..."
  "2|PILLOW FIGHT TIME!|Boing! Boing! Oops!"
  "3|THE CUP TOWER...|Crash! Oh no!"
  "4|MAMA IS HERE!|Babies! What did you do?!"
  "5|MAMA IS ANGRY!|You are very bad babies!"
  "6|ALWAYS SAY SORRY|Like & Subscribe for more!"
)

: > "$TMP/list.txt"
for row in "${SCENES[@]}"; do
  IFS='|' read -r n top bottom <<< "$row"
  top2="${top#*^}"; [[ "$top2" == "$top" ]] && top2=""
  printf '%s' "${top%%^*}" > "$TMP/top$n.txt"
  printf '%s' "$top2" > "$TMP/topb$n.txt"
  printf '%s' "$bottom" > "$TMP/bot$n.txt"
  ffmpeg -hide_banner -loglevel error -y -i "$CLIPS/scene$n.mp4" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,\
drawtext=fontfile=$FONT:textfile=$TMP/top$n.txt:fontsize=78:fontcolor=#FFE14D:borderw=8:bordercolor=#E5337A:x=(w-tw)/2:y=170:enable='lt(t,3)',\
drawtext=fontfile=$FONT:textfile=$TMP/topb$n.txt:fontsize=78:fontcolor=#FFE14D:borderw=8:bordercolor=#E5337A:x=(w-tw)/2:y=270:enable='lt(t,3)',\
drawtext=fontfile=$FONT:textfile=$TMP/bot$n.txt:fontsize=60:fontcolor=white:borderw=6:bordercolor=black@0.85:x=(w-tw)/2:y=h-360" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100,aformat=channel_layouts=stereo" -c:a aac -b:a 192k \
    "$TMP/s$n.mp4"
  echo "file '$TMP/s$n.mp4'" >> "$TMP/list.txt"
done

mkdir -p "$OUT"
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -c copy -movflags +faststart \
  "$OUT/tiny_babies_broke_everything_9x16.mp4"
echo "Wrote $OUT/tiny_babies_broke_everything_9x16.mp4"
