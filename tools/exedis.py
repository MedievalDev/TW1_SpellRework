"""Small static-analysis helper for TwoWorlds.exe 1.7 (capstone + pefile).

    py exedis.py str NAME          code references to an ASCII string
    py exedis.py d HEXADDR [N]     disassemble N instructions
    py exedis.py c HEXADDR         direct calls (E8) to an address
    py exedis.py f HEXADDR         start of the function containing an address
"""
import re
import struct
import sys

import capstone
import pefile

EXE = r'F:\SteamLibrary\steamapps\common\Two Worlds - Epic Edition\TwoWorlds.exe'
pe = pefile.PE(EXE, fast_load=True)
BASE = pe.OPTIONAL_HEADER.ImageBase
DATA = open(EXE, 'rb').read()
SECS = [(BASE + s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData,
         s.Name.rstrip(b'\0').decode()) for s in pe.sections]
TEXT = next(s for s in SECS if s[4] == '.text')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True


def va2off(va):
    for sva, vsz, raw, rsz, _n in SECS:
        if sva <= va < sva + max(vsz, rsz):
            return raw + (va - sva)
    return None


def off2va(off):
    for sva, vsz, raw, rsz, n in SECS:
        if raw <= off < raw + rsz:
            return sva + off - raw, n
    return None, None


def rd(va, n):
    o = va2off(va)
    return DATA[o:o + n]


def cstr(va):
    o = va2off(va)
    if o is None:
        return None
    e = DATA.find(b'\0', o)
    s = DATA[o:e]
    return s.decode('ascii') if s and all(32 <= c < 127 for c in s) else None


def disasm(va, n=80, stop_ret=True):
    out = []
    for i in md.disasm(rd(va, n * 8), va):
        note = ''
        for op in i.operands:
            imm = op.imm if op.type == capstone.x86.X86_OP_IMM else (
                op.mem.disp if op.type == capstone.x86.X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0 else None)
            if imm and BASE <= imm < BASE + 0x800000:
                s = cstr(imm)
                if s and len(s) >= 3:
                    note = '  ; "%s"' % s[:60]
        out.append('%08x  %-6s %s%s' % (i.address, i.mnemonic, i.op_str, note))
        if len(out) >= n or (stop_ret and i.mnemonic == 'ret'):
            break
    return '\n'.join(out)


def refs_to(va):
    sva, _v, raw, rsz, _n = TEXT
    pat = struct.pack('<I', va)
    code = DATA[raw:raw + rsz]
    res, i = [], code.find(pat)
    while i != -1:
        res.append(sva + i)
        i = code.find(pat, i + 1)
    return res


def callers(target):
    sva, _v, raw, rsz, _n = TEXT
    code = DATA[raw:raw + rsz]
    res, i = [], code.find(b'\xe8')
    while i != -1:
        if i + 5 <= len(code) and sva + i + 5 + struct.unpack('<i', code[i + 1:i + 5])[0] == target:
            res.append(sva + i)
        i = code.find(b'\xe8', i + 1)
    return res


def func_start(va, back=0x4000):
    o = va2off(va)
    for k in range(1, back):
        p = o - k
        if DATA[p] == 0xcc and DATA[p + 1] != 0xcc:
            return va - k + 1
    return None


def string_refs(name):
    out = []
    for m in re.finditer(re.escape(name.encode()) + b'\x00', DATA):
        va, sec = off2va(m.start())
        if va and DATA[m.start() - 1] == 0:
            out.append((va, sec, refs_to(va)))
    return out


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'str':
        for va, sec, refs in string_refs(sys.argv[2]):
            print('%s %08x refs %s' % (sec, va, ' '.join('%08x' % r for r in refs)))
    elif cmd == 'd':
        print(disasm(int(sys.argv[2], 16), int(sys.argv[3]) if len(sys.argv) > 3 else 80))
    elif cmd == 'c':
        print(' '.join('%08x' % x for x in callers(int(sys.argv[2], 16))))
    elif cmd == 'f':
        print('%08x' % func_start(int(sys.argv[2], 16)))
