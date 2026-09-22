#!/usr/bin/env python3
"""Original weapon sounds for the two arc-discharge weapons (docs/BACKLOG.md
issue #110): `arcfire.wav` for the Arc Turret's ArcDischarge and `disrfire.wav`
for the Disruptor Trooper's Disruptor.

Why these exist: issue #14 turned the Flame Tower / Flame Infantry into the
Arc Turret / Disruptor Trooper by swapping the weapons, but the stock flame
weapons made their noise through the napalm impact effect that #14 removed,
so the Disruptor has fired in silence ever since, and the Arc Turret was given
`turret1.aud` -- the machine-gun turret's report. The only electric sound in
the RA content is `tesla1.aud`, which is the Tesla Coil's and the Shock
Trooper's; reusing it would make three actors sound the same. Same posture as
gen_intro_music.py: synthesized from oscillators, noise and simple DSP, no
sampled or stock material anywhere in the chain, so it is genuinely original
and regenerates byte-identically (fixed RNG seeds).

Ground rules (shared with gen_intro_music.py):
  - mod.yaml's SoundFormats lists `Wav`, and `sungrid|bits` loads after the
    content packages, so a plain 16-bit PCM WAV here is referenced by file
    name from weapons/other.yaml (`Report: arcfire.wav`,
    `StartBurstReport: disrfire.wav`) -- the engine looks the name up with its
    extension, so the `.wav` is part of the reference.
  - Lengths are tuned to the weapons: ArcDischarge plays `Report` once per
    zap, two zaps 20 ticks (0.8 s) apart, so its sound is a ~0.45 s crack that
    has decayed before the second one. The Disruptor plays `StartBurstReport`
    once at the start of its 15-shot, 15-tick (0.6 s) burst, so its sound is
    a ~0.75 s sustained sizzle that covers the burst and tails off.
  - Mono, 44.1 kHz, peak-normalised below full scale with short fades at both
    ends so nothing clicks.

Sound design, in words: the turret is a single heavy discharge -- an
instantaneous broadband crack, a dense crackle that thins out, a low buzzing
hum falling in pitch (the "transformer" body of the sound) and a brief hiss.
The trooper's prod is smaller and continuous -- a sputtering sizzle whose
grain is gated by a random flicker, over a lighter buzz, with sparse pops.

Usage:
    pip install numpy
    python3 gen_arc_sounds.py
Writes arcfire.wav and disrfire.wav next to this file, overwriting them.
"""

import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def bandpass(sig, lo, hi, sr=SR, edge=0.25):
    """FFT band-pass with soft (raised-cosine) edges, `edge` as a fraction of
    each cutoff, so the filter does not ring. Zero-phase: fine for effects."""
    n = len(sig)
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    mask = np.ones_like(freqs)
    lo_w = max(lo * edge, 1.0)
    hi_w = max(hi * edge, 1.0)
    below = freqs < lo
    mask[below] = 0.5 * (1 + np.cos(np.clip((lo - freqs[below]) / lo_w, 0, 1) * np.pi))
    above = freqs > hi
    mask[above] = 0.5 * (1 + np.cos(np.clip((freqs[above] - hi) / hi_w, 0, 1) * np.pi))
    return np.fft.irfft(spec * mask, n)


def exp_decay(n, tau, sr=SR):
    t = np.arange(n) / sr
    return np.exp(-t / tau)


def crackle(rng, n, rate_start, rate_end, grain_ms=(1.5, 6.0), sr=SR):
    """Sparse random impulses whose density falls from rate_start to rate_end
    (events per second) across the buffer, each an exponentially decaying
    noise grain. This is the 'frying' texture of an electric discharge."""
    out = np.zeros(n)
    t = 0.0
    while True:
        frac = t * sr / n
        if frac >= 1.0:
            break
        rate = rate_start + (rate_end - rate_start) * frac
        t += rng.exponential(1.0 / max(rate, 1e-3))
        i = int(t * sr)
        if i >= n:
            break
        g_len = int(rng.uniform(*grain_ms) * sr / 1000)
        grain = rng.normal(0, 1, g_len) * exp_decay(g_len, g_len / sr / 3.0)
        amp = rng.uniform(0.4, 1.0)
        end = min(n, i + g_len)
        out[i:end] += grain[: end - i] * amp
    return out


