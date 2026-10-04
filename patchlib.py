"""Line-based patching for the EarthC sources of the SpellRework mod.

The SDK sources mix line endings and carry trailing blanks that editors and
tools strip. Anchors are therefore matched line by line with trailing
whitespace ignored; the replacement is written with the file's own line
ending. Every anchor must match exactly once. Files are only written by
write_all(), after every anchor matched. Text is latin-1 (Polish comments).
"""
import os


class Patcher:
    def __init__(self, folder):
        self.folder = folder
        self.files = {}      # name -> list of lines (without line ending)
        self.newline = {}    # name -> '\r\n' or '\n'
        self.new_files = {}  # name -> text

    def lines(self, name):
        if name not in self.files:
            with open(os.path.join(self.folder, name), 'rb') as f:
                text = f.read().decode('latin-1')
            self.newline[name] = '\r\n' if '\r\n' in text else '\n'
            self.files[name] = text.replace('\r\n', '\n').split('\n')
        return self.files[name]

    def replace_once(self, name, old, new):
        lines = self.lines(name)
        want = [l.rstrip() for l in old.replace('\r\n', '\n').rstrip('\n').split('\n')]
        stripped = [l.rstrip() for l in lines]
        hits = [i for i in range(len(lines) - len(want) + 1) if stripped[i:i + len(want)] == want]
        if len(hits) != 1:
            raise SystemExit('%s: anchor found %d times: %r' % (name, len(hits), want[:3]))
        i = hits[0]
        repl = new.replace('\r\n', '\n').rstrip('\n').split('\n')
        self.files[name] = lines[:i] + repl + lines[i + len(want):]

    def add_file(self, name, text):
        self.new_files[name] = text

    def write_all(self):
        for name, lines in self.files.items():
            with open(os.path.join(self.folder, name), 'wb') as f:
                f.write(self.newline[name].join(lines).encode('latin-1'))
        for name, text in self.new_files.items():
            with open(os.path.join(self.folder, name), 'wb') as f:
                f.write(text.replace('\r\n', '\n').replace('\n', '\r\n').encode('latin-1'))
        return sorted(list(self.files) + list(self.new_files))
