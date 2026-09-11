"""Minimal Lua SavedVariables parser -> Python dicts. Tables always become dicts."""
import re

TOK = re.compile(r'''
   (?P<ws>\s+|--\[\[.*?\]\]|--[^\n]*)
 | (?P<str>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')
 | (?P<num>-?(?:0x[0-9a-fA-F]+|\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?))
 | (?P<name>[A-Za-z_][A-Za-z0-9_]*)
 | (?P<p>[{}\[\]=,;])
''', re.X | re.S)

ESC = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", 'a': '\a', 'b': '\b', 'f': '\f', 'v': '\v', '\n': '\n'}


def unq(s):
    body = s[1:-1]
    if '\\' not in body:
        return body
    out = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            d = body[i + 1]
            if d.isdigit():
                j = i + 1
                while j < len(body) and j < i + 4 and body[j].isdigit():
                    j += 1
                out.append(chr(int(body[i + 1:j])))
                i = j
                continue
            out.append(ESC.get(d, d))
            i += 2
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def tokenize(text):
    pos = 0
    n = len(text)
    toks = []
    m = TOK.match
    while pos < n:
        mo = m(text, pos)
        if not mo:
            raise ValueError('bad char at %d: %r' % (pos, text[pos:pos + 20]))
        k = mo.lastgroup
        v = mo.group(k)
        pos = mo.end()
        if k == 'ws':
            continue
        if k == 'str':
            toks.append(('s', unq(v)))
        elif k == 'num':
            if v.lower().startswith(('0x', '-0x')):
                toks.append(('n', int(v, 16)))
            elif re.fullmatch(r'-?\d+', v):
                toks.append(('n', int(v)))
            else:
                toks.append(('n', float(v)))
        elif k == 'name':
            if v == 'true':
                toks.append(('v', True))
            elif v == 'false':
                toks.append(('v', False))
            elif v == 'nil':
                toks.append(('v', None))
            else:
                toks.append(('id', v))
        else:
            toks.append(('p', v))
    return toks


class P:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def nxt(self):
        x = self.t[self.i]
        self.i += 1
        return x

    def value(self):
        k, v = self.nxt()
        if k in ('s', 'n', 'v'):
            return v
        if k == 'p' and v == '{':
            return self.table()
        if k == 'p' and v == '-':
            raise ValueError
        raise ValueError('unexpected %r %r at %d' % (k, v, self.i))

    def table(self):
        d = {}
        arr = 1
        while True:
            k, v = self.peek()
            if k == 'p' and v == '}':
                self.i += 1
                return d
            if k == 'p' and v == '[':
                self.i += 1
                key = self.value()
                assert self.nxt() == ('p', ']')
                assert self.nxt() == ('p', '=')
                d[key] = self.value()
            elif k == 'id' and self.t[self.i + 1] == ('p', '='):
                self.i += 2
                d[v] = self.value()
            else:
                d[arr] = self.value()
                arr += 1
            k, v = self.peek()
            if k == 'p' and v in (',', ';'):
                self.i += 1


def parse_sv(text):
    toks = tokenize(text)
    p = P(toks)
    out = {}
    while p.i < len(toks):
        k, name = p.nxt()
        assert k == 'id', (k, name)
        assert p.nxt() == ('p', '=')
        out[name] = p.value()
    return out
