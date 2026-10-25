#!/usr/bin/env python3
"""Build v2 of "Tiny Babies Broke Everything!" (9:16, HD sound).

Video: each segment is cut/zoomed/reversed with ffmpeg and gets its hook text burned in.
Audio: cleaned clip audio + narrator + original music (ducked under voices) + sound effects,
mixed in numpy at 48 kHz and mastered to -14 LUFS, AAC 320 kb/s.

Usage: python3 scripts/build_v2.py   (needs ffmpeg + numpy)
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import music  # noqa: E402

SR = music.SR
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLIPS = os.path.join(ROOT, "clips")
KEYS = os.path.join(ROOT, "keyframes")
NARR = os.path.join(ROOT, "audio", "narrator")
OUT = os.path.join(ROOT, "output", "tiny_babies_broke_everything_v2_HD.mp4")
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FPS = 30
W, H = 1080, 1920

# Narrator files: (file, seconds of leading silence to trim)
N = {k: (f"n{k:02d}.wav", t) for k, t in
     {1: .45, 2: .2, 3: .28, 4: .4, 5: .45, 6: .45, 7: .45, 8: .45, 9: .45, 10: .35}.items()}

# Text styles
HOOK = dict(size=82, color="#FFE14D", border="#E5337A", bw=9)
CAP = dict(size=62, color="white", border="black@0.85", bw=7)
TAG = dict(size=64, color="white", border="#E5337A", bw=8)

# Each segment:
#   src: clip file or still image; ss/dur: cut; mode: normal|reverse|still|freeze_end
#   zoom: punch-in amount over the segment; texts: (text, style, y, t_from, t_to, x)
#   vo: narrator (key, at, tempo); sfx: (name, at); mood: music mood or None; clip_gain
SEGMENTS = [
    dict(name="cold_open", src="scene4.mp4", ss=0, dur=3.8, zoom=0.18, clip_gain=0.0, mood="sneaky",
         vo=[(1, 0.0, 1.0)], sfx=[("scratch", 3.45)],
         texts=[("WHO BROKE IT?!", HOOK, 200, 0, 99)]),
    dict(name="rewind", src="scene1.mp4", ss=0, dur=6.0, mode="reverse", speed=2.6, clip_gain=0.0, mood=None,
         vo=[(2, 0.0, 1.0)], sfx=[("whoosh", 0.0), ("whoosh_up", 1.4)], vhs=True,
         texts=[("<< REWIND <<", HOOK, 200, 0, 99)]),
    dict(name="intro", src="scene1.jpg", mode="still", dur=5.8, zoom=0.12, clip_gain=0.0, mood="happy",
         vo=[(3, 0.1, 1.15)], sfx=[("pop", 1.2), ("pop", 2.7)],
         texts=[("MEET THE TINY BABIES!", HOOK, 200, 0, 99),
                ("PINKU", TAG, 1180, 1.2, 99, 120), ("GOLDY", TAG, 1180, 2.7, 99, 640)]),
    dict(name="ball", src="scene1.mp4", dur=6.04, mood="happy", vo=[(4, 0.0, 1.0)],
         texts=[("1, 2, 3... KICK!", HOOK, 200, 0, 3.2), ("CRASH! The vase!", CAP, H - 430, 4.6, 99)]),
    dict(name="pillows", src="scene2.mp4", dur=6.04, mood="happy", vo=[(5, 0.15, 1.0)],
         texts=[("PILLOW FIGHT!", HOOK, 200, 0, 3.2), ("Boing! Boing! Oops!", CAP, H - 430, 3.4, 99)]),
    dict(name="crayons", src="scene_crayons.mp4", dur=6.04, mood="happy", vo=[(6, 0.15, 1.12)],
         texts=[("CRAYON ART TIME!", HOOK, 200, 0, 3.0), ("Not on the wall!", CAP, H - 430, 3.6, 99)]),
    dict(name="cups", src="scene3.mp4", dur=6.04, mood="happy", vo=[(7, 0.0, 1.1)],
         texts=[("WILL IT FALL?", HOOK, 200, 0, 3.4), ("CRASH! Oops!", CAP, H - 430, 4.0, 99)]),
    dict(name="mama_tease", src="scene4.jpg", mode="still", dur=2.8, zoom=0.15, clip_gain=0.0, mood="sneaky",
         vo=[(8, 0.0, 1.0)], sfx=[("whoosh_up", 0.0)],
         texts=[("HERE COMES MAMA!", HOOK, 200, 0, 99)]),
    dict(name="mama", src="scene4.mp4", dur=5.04, mood="sneaky", music_gain=0.45,
         texts=[("MAMA IS HERE!", HOOK, 200, 0, 3.0), ("Babies! What did you do?!", CAP, H - 430, 0.9, 99)]),
    dict(name="ears", src="scene_ears.mp4", dur=5.04, mood="sneaky", music_gain=0.4,
         texts=[("MAMA IS ANGRY!", HOOK, 200, 0, 3.0), ("You are very bad babies!", CAP, H - 430, 0.6, 99)]),
    dict(name="sorry", src="scene5.mp4", ss=3.0, dur=4.0, mood="sweet", music_gain=0.45,
         texts=[("Sorry, Mama...", CAP, H - 430, 0.8, 99)]),
    dict(name="hug", src="scene6.mp4", dur=6.04, mood="sweet", music_gain=0.45,
         texts=[("I love you, babies!", CAP, H - 430, 0.2, 4.6), ("Okay, Mama!", CAP, H - 430, 4.7, 99)]),
    dict(name="end_card", src="scene6.jpg", mode="still", dur=11.4, zoom=0.1, clip_gain=0.0, mood="sweet",
         vo=[(9, 0.2, 1.05), (10, 5.0, 1.15)], sfx=[("ding", 4.8)],
         texts=[("ALWAYS SAY SORRY!", HOOK, 200, 0, 4.8),
                ("WHO WAS NAUGHTY?", HOOK, 200, 4.8, 99),
                ("PINKU or GOLDY?", HOOK, 300, 5.6, 99),
                ("Comment below & Subscribe!", CAP, H - 430, 7.0, 99)]),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def esc_path(p):
    return p.replace(":", r"\:")


def text_filters(seg, tmp):
    out = []
    for i, t in enumerate(seg.get("texts", [])):
        text, st, y, t0, t1 = t[:5]
        x = f"{t[5]}" if len(t) > 5 else "(w-tw)/2"
        tf = os.path.join(tmp, f"{seg['name']}_{i}.txt")
        with open(tf, "w") as f:
            f.write(text)
        alpha = f"if(lt(t,{t0}+0.15),(t-{t0})/0.15,1)"
        out.append(
            f"drawtext=fontfile={FONT}:textfile={esc_path(tf)}:fontsize={st['size']}:fontcolor={st['color']}:"
            f"borderw={st['bw']}:bordercolor={st['border']}:x={x}:y={y}:alpha='{alpha}':"
            f"enable='between(t,{t0},{t1})'")
    return out


def zoom_filter(z, dur):
    if not z:
        return []
    frames = int(dur * FPS)
    return [f"scale={W * 2}:{H * 2}",
            f"zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}"]


def render_video(seg, tmp):
    out = os.path.join(tmp, f"{seg['name']}.mp4")
    dur = seg["dur"]
    mode = seg.get("mode", "normal")
    base = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}", "setsar=1", f"fps={FPS}"]
    if mode == "still":
        inp = ["-loop", "1", "-t", str(dur), "-i", os.path.join(KEYS, seg["src"])]
        chain = base
    elif mode == "freeze_end":
        inp = ["-sseof", "-0.1", "-i", os.path.join(CLIPS, seg["src"])]
        chain = base + [f"tpad=stop_mode=clone:stop_duration={dur}"]
    elif mode == "reverse":
        inp = ["-ss", str(seg.get("ss", 0)), "-t", str(dur), "-i", os.path.join(CLIPS, seg["src"])]
        chain = base + ["reverse", f"setpts=PTS/{seg['speed']}"]
        dur = dur / seg["speed"]
        seg["dur"] = dur
    else:
        inp = ["-ss", str(seg.get("ss", 0)), "-i", os.path.join(CLIPS, seg["src"])]
        chain = base
    chain += zoom_filter(seg.get("zoom"), dur)
    if seg.get("vhs"):
        chain += ["eq=saturation=0.6:contrast=1.15", "noise=alls=25:allf=t",
                  "drawbox=y='mod(t*1600,ih)':h=18:w=iw:color=white@0.25:t=fill"]
    chain += text_filters(seg, tmp)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inp, "-t", f"{dur:.3f}",
         "-vf", ",".join(chain), "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "9M", "-bufsize", "18M",
         "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    return out


def load_audio(path, ss=0.0, dur=None, filt=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path]
    if filt:
        cmd += ["-af", filt]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def fit(a, n):
    if len(a) >= n:
        return a[:n]
    return np.vstack([a, np.zeros((n - len(a), 2))])


# Light clean-up for the generated clip audio: remove rumble, soften hiss, add presence.
CLIP_CLEAN = "highpass=f=70,afftdn=nf=-32,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=1.5"
# Narrator: same clean-up plus a little compression so every word is clear.
NARR_CLEAN = "highpass=f=90,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=80"

SFX = {"scratch": music.sfx_scratch, "whoosh": music.sfx_whoosh, "pop": music.sfx_pop, "ding": music.sfx_ding,
       "whoosh_up": lambda: music.sfx_whoosh(0.9, rising=True)}


def envelope(x, win=0.08):
    mono = np.abs(x).mean(1)
    k = int(win * SR)
    c = np.cumsum(np.concatenate([[0], mono]))
    env = (c[k:] - c[:-k]) / k
    return np.concatenate([env, np.full(k - 1, env[-1])])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        vids = []
        for seg in SEGMENTS:
            print("video:", seg["name"])
            vids.append(render_video(seg, tmp))

        total = sum(s["dur"] for s in SEGMENTS)
        n = int(total * SR) + SR
        clip_bus, vo_bus, sfx_bus = (np.zeros((n, 2)) for _ in range(3))
        mood_gain = {m: np.zeros(n) for m in ("happy", "sneaky", "sweet")}

        t = 0.0
        for seg in SEGMENTS:
            i0, ns = int(t * SR), int(seg["dur"] * SR)
            g = seg.get("clip_gain", 1.0)
            if g and seg.get("mode", "normal") == "normal":
                a = load_audio(os.path.join(CLIPS, seg["src"]), seg.get("ss", 0), seg["dur"], CLIP_CLEAN)
                clip_bus[i0:i0 + ns] += fit(a, ns) * g
            for key, at, tempo in seg.get("vo", []):
                f, trim = N[key]
                filt = NARR_CLEAN + (f",atempo={tempo}" if tempo != 1.0 else "")
                a = load_audio(os.path.join(NARR, f), trim, None, filt)
                j = i0 + int(at * SR)
                vo_bus[j:j + len(a)] += a[: n - j] * 1.1
            for name, at in seg.get("sfx", []):
                a = SFX[name]()
                j = i0 + int(at * SR)
                sfx_bus[j:j + len(a)] += a[: n - j]
            if seg.get("mood"):
                fade = int(0.12 * SR)
                ramp = np.ones(ns)
                ramp[:fade] = np.linspace(0, 1, fade)
                ramp[-fade:] = np.minimum(ramp[-fade:], np.linspace(1, 0, fade))
                mood_gain[seg["mood"]][i0:i0 + ns] += ramp * seg.get("music_gain", 1.0)
            t += seg["dur"]

        print("music...")
        music_bus = np.zeros((n, 2))
        for m, gain in mood_gain.items():
            if gain.any():
                music_bus += music.render(m, n / SR, seed=hash(m) % 100)[:n] * gain[:, None]

        # duck music under any voice (narrator or characters)
        voice_env = envelope(vo_bus + clip_bus)
        duck = 1 - 0.65 * np.clip(voice_env / 0.04, 0, 1)
        smooth = int(0.15 * SR)
        duck = np.convolve(duck, np.ones(smooth) / smooth, mode="same")
        mix = clip_bus * 1.0 + vo_bus + sfx_bus * 0.5 + music_bus * 0.32 * duck[:, None]
        mix = mix[: int(total * SR)]
        mix /= np.abs(mix).max() + 1e-9
        mix *= 0.9

        wav = os.path.join(tmp, "mix.f32")
        mix.astype(np.float32).tofile(wav)
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{v}'\n" for v in vids)
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        # two-pass loudness normalisation to -14 LUFS / -1 dBTP
        probe = subprocess.run(["ffmpeg", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", wav,
                                "-af", "loudnorm=I=-14:TP=-1.0:LRA=9:print_format=json", "-f", "null", "-"],
                               capture_output=True, text=True, check=True).stderr
        m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
        loudnorm = (f"loudnorm=I=-14:TP=-1.0:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                    f"offset={m['target_offset']}:linear=true,aresample=48000")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "concat", "-safe", "0", "-i", lst,
             "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", wav,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-af", loudnorm,
             "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", OUT])
        print("Wrote", OUT, f"({total:.1f}s)")


if __name__ == "__main__":
    main()
