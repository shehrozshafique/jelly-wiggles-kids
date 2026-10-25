"""Original kids background music, synthesised with numpy (48 kHz stereo).

Three moods share one tempo so they can be cut together:
  happy  - bouncy ukulele-style plucks, glockenspiel melody, bass, shaker, soft kick
  sneaky - staccato minor pizzicato bass and plucks (Mama arrives / scolding)
  sweet  - soft pads with a slow glockenspiel lullaby (hug and ending)
"""
import numpy as np

SR = 48000
BPM = 112
BEAT = 60.0 / BPM


def midi_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_exp(n, decay):
    t = np.arange(n) / SR
    e = np.exp(-t / decay)
    att = min(n, int(0.004 * SR))
    e[:att] *= np.linspace(0, 1, att)
    return e


def pluck(freq, dur, rng, bright=0.5):
    """Karplus-Strong plucked string."""
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, period)
    out = np.empty(n)
    for i in range(n):
        j = i % period
        out[i] = buf[j]
        buf[j] = 0.5 * (buf[j] + buf[(j + 1) % period]) * (0.994 + 0.005 * bright)
    return out * env_exp(n, dur * 0.6)


def glock(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / 0.08)
    s += 0.15 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t / 0.04)
    return s * env_exp(n, 0.45)


def bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    return s * env_exp(n, 0.25)


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t + k) + 0.2 * np.sin(2 * np.pi * f * 2.001 * t) for k, f in enumerate(freqs))
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return s / len(freqs) * np.clip(e, 0, 1)


def kick(dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t / 0.05) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)


def shaker(rng, dur=0.06):
    n = int(dur * SR)
    s = rng.uniform(-1, 1, n)
    s = s - np.concatenate([[0], s[:-1]])  # crude high-pass
    return s * env_exp(n, 0.02)


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


# chords as MIDI root + triad intervals
HAPPY = [(60, (0, 4, 7)), (67, (0, 4, 7)), (69, (0, 3, 7)), (65, (0, 4, 7))]   # C G Am F
SNEAKY = [(57, (0, 3, 7)), (57, (0, 3, 7)), (52, (0, 4, 7)), (57, (0, 3, 7))]  # Am Am E Am
SWEET = [(65, (0, 4, 7)), (60, (0, 4, 7)), (67, (0, 4, 7)), (60, (0, 4, 7))]   # F C G C

MELODY_STEPS = [[0, 2, 4, 2, 7, 4, 2, 0], [4, 4, 2, 0, 2, 4, 7, 4], [7, 4, 2, 4, 0, 2, 4, None], [2, 0, 2, 4, 2, 0, None, 0]]


def scale_note(root, step):
    major = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]
    return root + major[step] if step < len(major) else root + 12


def render(mood, seconds, seed=1):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR) + SR
    L = np.zeros(n)
    R = np.zeros(n)
    bar = BEAT * 4
    bars = int(np.ceil(seconds / bar)) + 1
    prog = {"happy": HAPPY, "sneaky": SNEAKY, "sweet": SWEET}[mood]
    for b in range(bars):
        root, tri = prog[b % 4]
        t0 = b * bar
        if mood == "happy":
            for k in range(8):  # ukulele arpeggio in eighths
                note = root + tri[[0, 1, 2, 1, 2, 1, 0, 1][k]]
                p = pluck(midi_hz(note), BEAT * 1.5, rng)
                add(L, p, t0 + k * BEAT / 2, 0.22)
                add(R, p, t0 + k * BEAT / 2 + 0.008, 0.18)
            mel = MELODY_STEPS[b % 4]
            for k, st in enumerate(mel):
                if st is None:
                    continue
                g = glock(midi_hz(scale_note(72, st)), BEAT)
                add(L, g, t0 + k * BEAT / 2, 0.16)
                add(R, g, t0 + k * BEAT / 2, 0.2)
            for k in range(4):
                bs = bass(midi_hz(root - 24 + (7 if k % 2 else 0)), BEAT)
                add(L, bs, t0 + k * BEAT, 0.35)
                add(R, bs, t0 + k * BEAT, 0.35)
            for k in (0, 2):
                add(L, kick(), t0 + k * BEAT, 0.35)
                add(R, kick(), t0 + k * BEAT, 0.35)
            for k in range(8):
                sh = shaker(rng)
                add(L, sh, t0 + k * BEAT / 2, 0.05 if k % 2 else 0.03)
                add(R, sh, t0 + k * BEAT / 2, 0.03 if k % 2 else 0.05)
        elif mood == "sneaky":
            for k in range(4):  # tiptoe staccato bass
                bs = bass(midi_hz(root - 12 + (0 if k % 2 == 0 else 7)), BEAT * 0.3)
                add(L, bs, t0 + k * BEAT, 0.4)
                add(R, bs, t0 + k * BEAT, 0.4)
            for k in (1, 3):
                ch = sum(pluck(midi_hz(root + iv + 12), BEAT * 0.4, rng) for iv in tri) / 2
                add(L, ch, t0 + k * BEAT + BEAT / 2, 0.18)
                add(R, ch, t0 + k * BEAT + BEAT / 2, 0.18)
            g = glock(midi_hz(root + 24 + tri[b % 3]), BEAT * 2)
            add(L, g, t0 + 2 * BEAT, 0.08)
            add(R, g, t0 + 2 * BEAT, 0.1)
        else:  # sweet
            pd = pad([midi_hz(root + iv) for iv in tri] + [midi_hz(root - 12)], bar + 0.4)
            add(L, pd, t0, 0.22)
            add(R, pd, t0, 0.22)
            for k, st in enumerate([0, 4, 7, 4]):
                g = glock(midi_hz(scale_note(72 + (root - 60), st)), BEAT * 2)
                add(L, g, t0 + k * BEAT, 0.12)
                add(R, g, t0 + k * BEAT, 0.14)
    out = np.stack([L, R], 1)[: int(seconds * SR)]
    return out / (np.abs(out).max() + 1e-9) * 0.8


# ---- sound effects -------------------------------------------------------

def sfx_whoosh(dur=0.8, rising=False):
    rng = np.random.default_rng(7)
    n = int(dur * SR)
    noise = rng.uniform(-1, 1, n)
    out = np.zeros(n)
    t = np.arange(n) / dur / SR
    cut = (0.02 + 0.25 * (t if rising else 1 - t))
    y = 0.0
    for i in range(n):  # sweeping one-pole low-pass
        y += cut[i] * (noise[i] - y)
        out[i] = y
    e = np.sin(np.pi * t) ** 1.5
    return np.stack([out * e, out * e[::-1]], 1) * 3


def sfx_scratch(dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 900 * np.abs(np.sin(2 * np.pi * 7 * t)) + 150
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4
    rng = np.random.default_rng(3)
    s += rng.uniform(-0.3, 0.3, n)
    s *= np.exp(-t / 0.25)
    return np.stack([s, s], 1) * 0.6


def sfx_pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 400 + 2200 * (t / 0.12)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.04)
    return np.stack([s, s], 1) * 0.7


def sfx_ding():
    s = glock(midi_hz(84), 1.2) + 0.6 * glock(midi_hz(91), 1.2)
    return np.stack([s, s], 1) * 0.5
