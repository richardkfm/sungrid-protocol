#!/usr/bin/env python3
"""First-pass original main-menu music sting (docs/BACKLOG.md Phase 6 follow-up;
see docs/ART_DIRECTION.md). The main menu's background track (audio/music.yaml's
`intro` entry, `Hidden: true` -- not in the jukebox, referenced directly by id)
was still stock Red Alert's own "Intro" theme, pulled from the RA content pack
(`content|intro.aud`) since nothing in mods/sungrid overrode it. That's arguably
as recognizable as the visuals Phase 6's chrome/cursor/terrain passes already
replaced, so it's the same kind of gap as the pre-#41 chrome or pre-this-pass
cursors: audible "stock RA", not "Sungrid Protocol".

Same "programmatic first pass now, real composer pass later" posture the art
generators use (gen_chrome.py, gen_concept_art.py, gen_cursor_art.py): this
synthesizes an original ambient/electronic loop from oscillators and simple
DSP, not a real composition, but it is genuinely original audio -- no sampled
or stock material anywhere in the signal chain.

Ground rules:
  - mod.yaml's SoundFormats already lists `Wav` (alongside `Aud`), so this
    ships as a plain 16-bit PCM WAV -- no Westwood .aud encoder needed.
  - mod.yaml's ContentPackages comment is explicit: `sungrid|bits` (this
    directory) is loaded *after* the content packages specifically so it can
    override same-named content assets. Writing `intro.wav` here overrides
    `content|intro.aud` for the bare id "intro" that audio/music.yaml and the
    main menu both reference -- no YAML changes needed anywhere.
  - Tone: hopeful, driving, electronic-organic (solarpunk, not militaristic) --
    a warm pad progression, a plucked arpeggio outlining a "grid pulse", a
    soft sub bass, and a breathy noise-bed texture, per docs/ART_DIRECTION.md's
    palette-equivalent audio direction (green/gold/blue-black -> warm pads,
    bright plucks, deep sub).
  - Loops cleanly (matching start/end phase, short crossfade at the seam) since
    the jukebox/menu will repeat it.

Usage:
    pip install numpy
    python3 gen_intro_music.py
Writes mods/sungrid/bits/intro.wav directly (overwriting any previous output).
"""
import os
import wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100

# Solarpunk-hopeful progression in A minor -> resolving major colour (vi-IV-I-V
# feel, borrowed-major brightening rather than a straight minor loop).
CHORDS = [
    ("A2", ["A3", "C4", "E4"]),
    ("F2", ["F3", "A3", "C4"]),
    ("C3", ["C4", "E4", "G4"]),
    ("G2", ["G3", "B3", "D4"]),
]

NOTE_FREQS = {}
_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_freq(name):
    if name in NOTE_FREQS:
        return NOTE_FREQS[name]
    pitch = name[:-1]
    octave = int(name[-1])
    semitone = _NAMES.index(pitch)
    midi = (octave + 1) * 12 + semitone
    freq = 440.0 * 2 ** ((midi - 69) / 12)
    NOTE_FREQS[name] = freq
    return freq


def adsr(n, attack, decay, sustain_level, release, sr=SR):
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    s = max(0, n - a - d - r)
    env = np.concatenate([
        np.linspace(0, 1, max(a, 1), endpoint=False),
        np.linspace(1, sustain_level, max(d, 1), endpoint=False),
        np.full(max(s, 1), sustain_level),
        np.linspace(sustain_level, 0, max(r, 1)),
    ])
    return env[:n] if len(env) >= n else np.pad(env, (0, n - len(env)))


def osc_pad(freq, n, sr=SR, detune=0.4):
    t = np.arange(n) / sr
    voices = [0.0, -detune, detune, detune * 2]
    out = np.zeros(n)
    for i, cents in enumerate(voices):
        f = freq * (2 ** (cents / 1200))
        out += np.sin(2 * np.pi * f * t) * (0.5 if i == 0 else 0.28)
        out += 0.12 * np.sin(2 * np.pi * f * 2 * t)
    return out / len(voices)


def osc_pluck(freq, n, sr=SR):
    t = np.arange(n) / sr
    tone = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
    tone += 0.25 * np.sin(2 * np.pi * freq * 3 * t)
    return tone


def osc_sub(freq, n, sr=SR):
    t = np.arange(n) / sr
    return np.sin(2 * np.pi * freq * t) + 0.15 * np.sign(np.sin(2 * np.pi * freq * t)) * 0.2


def simple_delay(sig, sr, delay_s, feedback, mix):
    d = int(delay_s * sr)
    out = sig.copy()
    buf = np.zeros_like(sig)
    buf[d:] = sig[:-d]
    acc = buf.copy()
    for _ in range(4):
        shifted = np.zeros_like(acc)
        shifted[d:] = acc[:-d] * feedback
        acc = shifted
        out += acc
    return sig * (1 - mix) + out * mix / 4


def lowpass(sig, alpha):
    out = np.empty_like(sig)
    prev = 0.0
    for i in range(len(sig)):
        prev = prev + alpha * (sig[i] - prev)
        out[i] = prev
    return out


def build(repeats=4):
    progression = CHORDS * repeats
    bar_seconds = 60.0 / 92 * 4  # 92 BPM, 4/4 bars
    n_per_chord = int(bar_seconds * SR)
    total_n = n_per_chord * len(progression)

    pad = np.zeros(total_n)
    arp = np.zeros(total_n)
    sub = np.zeros(total_n)

    arp_pattern_beats = 8  # eighth notes per bar
    for ci, (root, chord_notes) in enumerate(progression):
        start = ci * n_per_chord
        seg_pad = np.zeros(n_per_chord)
        for note in chord_notes:
            seg_pad += osc_pad(note_freq(note), n_per_chord)
        seg_pad *= adsr(n_per_chord, attack=0.8, decay=0.6, sustain_level=0.75, release=1.2)
        pad[start:start + n_per_chord] += seg_pad

        seg_sub = osc_sub(note_freq(root), n_per_chord) * 0.5
        seg_sub *= adsr(n_per_chord, attack=0.05, decay=0.2, sustain_level=0.85, release=0.3)
        sub[start:start + n_per_chord] += seg_sub

        step_n = n_per_chord // arp_pattern_beats
        seq = (chord_notes * 3)[:arp_pattern_beats]
        for si, note in enumerate(seq):
            s0 = start + si * step_n
            seg = osc_pluck(note_freq(note) * 2, step_n)
            seg *= adsr(step_n, attack=0.005, decay=0.12, sustain_level=0.0, release=0.05)
            arp[s0:s0 + step_n] += seg * 0.35

    rng = np.random.default_rng(42)
    noise = rng.normal(0, 1, total_n)
    noise = lowpass(noise, 0.02) * 0.05

    pad = lowpass(pad, 0.25)
    mix = pad * 0.55 + arp * 0.7 + sub * 0.6 + noise
    mix = simple_delay(mix, SR, delay_s=bar_seconds / 4, feedback=0.35, mix=0.25)

    fade_n = int(1.5 * SR)
    fade_in = np.linspace(0, 1, fade_n)
    fade_out = np.linspace(1, 0, fade_n)
    mix[:fade_n] *= fade_in
    mix[-fade_n:] *= fade_out

    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.9

    return mix


def save_wav(samples, path, sr=SR):
    pcm = np.clip(samples, -1.0, 1.0)
    pcm16 = (pcm * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())
    print(f"wrote {os.path.basename(path)}  {len(samples) / sr:.1f}s  {sr}Hz mono 16-bit")


if __name__ == "__main__":
    audio = build()
    save_wav(audio, os.path.join(HERE, "intro.wav"))
