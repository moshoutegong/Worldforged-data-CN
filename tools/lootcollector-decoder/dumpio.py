"""Shared, privacy-safe read access to the Discord dump. NOTHING is extracted to disk.

redact()     masks account and character path segments in every layout seen in the dump
             (WTF/Account/<acct>/..., <realm>/<char>/..., archives rooted at <acct>/ or <char>/).
is_archive() .zip / .rar / .7z / .tar / .tar.gz / .tgz
members()    lists archive members (files only) in archive INDEX order with their sizes.
stream()     yields (path, bytes) per member. For 7-Zip archives one `7z e -so` run emits every member
             back-to-back in index order; the stream is split on the listed sizes and the grand total
             is checked, so a mismatch fails loudly instead of mis-attributing bytes to the wrong file.
7-Zip's stderr can contain member paths (names), so it is never printed.
"""
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

ROOT = r"D:\ascension data till 10-9 11 am"
SEVEN = next((p for p in (r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe",
                          shutil.which("7z") or "") if p and os.path.exists(p)), None)
ARCHIVE_EXT = (".zip", ".rar", ".7z", ".tar", ".tar.gz", ".tgz")

REALM = re.compile(r".+ - .+")                      # "<Server> - <Mode>", a server not a person
CHAR_CHILDREN = {"savedvariables", "addons.txt", "chat-cache.txt", "chat-cache.old", "macros-cache.txt",
                 "macros-cache.old", "layout-local.txt", "layout-local.old", "layout-cache.txt",
                 "bindings-cache.wtf", "bindings-cache.old", "config-cache.wtf", "config-cache.old"}
SAFE = {"wtf", "account", "interface", "addons", "wdb", "cache", "logs", "data",
        "enus", "engb", "dede", "frfr", "eses", "esmx", "ruru", "kokr", "zhcn", "zhtw", "ptbr"}


def redact(path):
    parts = re.split(r"[\\/]", path)
    out, n = list(parts), len(parts)
    for i, p in enumerate(parts):
        prev = parts[i - 1] if i else ""
        nxt = parts[i + 1] if i + 1 < n else None
        low = p.lower()
        if prev.lower() == "account" and nxt is not None:
            out[i] = "<acct>"                                   # WTF/Account/<acct>/...
        elif REALM.fullmatch(prev) and nxt is not None and low != "savedvariables":
            out[i] = "<char>"                                   # <realm>/<char>/...
        elif low in SAFE or REALM.fullmatch(p):
            continue
        elif nxt is not None and nxt.lower() in CHAR_CHILDREN:
            out[i] = "<char>"                                   # archive rooted at <char>/
        elif nxt is not None and REALM.fullmatch(nxt):
            out[i] = "<acct>"                                   # archive rooted at <acct>/<realm>/
    return "/".join(out)


for _raw, _want in (
        ("WTF/Account/ACCT1/SavedVariables/X.lua", "WTF/Account/<acct>/SavedVariables/X.lua"),
        ("Account/ACCT1/Vol'jin - Conquest of Azeroth/CHAR1/SavedVariables/D.lua",
         "Account/<acct>/Vol'jin - Conquest of Azeroth/<char>/SavedVariables/D.lua"),
        ("Vol'Jin - Conquest of Azeroth/CHAR1/SavedVariables/D.lua",
         "Vol'Jin - Conquest of Azeroth/<char>/SavedVariables/D.lua"),
        ("Rexxar - Conquest of Azeroth/CHAR1/chat-cache.txt", "Rexxar - Conquest of Azeroth/<char>/chat-cache.txt"),
        ("CHAR1/SavedVariables/D.lua", "<char>/SavedVariables/D.lua"),
        ("CHAR1/macros-cache.txt", "<char>/macros-cache.txt"),
        ("ACCT1/Vol'jin - Conquest of Azeroth/CHAR1/AddOns.txt",
         "<acct>/Vol'jin - Conquest of Azeroth/<char>/AddOns.txt"),
        ("WTF/Account/ACCT1/config-cache.wtf", "WTF/Account/<acct>/config-cache.wtf"),
        ("WDB/enUS/Rexxar - Conquest of Azeroth/itemcache.wdb", "WDB/enUS/Rexxar - Conquest of Azeroth/itemcache.wdb"),
        ("WDB/enUS/creaturecache.wdb", "WDB/enUS/creaturecache.wdb"),
        ("SavedVariables/LootCollector.lua", "SavedVariables/LootCollector.lua"),
        ("Interface/AddOns/Foo/Foo.toc", "Interface/AddOns/Foo/Foo.toc")):
    assert redact(_raw) == _want, ("redaction self-test failed", _want)


def is_archive(name):
    return name.lower().endswith(ARCHIVE_EXT)


def _kind(archive):
    low = archive.lower()
    if low.endswith(".zip"):
        return "zip"
    if low.endswith((".tar", ".tar.gz", ".tgz")):
        return "tar"
    return "7z"


def members(archive):
    kind = _kind(archive)
    if kind == "zip":
        with zipfile.ZipFile(archive) as z:
            return [(i.filename, i.file_size) for i in z.infolist() if not i.is_dir()]
    if kind == "tar":
        with tarfile.open(archive) as t:
            return [(m.name, m.size) for m in t.getmembers() if m.isfile()]
    if not SEVEN:
        raise RuntimeError("7-Zip not found")
    r = subprocess.run([SEVEN, "l", "-slt", "-ba", archive], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, stdin=subprocess.DEVNULL)
    items, cur = [], {}
    for line in r.stdout.splitlines() + [""]:
        if not line.strip():
            if "Path" in cur and cur.get("Folder") != "+" and "D" not in cur.get("Attributes", ""):
                items.append((cur["Path"], int(cur.get("Size") or 0)))
            cur = {}
            continue
        if " = " in line:
            k, v = line.split(" = ", 1)
            cur[k.strip()] = v.strip()
    return items


def stream(archive, want=None):
    """Yield (path, bytes) for every member, or only those `want(path)` accepts."""
    kind = _kind(archive)
    if kind == "zip":
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if not info.is_dir() and (want is None or want(info.filename)):
                    yield info.filename, z.read(info)
        return
    if kind == "tar":
        with tarfile.open(archive) as t:
            for m in t.getmembers():
                if m.isfile() and (want is None or want(m.name)):
                    yield m.name, t.extractfile(m).read()
        return
    mem = members(archive)
    if want is not None and not any(want(n) for n, _ in mem):
        return
    r = subprocess.run([SEVEN, "e", "-so", "-bd", archive], capture_output=True, timeout=1800,
                       stdin=subprocess.DEVNULL)
    total = sum(s for _, s in mem)
    if r.returncode != 0 or len(r.stdout) != total:
        raise RuntimeError(f"7z stream mismatch for {os.path.basename(archive)}: rc={r.returncode}, "
                           f"got {len(r.stdout):,} bytes, listing says {total:,}")
    off = 0
    for name, size in mem:
        chunk = r.stdout[off:off + size]
        off += size
        if want is None or want(name):
            yield name, chunk
