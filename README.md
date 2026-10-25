# Jelly Wiggles Kids

Short vertical (9:16) cartoon videos for small kids.

## Main characters

| Character | Look | Reference |
|---|---|---|
| **Pinku** | Tiny pale-pink fluffy baby, smooth cream round face, two little black dot eyes, rosy cheeks, small smile | `characters/pinku_reference.jpg` |
| **Goldy** | Tiny round golden-beige fluffy baby, big brown eyes, small folded ears, pink nose, chubby belly | `characters/goldy_reference.jpg` |
| **Mama** | Big soft fluffy cream mother, kind face, light-blue apron with a heart pocket | `characters/mama_design.png` |

Both babies are always shown **very small** (teacup size) next to normal furniture.

## Episode 1 — "Tiny Babies Broke Everything!" (9:16, ~36s)

| # | Scene | Hook / caption | Dialogue |
|---|---|---|---|
| 1 | Pinku & Goldy kick a red ball, it hits the table and the blue vase crashes | **UH-OH!! WATCH TILL THE END** | "Uh-oh!" |
| 2 | Pillow fight on the sofa, feathers explode, picture frame falls | **PILLOW FIGHT TIME!** | giggles |
| 3 | They build a cup & plate tower in the kitchen, it topples and breaks | **THE CUP TOWER...** | "Oops!" |
| 4 | Mama walks in, sees the mess, babies freeze | **MAMA IS HERE!** | Mama: "Babies! What did you do?!" |
| 5 | Mama picks both up to her ears and scolds them | **MAMA IS ANGRY!** | Mama: "You are very bad babies!" — Babies: "Sorry, Mama..." |
| 6 | Babies kiss Mama, big hug, hearts | **ALWAYS SAY SORRY** + Like & Subscribe | Mama: "I love you! But no more breaking things, okay?" — "Okay, Mama!" |

Lesson for kids: play gently, and say sorry when you make a mistake.

## Episode 1 v2 — HD sound + more fun (9:16, ~70s)

`output/tiny_babies_broke_everything_v2_HD.mp4` — built by `scripts/build_v2.py`.

What's new:
- **Cold-open hook**: Mama's shocked face + "Uh-oh! Who broke Mama's vase?!" then a record scratch
- **Rewind effect**: VHS-style rewind with whoosh sounds and "Let's rewind and find out!"
- **Character intro** with pop-up name tags: "Meet Pinku... and Goldy!"
- **Narrator** for small kids: counting "1, 2, 3... KICK!", "Pillow fight! Boing, boing!", "Will it fall?"
- **New scene**: crayon drawings on the wall
- **New ear scene**: Mama lifts both babies up by their ears — "You are very bad babies!"
- **Lesson + interactive ending**: "Always say sorry!", "Who was the naughty one? Pinku or Goldy? Tell us in the comments!"

HD sound:
- 48 kHz stereo, AAC 320 kb/s, two-pass loudness to -14 LUFS (YouTube/TikTok standard), peaks below -1 dBTP
- Clip audio cleaned (rumble high-pass, light de-noise, presence EQ); narrator compressed for clear words
- Original music (`scripts/music.py`): happy ukulele + glockenspiel for play, sneaky pizzicato when Mama
  arrives, sweet lullaby for the hug — automatically ducked under every voice
- Sound effects: record scratch, rewind whooshes, name-tag pops, ending ding

## Files

- `keyframes/scene1-6.jpg` — still frame each scene was animated from
- `clips/scene1-6.mp4` — raw animated clips with sound
- `output/tiny_babies_broke_everything_9x16.mp4` — final video with hooks and captions
- `scripts/assemble.sh` — rebuilds the v1 video from `clips/` (needs ffmpeg)
- `scripts/build_v2.py` + `scripts/music.py` — rebuild v2 with the full HD audio mix (needs ffmpeg + numpy)
- `audio/narrator/` — narrator voice lines (48 kHz WAV)
