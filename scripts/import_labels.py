#!/usr/bin/env python3
"""
Import labels from .github/labels.yml into the current repository using the GitHub CLI (`gh`).

Usage:
  python3 scripts/import_labels.py

Requirements:
- `gh` must be installed and authenticated (run `gh auth login` first).

This script is intentionally tiny and uses a simple YAML-ish parser
that works with the labels format we keep in `.github/labels.yml`.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LABELS_PATH = os.path.join(ROOT, '.github', 'labels.yml')

def read_labels(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    labels = []
    name = None
    color = None
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            m = re.match(r'^\s*-\s*name:\s*(.+)$', line)
            if m:
                if name:
                    labels.append({'name': name, 'color': color})
                name = m.group(1).strip().strip('"').strip("'")
                color = None
                continue
            m2 = re.match(r'^\s*color:\s*([0-9a-fA-F]{3,6})\s*$', line)
            if m2 and name:
                color = m2.group(1).strip().lstrip('#')
    if name:
        labels.append({'name': name, 'color': color})
    return labels

def gh_available():
    return subprocess.run(['gh', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def main():
    if not gh_available():
        print('gh CLI not found. Install from https://cli.github.com/', file=sys.stderr)
        sys.exit(2)
    try:
        labels = read_labels(LABELS_PATH)
    except FileNotFoundError:
        print(f'Could not find {LABELS_PATH}', file=sys.stderr)
        sys.exit(1)

    if not labels:
        print('No labels found in labels.yml')
        return

    created = 0
    updated = 0
    failed = 0

    for lbl in labels:
        name = lbl['name']
        color = (lbl.get('color') or 'ffffff').lstrip('#')
        # try create
        print(f'Processing label: {name} (#{color})')
        res = run(['gh', 'label', 'create', name, '--color', color])
        if res.returncode == 0:
            print(f'  created: {name}')
            created += 1
            continue
        # if create failed, try edit
        res2 = run(['gh', 'label', 'edit', name, '--color', color])
        if res2.returncode == 0:
            print(f'  updated: {name}')
            updated += 1
        else:
            print(f'  failed: {name}\n    create stderr: {res.stderr.strip()}\n    edit stderr: {res2.stderr.strip()}', file=sys.stderr)
            failed += 1

    print('\nSummary:')
    print(f'  created: {created}')
    print(f'  updated: {updated}')
    print(f'  failed:  {failed}')

if __name__ == '__main__':
    main()
