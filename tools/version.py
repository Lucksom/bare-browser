#!/usr/bin/env python3
"""Version helpers for Bare Browser Android builds."""

import os
import sys

BASE = 800000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read():
    v = {}
    with open(os.path.join(ROOT, "VERSION")) as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, _, val = line.partition("=")
                v[k.strip()] = val.strip()
    return v


def version_code(v):
    code = (BASE
            + int(v["MAJOR"]) * 1000000
            + int(v["MINOR"]) * 10000
            + int(v["PATCH"]) * 100
            + int(v["BUILD"]))
    assert code < 2100000000, "versionCode past Android's ceiling"
    return code


def version_name(v):
    name = "%s.%s.%s" % (v["MAJOR"], v["MINOR"], v["PATCH"])
    if v["CHANNEL"] != "stable":
        name += "-%s.%s" % (v["CHANNEL"], v["CHANNEL_NUM"])
    return name


def tag(v):
    return "v" + version_name(v)


if __name__ == "__main__":
    v = read()
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what == "code":
        print(version_code(v))
    elif what == "name":
        print(version_name(v))
    elif what == "tag":
        print(tag(v))
    elif what == "gn":
        # Paste into args.gn. Both are plain declare_args in
        # build/config/android/config.gni, so no patch is needed to use them.
        print('android_override_version_code = "%d"' % version_code(v))
        print('android_override_version_name = "%s"' % version_name(v))
    else:
        print("versionName %s" % version_name(v))
        print("versionCode %d" % version_code(v))
        print("tag         %s" % tag(v))
