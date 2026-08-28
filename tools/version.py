#!/usr/bin/env python3
"""Version helpers for Bare Browser Android builds."""

import os
import sys

BASE = 800000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The last digit of the versionCode, mirroring Chromium's own assignment so a
# 64-bit device always sees the 64-bit APK as the newer of the two and Android
# refuses to replace it with the 32-bit one.
ABI_DIGITS = {"arm": 0, "arm64": 5}


def read():
    v = {}
    with open(os.path.join(ROOT, "VERSION")) as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, _, val = line.partition("=")
                v[k.strip()] = val.strip()
    return v


def version_code(v, abi):
    # BUILD sits in the tens so the ABI digit gets the ones. That caps BUILD
    # at 9; the assert keeps a tenth rebuild from silently colliding with the
    # next PATCH level.
    assert int(v["BUILD"]) <= 9, "BUILD only has one digit now"
    code = (BASE
            + int(v["MAJOR"]) * 1000000
            + int(v["MINOR"]) * 10000
            + int(v["PATCH"]) * 100
            + int(v["BUILD"]) * 10
            + ABI_DIGITS[abi])
    assert code < 2100000000, "versionCode past Android's ceiling"
    return code


def version_name(v):
    name = "%s.%s.%s" % (v["MAJOR"], v["MINOR"], v["PATCH"])
    if v["CHANNEL"] != "stable":
        name += "-%s.%s" % (v["CHANNEL"], v["CHANNEL_NUM"])
    return name


def tag(v):
    return "v" + version_name(v)


def need_abi(argv, position):
    # code and gn are per-ABI on purpose: with no default there is no way to
    # emit a number that does not say which APK it belongs to.
    if len(argv) <= position or argv[position] not in ABI_DIGITS:
        sys.exit("usage: version.py %s {arm|arm64}" % argv[position - 1])
    return argv[position]


if __name__ == "__main__":
    v = read()
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what == "code":
        print(version_code(v, need_abi(sys.argv, 2)))
    elif what == "name":
        print(version_name(v))
    elif what == "tag":
        print(tag(v))
    elif what == "gn":
        # Paste into args.gn. Both are plain declare_args in
        # build/config/android/config.gni, so no patch is needed to use them.
        abi = need_abi(sys.argv, 2)
        print('android_override_version_code = "%d"' % version_code(v, abi))
        print('android_override_version_name = "%s"' % version_name(v))
    else:
        print("versionName %s" % version_name(v))
        for abi in ("arm", "arm64"):
            print("versionCode %d  (%s)" % (version_code(v, abi), abi))
        print("tag         %s" % tag(v))
