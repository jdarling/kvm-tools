import re
import sys
from itertools import product


def split_respecting_braces(s):
    """Split string on commas, but respect brace boundaries"""
    segments = []
    current = ""
    brace_count = 0

    for char in s:
        if char == "{":
            brace_count += 1
            current += char
        elif char == "}":
            brace_count -= 1
            current += char
        elif char == "," and brace_count == 0:
            # Only split on commas outside of braces
            segments.append(current.strip())
            current = ""
        else:
            current += char

    # Add the last segment
    if current.strip():
        segments.append(current.strip())

    return segments


def expand_braces(s):
    # Find all {...} patterns
    brace_pattern = re.compile(r"\{([^{}]+)\}")
    m = brace_pattern.search(s)
    if not m:
        return [s]
    pre = s[: m.start()]
    post = s[m.end() :]
    items = []
    # Split items and strip whitespace so patterns like '{1,  3}' don't keep spaces
    for part in m.group(1).split(","):
        part = part.strip()
        if ".." in part:
            start, end = [p.strip() for p in part.split("..")]
            items.extend(str(i) for i in range(int(start), int(end) + 1))
        else:
            items.append(part)
    results = []
    for item in items:
        for rest in expand_braces(post):
            results.append(pre + item + rest)
    return results


ips = []
for segment in split_respecting_braces(sys.argv[1]):
    ips.extend(expand_braces(segment))
for ip in ips:
    print(ip)
