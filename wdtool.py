"""WD archive helpers for the SpellRework mod (read retail archives, write the mod).

Format as measured for the Quest Limit Patcher and the Probe mod (see the
tw1-modding skill): WD 0x200, zlib header record, zlib entries, zlib
directory at the end, last 4 bytes = directory length + 4. Script entries
need flags 0x3b, the resource name and class id of the retail entry, and a
NEW GUID (the engine keys scripts by GUID; the retail GUID keeps the original).
"""
import os
import random
import struct
import time
import zlib

GAME = r'F:\SteamLibrary\steamapps\common\Two Worlds - Epic Edition'
WD_MAGIC = bytes([0xFF, 0xA1, 0xD0, 0x31, 0x57, 0x44, 0x00, 0x02])
FILETIME_EPOCH = 116444736000000000


def entries(path):
    with open(path, 'rb') as f:
        f.seek(-4, 2)
        dir_off = struct.unpack('<I', f.read(4))[0]
        f.seek(-dir_off, 2)
        raw = f.read()
    d = zlib.decompressobj()
    t = d.decompress(raw) + d.flush()
    off = 8
    n = struct.unpack_from('<H', t, off)[0]
    off += 2
    out = []
    for _ in range(n):
        nl = t[off]; off += 1
        name = t[off:off + nl].decode('latin-1'); off += nl
        flags, foff, clen, rlen = struct.unpack_from('<BIII', t, off); off += 13
        res = kid = guid = None
        if flags & 0x08:
            xl = t[off]; off += 1
            res = t[off:off + xl]; off += xl
        if flags & 0x10:
            kid = struct.unpack_from('<I', t, off)[0]; off += 4
        if flags & 0x20:
            guid = t[off:off + 16]; off += 16
        out.append({'path': name, 'flags': flags, 'offset': foff, 'clen': clen,
                    'rlen': rlen, 'res': res, 'id': kid, 'guid': guid})
    return out


def read(path, entry):
    with open(path, 'rb') as f:
        f.seek(entry['offset'])
        raw = f.read(entry['clen'])
    if entry['flags'] & 0x01:
        d = zlib.decompressobj()
        return d.decompress(raw) + d.flush()
    return raw


def find(path, inner):
    for e in entries(path):
        if e['path'].lower() == inner.lower():
            return e
    return None


def eco_body(raw):
    """ECO body: naked, or the compiler's two-stream file (header + body)."""
    if raw[:4] == b'ECO' + bytes(1):
        return raw
    if raw[:2] == b'\x78\x9c':
        d = zlib.decompressobj()
        d.decompress(raw)
        rest = d.unused_data
        return zlib.decompress(rest) if rest[:2] == b'\x78\x9c' else rest
    raise ValueError('unknown .eco layout')


def latest(inner, archives=('Update16.wd', 'Update11-15.wd', 'Scripts.wd')):
    """(archive, entry) of the newest retail copy of a file."""
    for a in archives:
        p = os.path.join(GAME, 'WDFiles', a)
        if os.path.exists(p):
            e = find(p, inner)
            if e:
                return p, e
    raise FileNotFoundError(inner)


def build(out_path, files):
    """files: list of dicts {path, data, flags, res, id, guid}. Writes a WD 0x200 archive."""
    head = zlib.compress(WD_MAGIC + random.randbytes(16))
    body = bytearray()
    tab = struct.pack('<QH', int(time.time() * 10000000) + FILETIME_EPOCH, len(files))
    offset = len(head)
    for f in files:
        data = zlib.compress(f['data']) if f['flags'] & 0x01 else f['data']
        path = f['path'].encode('latin-1')
        tab += bytes([len(path)]) + path
        tab += struct.pack('<BIII', f['flags'], offset + len(body), len(data), len(f['data']))
        if f['flags'] & 0x08:
            tab += bytes([len(f['res'])]) + f['res']
        if f['flags'] & 0x10:
            tab += struct.pack('<I', f['id'])
        if f['flags'] & 0x20:
            tab += f['guid']
        body += data
    cdir = zlib.compress(tab)
    with open(out_path, 'wb') as fh:
        fh.write(head)
        fh.write(body)
        fh.write(cdir)
        fh.write(struct.pack('<I', len(cdir) + 4))
