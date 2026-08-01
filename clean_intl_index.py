#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

path = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn\index.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

replacements = [
    # Badge labels
    ("Floor · Survival Right", "Mutual Aid · Survival Right"),
    ("Engine · Development Right", "Contribution · Development Right"),
    ("Ceiling · Accountability", "Accountability · Repair"),
    # SVG text
    ("Co-Creation / Floor-Maximalism", "Co-Creation / Mutual Aid"),
    # Section headings
    ("Do the math: the floor is actually cheap", "Do the math: the baseline is actually cheap"),
    ("\"cash floor\"", "\"cash baseline\""),
    ("Cash floor", "Cash baseline"),
    # Text snippets
    ("verifiable floor", "verifiable baseline"),
    ("UCV (floor)", "UCV (mutual aid)"),
    ("CV (engine) — incentives zone", "CV (contribution) — incentives zone"),
    ("NCV (ceiling) — accountability", "NCV (accountability) — repair zone"),
    ("floor → engine → resilience → brightness → ceiling", "mutual aid → contribution → resilience → brightness → accountability"),
    ("NCV accountability ceiling", "NCV accountability mechanism"),
    ('nobody has a "ceiling"', 'nobody has "accountability"'),
    ("Yes (NCV ceiling)", "Yes (NCV accountability)"),
]

orig = text
for old, new in replacements:
    text = text.replace(old, new)

if text != orig:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("FIXED", path)
else:
    print("NOCHG", path)
