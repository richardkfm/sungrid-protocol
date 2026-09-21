"""Minimal RA/TD .shp decoder (Format80 LCW + Format40 XOR delta)."""
import struct, sys, os
from PIL import Image

def lcw(src, dst_len):
    out = bytearray()
    i = 0
    while i < len(src) and len(out) < dst_len:
        b = src[i]; i += 1
        if b == 0x80:
            break
        if b & 0x80 == 0:           # 0cccpppp p : copy from dest, rel
            cnt = (b >> 4) + 3
            pos = ((b & 0x0F) << 8) | src[i]; i += 1
            start = len(out) - pos
            for k in range(cnt): out.append(out[start + k])
        elif b & 0x40 == 0:         # 10cccccc : copy cnt bytes from src
            cnt = b & 0x3F
            out += src[i:i + cnt]; i += cnt
        elif b == 0xFE:             # fill
            cnt = src[i] | (src[i+1] << 8); v = src[i+2]; i += 3
            out += bytes([v]) * cnt
        elif b == 0xFF:             # long copy abs
            cnt = src[i] | (src[i+1] << 8); pos = src[i+2] | (src[i+3] << 8); i += 4
            for k in range(cnt): out.append(out[pos + k])
        else:                       # 11cccccc pp pp : copy cnt+3 from abs pos
            cnt = (b & 0x3F) + 3
            pos = src[i] | (src[i+1] << 8); i += 2
            for k in range(cnt): out.append(out[pos + k])
    return bytes(out[:dst_len])

def xor_delta(src, base):
    out = bytearray(base)
    i = 0; p = 0
    while i < len(src):
        b = src[i]; i += 1
        if b == 0x80:
            cnt = src[i] | (src[i+1] << 8); i += 2
            if cnt == 0: break
            if cnt & 0x8000 == 0:
                p += cnt
            elif cnt & 0x4000 == 0:
                cnt &= 0x3FFF
                for k in range(cnt): out[p] ^= src[i + k]; p += 1
                i += cnt
            else:
                cnt &= 0x3FFF; v = src[i]; i += 1
                for k in range(cnt): out[p] ^= v; p += 1
        elif b & 0x80:
            p += b & 0x7F
        elif b == 0:
            cnt = src[i]; v = src[i+1]; i += 2
            for k in range(cnt): out[p] ^= v; p += 1
        else:
            for k in range(b): out[p] ^= src[i + k]; p += 1
            i += b
    return bytes(out)

def read_shp(path):
    d = open(path, 'rb').read()
    count, x, y, w, h, delta, flags = struct.unpack('<HHHHHHH', d[:14])
    ents = []
    for k in range(count + 2):
        o = 14 + k * 8
        off = d[o] | (d[o+1] << 8) | (d[o+2] << 16); fmt = d[o+3]
        roff = d[o+4] | (d[o+5] << 8) | (d[o+6] << 16); rfmt = d[o+7]
        ents.append((off, fmt, roff, rfmt))
    frames = [None] * count
    size = w * h
    def decode(k):
        if frames[k] is not None: return frames[k]
        off, fmt, roff, rfmt = ents[k]
        end = ents[k + 1][0]
        chunk = d[off:end]
        if fmt == 0x80:
            f = lcw(chunk, size)
        elif fmt == 0x40:
            # ref by offset: find frame whose offset == roff
            ref = next(i for i, e in enumerate(ents[:count]) if e[0] == roff)
            f = xor_delta(chunk, decode(ref))
        elif fmt == 0x20:
            f = xor_delta(chunk, decode(k - 1))
        else:
            raise ValueError(fmt)
        frames[k] = f
        return f
    for k in range(count): decode(k)
    return w, h, frames

def load_pal(path):
    raw = open(path, 'rb').read()
    return [(raw[i*3] << 2, raw[i*3+1] << 2, raw[i*3+2] << 2) for i in range(256)]

def frame_rgba(w, h, f, pal, shadow=(0, 0, 0, 120)):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = img.load()
    for yy in range(h):
        for xx in range(w):
            v = f[yy * w + xx]
            if v == 0: continue
            if v == 4: px[xx, yy] = shadow; continue
            px[xx, yy] = pal[v] + (255,)
    return img

if __name__ == '__main__':
    w, h, frames = read_shp(sys.argv[1])
    print(sys.argv[1], w, h, len(frames))
