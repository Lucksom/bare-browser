#!/usr/bin/env python3
"""Compare APK contents while ignoring signing metadata.

Usage:
    tools/apk-content-hash.py app1.apk app2.apk
"""

import hashlib
import sys
import zipfile


def content_hash(path):
    h = hashlib.sha256()
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            # The v1 signature lives in META-INF. The v2/v3 blocks live outside
            # the zip structure entirely, between the entries and the central
            # directory, so reading entries never sees them.
            if name.startswith("META-INF/"):
                continue
            h.update(name.encode("utf-8"))
            h.update(b"\0")
            h.update(z.read(name))
    return h.hexdigest()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    results = [(p, content_hash(p)) for p in sys.argv[1:]]
    for path, digest in results:
        print("%s  %s" % (digest, path))
    if len(results) > 1:
        same = len({d for _, d in results}) == 1
        print()
        print("identical contents" if same else "CONTENTS DIFFER")
        sys.exit(0 if same else 1)
