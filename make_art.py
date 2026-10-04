r"""Tornado card art: card texture, inventory icon, card .prt, missile .prt -> art/.

    py make_art.py

Inputs (ref/, extracted from the game archives):
  AIR_LIGHTING.DDS / AIR_PUSH_WAVE.DDS   card textures 128x256 DXT5 (ring 1 / ring 4)
  LIGHTING_CARD.DDS / PUSH_WAVE_CARD.DDS inventory icons 96x128 DXT1
  LIGHTING_CARD.prt                       card particle, carries the card texture path
  tornado.png                             picture from ComfyUI (tools/comfy_gen.py, seed 44)
The Lightning card (ring 1, one air symbol) is the base. Its frame and
corner ornaments are kept: a pixel inside the picture area that is equal
on the Lightning and the Push Wave card (same frame, other picture) and
not dark belongs to the frame. Everything else gets the new picture.

Tornado effect: the desert sand devil Particles\Enviroment\Desert\SANDDEVIL2.prt
(Graphics.wd; a spinning column that widens upwards, picked and checked in
the SDK's ParticleEdit) recoloured to pale storm blue - particle colour =
curve pairs 6-8 (curves 12-17), light colour = emitter curves 22-27, layout
from wicked/tw1probe/research/prtparse.py and spell_vfx.md. Curves AND the
baked per-tick tables behind them are changed (the game reads the tables).
"""
import io
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageFilter

import wdtool as W

sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'Desktop', 'wicked', 'tw1probe', 'research'))
import prtparse  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(ROOT, 'ref')
ART = os.path.join(ROOT, 'art')
SEP = chr(92)

# picture area (x0, y0, x1, y1) inside the frame, measured on the originals
CARD_RECT = (8, 12, 120, 214)
ICON_RECT = (5, 5, 91, 107)
MISSILE_TEMPLATE = SEP.join(['Particles', 'Enviroment', 'Desert', 'SANDDEVIL2.prt'])
TORNADO_TINT = (0.72, 0.84, 1.0)    # pale storm blue, times the layer's old brightness
TORNADO_LIGHT = (0.45, 0.6, 1.0)
TORNADO_GAIN = 1.0
CARD_TEX_OLD = SEP.join(['Textures', 'Particles', 'Cards', 'AIR_LIGHTING.DDS'])
CARD_TEX_NEW = SEP.join(['Textures', 'Particles', 'Cards', 'AIR_TORNADO1.DDS'])
ARCHIVES = ('Update16.wd', 'Update11-15.wd', 'Graphics.wd')
PUSHWAVE_TEMPLATE = SEP.join(['Particles', 'Magic', 'PUSH_WAVE_HIT.prt'])
PUSHHIT_TEMPLATE = SEP.join(['Particles', 'Magic', 'MAGICHAMMER_HIT.prt'])
PUSH_TINT = (0.78, 0.9, 1.0)        # wind: white with a touch of blue
PUSH_LIGHT = (0.55, 0.75, 1.0)


def rgba(name):
    return np.array(Image.open(os.path.join(REF, name)).convert('RGBA')).astype(np.int32)


def frame_mask(a, b, rect):
    """1 = keep the original pixel (frame/ornament), 0 = new picture."""
    h, w = a.shape[:2]
    diff = np.abs(a[..., :3] - b[..., :3]).max(axis=2)
    bright = a[..., :3].max(axis=2)
    warm = (a[..., 0] - a[..., 2]) > 6
    x0, y0, x1, y1 = rect
    # ornaments only reach into the picture at the two top corners and along the edges
    zone = np.zeros((h, w), bool)
    cw, ch = (x1 - x0) * 3 // 10, (y1 - y0) // 6
    zone[y0:y0 + ch, x0:x0 + cw] = True
    zone[y0:y0 + ch, x1 - cw:x1] = True
    zone[y0:y1, x0:x0 + 3] = zone[y0:y1, x1 - 3:x1] = True
    zone[y1 - 3:y1, x0:x1] = True
    keep = (diff < 40) & (bright > 45) & warm & zone
    inside = np.zeros((h, w), bool)
    inside[y0:y1, x0:x1] = True
    keep = keep | ~inside
    # soft edge between ornament and picture
    m = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    return np.array(m).astype(np.float32) / 255.0


def picture(src, rect):
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    im = src.copy()
    sw, sh = im.size
    # cover-crop to the area's aspect
    if sw / sh > w / h:
        nw = int(sh * w / h)
        im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw * h / w)
        im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    im = im.resize((w, h), Image.LANCZOS)
    p = np.array(im.convert('RGB')).astype(np.float32)
    # darken towards the frame like the originals
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.maximum(np.abs(xx - w / 2) / (w / 2), np.abs(yy - h / 2) / (h / 2))
    vign = np.clip(1.15 - 0.55 * d ** 3, 0, 1)
    return p * vign[..., None]