def buzz(n, f_start, f_end, harmonics=10, jitter=0.0, rng=None, sr=SR):
    """Harmonic-rich hum (1/k rolloff, odd harmonics louder) sweeping from
    f_start to f_end, with optional slow random pitch jitter."""
    t = np.arange(n) / sr
    f = f_start + (f_end - f_start) * (t / t[-1])
    if jitter and rng is not None:
        wobble = rng.normal(0, 1, n)
        wobble = np.cumsum(wobble) / sr
        wobble = wobble - np.linspace(wobble[0], wobble[-1], n)
        f = f * (1 + jitter * wobble / (np.max(np.abs(wobble)) + 1e-9))
    phase = 2 * np.pi * np.cumsum(f) / sr
    out = np.zeros(n)
    for k in range(1, harmonics + 1):
        amp = (1.0 / k) * (1.0 if k % 2 else 0.55)
        out += amp * np.sin(k * phase)
    return out / np.max(np.abs(out))


def fade_ends(sig, ms=4.0, sr=SR):
    k = int(ms * sr / 1000)
    sig[:k] *= np.linspace(0, 1, k)
    sig[-k:] *= np.linspace(1, 0, k)
    return sig


def normalise(sig, peak):
    m = np.max(np.abs(sig))
    return sig / m * peak if m > 0 else sig


def save_wav(samples, path, sr=SR):
    pcm = np.clip(samples, -1.0, 1.0)
    pcm16 = (pcm * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())
    rms = float(np.sqrt(np.mean(pcm ** 2)))
    print(f"wrote {os.path.basename(path)}  {len(samples) / sr:.2f}s  {sr}Hz mono 16-bit"
          f"  peak={np.max(np.abs(pcm)):.2f} rms={rms:.3f}")


# ---------------------------------------------------------------------------
# The two sounds
# ---------------------------------------------------------------------------

def arc_turret_fire():
    """ArcDischarge: one heavy discharge, ~0.45 s."""
    rng = np.random.default_rng(110)
    n = int(0.45 * SR)

    # Instantaneous crack: a few ms of full-band noise, hard-edged.
    crack_n = int(0.004 * SR)
    crack = np.zeros(n)
    crack[:crack_n] = rng.normal(0, 1, crack_n) * np.linspace(1, 0.3, crack_n)
    crack = bandpass(crack, 400, 12000)

    # Dense crackle that thins out as the arc collapses.
    fry = crackle(rng, n, rate_start=2600, rate_end=120)
    fry = bandpass(fry, 1200, 7500) * exp_decay(n, 0.13)

    # Transformer body: buzzing hum sliding down as the capacitor bank dumps.
    hum = buzz(n, 132, 88, harmonics=12, jitter=0.02, rng=rng)
    hum *= exp_decay(n, 0.11)
    hum = bandpass(hum, 60, 2400)

    # Brief hiss halo on the top end.
    hiss = bandpass(rng.normal(0, 1, n), 3500, 10000) * exp_decay(n, 0.07)

    # Low thump so it has weight next to the ported RA gun sounds.
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * 58 * t) * exp_decay(n, 0.045)

    mix = crack * 0.9 + fry * 0.75 + hum * 0.55 + hiss * 0.28 + thump * 0.5
    return fade_ends(normalise(mix, 0.9))


def disruptor_fire():
    """Disruptor: a sustained sputtering sizzle, ~0.75 s (0.6 s burst + tail)."""
    rng = np.random.default_rng(1114)
    n = int(0.75 * SR)
    t = np.arange(n) / SR

    # Amplitude envelope: fast on, held for the burst, released after it.
    env = np.ones(n)
    on = int(0.012 * SR)
    env[:on] = np.linspace(0, 1, on)
    rel_start = int(0.58 * SR)
    env[rel_start:] = np.exp(-(t[rel_start:] - t[rel_start]) / 0.06)

    # Sizzle: band-limited noise gated by a fast random flicker, so it
    # sputters rather than hisses steadily.
    flicker = bandpass(rng.normal(0, 1, n), 8, 60)
    flicker = np.clip(flicker / (np.max(np.abs(flicker)) + 1e-9) * 1.6 + 0.55, 0, 1)
    sizzle = bandpass(rng.normal(0, 1, n), 1800, 9000) * flicker

    # Continuous crackle grain underneath at a steady rate.
    fry = bandpass(crackle(rng, n, rate_start=900, rate_end=700), 1000, 6500)

    # Lighter buzz than the turret's, wandering in pitch.
    hum = bandpass(buzz(n, 104, 96, harmonics=8, jitter=0.05, rng=rng), 70, 1800)

    # Sparse louder pops through the burst.
    pops = bandpass(crackle(rng, n, rate_start=40, rate_end=25, grain_ms=(3.0, 9.0)), 500, 5000)

    mix = (sizzle * 0.6 + fry * 0.5 + hum * 0.32 + pops * 0.7) * env
    return fade_ends(normalise(mix, 0.8))


if __name__ == "__main__":
    save_wav(arc_turret_fire(), os.path.join(HERE, "arcfire.wav"))
    save_wav(disruptor_fire(), os.path.join(HERE, "disrfire.wav"))
