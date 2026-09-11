import zipfile, os
D = r"D:\ascension data till 10-9 11 am"
ZIPS = ["Account.zip", "Account (1).zip", "Account (2).zip", "wtf.zip"]


def redact(p):
    parts = p.replace(chr(92), '/').split('/')
    low = [s.lower() for s in parts]
    i = None
    for k, s in enumerate(low):
        if s == 'account':
            i = k
            break
    if i is None:
        return p
    out = list(parts)
    if i + 1 < len(out):
        out[i + 1] = '<acct>'
    # Account/<acct>/SavedVariables/...  or Account/<acct>/<realm>/<char>/...
    if i + 2 < len(out) and low[i + 2] != 'savedvariables':
        if i + 3 < len(out) - 1:
            out[i + 3] = '<char>'
    return '/'.join(out)


def lc_members():
    """yield (zipname, redacted_path, account_index, raw_bytes)"""
    for z in ZIPS:
        zf = zipfile.ZipFile(os.path.join(D, z))
        accts = {}
        for n in zf.infolist():
            if 'lootcollector' in n.filename.lower() and not n.is_dir():
                parts = n.filename.replace(chr(92), '/').split('/')
                low = [s.lower() for s in parts]
                ak = None
                if 'account' in low:
                    ai = low.index('account')
                    ak = parts[ai + 1] if ai + 1 < len(parts) else None
                if ak not in accts:
                    accts[ak] = len(accts)
                yield z, redact(n.filename), accts[ak], n.file_size, zf.read(n)