def compose(base_name, other_name, rect, src):
    a = rgba(base_name)
    m = frame_mask(a, rgba(other_name), rect)
    out = a.astype(np.float32).copy()
    x0, y0, x1, y1 = rect
    pic = picture(src, rect)
    region = out[y0:y1, x0:x1, :3]
    mm = m[y0:y1, x0:x1, None]
    out[y0:y1, x0:x1, :3] = region * mm + pic * (1 - mm)
    out[y0:y1, x0:x1, 3] = np.maximum(out[y0:y1, x0:x1, 3], 255 * (1 - m[y0:y1, x0:x1]))
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), 'RGBA')


def dxt_level(img, fmt):
    w, h = img.size
    pw, ph = max(4, (w + 3) // 4 * 4), max(4, (h + 3) // 4 * 4)
    if (pw, ph) != (w, h):
        pad = Image.new('RGBA', (pw, ph))
        pad.paste(img, (0, 0))
        img = pad
    buf = io.BytesIO()
    (img if fmt == 'DXT5' else img.convert('RGB')).save(buf, format='DDS', pixel_format=fmt)
    raw = buf.getvalue()
    assert raw[84:88] == fmt.encode(), raw[84:88]
    return raw[128:]


def write_dds(img, template_name, out_path):
    """Same header (size, format, mip count) as the original, new data for every mip level."""
    tmpl = open(os.path.join(REF, template_name), 'rb').read()
    fmt = tmpl[84:88].decode()
    h, w = struct.unpack_from('<II', tmpl, 12)
    mips = struct.unpack_from('<I', tmpl, 28)[0] or 1
    assert img.size == (w, h), (img.size, w, h)
    data = b''
    for lvl in range(mips):
        lw, lh = max(1, w >> lvl), max(1, h >> lvl)
        data += dxt_level(img if lvl == 0 else img.resize((lw, lh), Image.LANCZOS), fmt)
    out = tmpl[:128] + data
    assert len(out) == len(tmpl), (len(out), len(tmpl))
    open(out_path, 'wb').write(out)
    return out


def swap_texture_path(prt, old, new):
    """The card .prt names its texture as u32 length + characters (no terminator)."""
    ob, nb = old.encode('latin-1'), new.encode('latin-1')
    i = prt.lower().find(ob.lower())
    assert i >= 4 and prt.lower().count(ob.lower()) == 1, 'texture path not found once'
    n = struct.unpack_from('<I', prt, i - 4)[0]
    assert n == len(ob), (n, len(ob))
    return prt[:i - 4] + struct.pack('<I', len(nb)) + nb + prt[i + len(ob):]


def set_curve(d, off, value):
    """every key of the curve at off gets value (key = f32 0, time, value, tangent in, tangent out)."""
    n = struct.unpack_from('<I', d, off)[0]
    for k in range(n):
        struct.pack_into('<f', d, off + 4 + 20 * k + 8, value)


def curve_offsets(d, start, count):
    out = []
    o = start
    for _ in range(count):
        out.append(o)
        _keys, o = prtparse.curve(d, o)
    return out


def scale_curve(d, off, factor):
    n = struct.unpack_from('<I', d, off)[0]
    for k in range(n):
        o = off + 4 + 20 * k + 8
        struct.pack_into('<f', d, o, min(1.0, struct.unpack_from('<f', d, o)[0] * factor))


def table_offsets(d, start, count):
    """Baked per-tick tables after the curves (the game reads these, ParticleEdit's preview the curves):
    per curve u32 n, u32 0, n x f32 samples, u8 isConst, f32 const. Returns (samples_off, n, isconst_off)."""
    out = []
    o = start
    for _ in range(count):
        n, zero = struct.unpack_from('<II', d, o)
        assert zero == 0 and n < 100000, (o, n, zero)
        out.append((o + 8, n, o + 8 + 4 * n))
        o += 8 + 4 * n + 5
    return out


def set_table(d, tab, value):
    s, n, c = tab
    for k in range(n):
        struct.pack_into('<f', d, s + 4 * k, value)
    if d[c]:
        struct.pack_into('<f', d, c + 1, value)


def scale_table(d, tab, factor):
    s, n, c = tab
    for k in range(n):
        struct.pack_into('<f', d, s + 4 * k, min(1.0, struct.unpack_from('<f', d, s + 4 * k)[0] * factor))
    if d[c]:
        struct.pack_into('<f', d, c + 1, min(1.0, struct.unpack_from('<f', d, c + 1)[0] * factor))


def table_values(d, tab):
    s, n, c = tab
    vals = list(struct.unpack_from('<%df' % n, d, s))
    if d[c]:
        vals.append(struct.unpack_from('<f', d, c + 1)[0])
    return vals


def recolour_prt(src, tint, gain, light, alpha_gain=1.0):
    """Every textured, coloured layer gets tint x its old brightness x gain; lights get light.

    Changes the colour curves (particle curves 12-17), the alpha curves
    (18-19) and the light colour curves (emitter 22-27) AND their baked
    tables in the block tail, so curves and tables agree. The file keeps its
    size and layout. Pure white layers (distortion rings, sparks) stay as
    they are.
    """
    r = prtparse.parse(src)
    post = 152 if src[3] == 2 else 148
    d = bytearray(src)
    checks = []
    for q in r['particles']:
        if not q.textures:
            continue
        first = [q.curves[12 + 2 * c][0][1] for c in range(3)]
        if all(abs(v - 1.0) < 1e-6 for v in first):
            continue
        p = prtparse.particle_head(src, q.offset)[8]
        offs = curve_offsets(src, p + 200, 28)
        assert prtparse.curves(src, p + 200, 28)[1] == q.curves_end, q.name
        tabs = table_offsets(src, q.curves_end, 28)
        lum = 0.3 * first[0] + 0.59 * first[1] + 0.11 * first[2]
        for c in range(3):
            v = min(1.0, lum * gain * tint[c])
            for i in (12 + 2 * c, 13 + 2 * c):
                set_curve(d, offs[i], v)
                set_table(d, tabs[i], v)
                checks.append((tabs[i], v))
        if alpha_gain != 1.0:
            for i in (18, 19):
                scale_curve(d, offs[i], alpha_gain)
                scale_table(d, tabs[i], alpha_gain)
    for e in r['emitters']:
        if all(abs(e.curves[22 + i][0][1] - 1.0) < 1e-6 for i in range(6)):
            continue                     # white = the default, no own light
        cs = prtparse.emitter_head(src, e.offset, post)[3]
        offs = curve_offsets(src, cs, 44)
        assert prtparse.curves(src, cs, 44)[1] == e.curves_end, e.name
        tabs = table_offsets(src, e.curves_end, 44)
        for c in range(3):
            for i in (22 + 2 * c, 23 + 2 * c):
                set_curve(d, offs[i], light[c])
                set_table(d, tabs[i], light[c])
                checks.append((tabs[i], light[c]))
    out = bytes(d)
    for tab, v in checks:
        assert all(abs(x - v) < 1e-6 for x in table_values(out, tab)), (tab, v)
    chk = prtparse.parse(out)
    assert len(out) == len(src) and len(chk['particles']) == len(r['particles']) and chk['end'] == r['end']
    return out


def tornado_prt(src):
    """The sand devil as a storm: pale blue layers at their old brightness (the dark debris stays dark)."""
    return recolour_prt(src, TORNADO_TINT, TORNADO_GAIN, TORNADO_LIGHT)


def art_from(inner, name, fn):
    arc, e = W.latest(inner, ARCHIVES)
    open(os.path.join(ART, name), 'wb').write(fn(W.read(arc, e)))


def main():
    os.makedirs(ART, exist_ok=True)
    src = Image.open(os.path.join(REF, 'tornado.png')).convert('RGB')

    card = compose('AIR_LIGHTING.DDS', 'AIR_PUSH_WAVE.DDS', CARD_RECT, src)
    icon = compose('LIGHTING_CARD.DDS', 'PUSH_WAVE_CARD.DDS', ICON_RECT, src)
    card.save(os.path.join(REF, 'AIR_TORNADO_preview.png'))
    icon.save(os.path.join(REF, 'TORNADO_CARD_preview.png'))
    write_dds(card, 'AIR_LIGHTING.DDS', os.path.join(ART, 'AIR_TORNADO1.DDS'))
    write_dds(icon, 'LIGHTING_CARD.DDS', os.path.join(ART, 'TORNADO_CARD.DDS'))

    prt = open(os.path.join(REF, 'LIGHTING_CARD.prt'), 'rb').read()
    new = swap_texture_path(prt, CARD_TEX_OLD, CARD_TEX_NEW)
    assert len(new) == len(prt)
    open(os.path.join(ART, 'TORNADO_CARD.prt'), 'wb').write(new)

    art_from(MISSILE_TEMPLATE, 'TORNADO_MISSILE.prt', tornado_prt)
    # Push Wave: the wave brighter and stronger, a wind impact on every unit it hits
    art_from(PUSHWAVE_TEMPLATE, 'SR_PUSH_WAVE.prt',
             lambda b: recolour_prt(b, PUSH_TINT, 1.7, PUSH_LIGHT, alpha_gain=1.4))
    art_from(PUSHHIT_TEMPLATE, 'SR_PUSH_UNIT_HIT.prt',
             lambda b: recolour_prt(b, PUSH_TINT, 2.6, PUSH_LIGHT))
    for old in ('AIR_TORNADO.DDS', 'SR_TORNADO_SWIRL4.dds'):
        if os.path.exists(os.path.join(ART, old)):
            os.remove(os.path.join(ART, old))
    for n in sorted(os.listdir(ART)):
        print('art/%-22s %6d bytes' % (n, os.path.getsize(os.path.join(ART, n))))


if __name__ == '__main__':
    main()
