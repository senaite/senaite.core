#!/usr/bin/env python
#
# Scans the doctests folder and generates the doctests.rst file

import os
from os import listdir

DOCTESTS_DIR = "../src/senaite/core/tests/doctests"

REPLACEMENTS = (
    ("=", "-"),
    ("-", "."),
    (".", "~"),
)


def is_header_marker(line, wildcard=None):
    if not wildcard:
        markers = dict(REPLACEMENTS).keys()
        markers = map(lambda r: r*2, markers)
    else:
        markers = [wildcard,]
    if not line or len(line) < 2:
        return
    return line[0:2] in markers


def rewrite_doctest(doctest_file):
    replacements = dict(REPLACEMENTS)
    with open(doctest_file, "r") as f:
        lines = f.readlines()

    replace = False
    output = []
    for line in lines:
        if not line:
            continue

        if is_header_marker(line, "=="):
            replace = True
            if not output:
                continue

        if replace and is_header_marker(line):
            replace_by = replacements.get(line[0])
            line = line.replace(line[0], replace_by)

        output.append(line)

    if output:
        with open(doctest_file, "w") as f:
            f.writelines(output)


if __name__ == "__main__":

    files = listdir(DOCTESTS_DIR)
    rst_files = filter(lambda f: os.path.splitext(f)[-1] == ".rst", files)

    # Sort them alphabetically
    rst_files = sorted(rst_files)

    # Re-write them (replace header markers)
    rst_files = map(lambda f: "/".join([DOCTESTS_DIR, f]), rst_files)
    map(rewrite_doctest, rst_files)

    # Generate the list
    lines = map(lambda f: ".. include:: {}".format(f), rst_files)

    # Write the doctests.rst
    with open("doctests.rst", "w") as out_file:
        out_file.write("Doctests\n========\n\n")
        out_file.write("\n".join(lines))
        out_file.write("\n")
