#!/usr/bin/env python3
"""
Import labels from .github/labels.yml using the GitHub REST API.

Requires a token in the environment: `GITHUB_TOKEN` or `GH_TOKEN` with repo permissions.

Usage:
  export GITHUB_TOKEN=ghp_...
  python3 scripts/import_labels_api.py
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LABELS_PATH = os.path.join(ROOT, '.github', 'labels.yml')

def read_labels(path):
    labels = []
    if not os.path.exists(path):
        raise FileNotFoundError(path)
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
    # normalize colors to 6-digit hex
    for lbl in labels:
        c = lbl.get('color') or 'ffffff'
        if len(c) == 3:
            c = ''.join(ch*2 for ch in c)
        lbl['color'] = c.lower()
    return labels

def get_repo():
    # try git remote
    try:
        import subprocess
        url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], text=True).strip()
    except Exception:
        url = os.environ.get('GIT_REMOTE_URL')
    if not url:
        raise RuntimeError('Could not determine remote origin URL. Set GIT_REMOTE_URL env var.')
    # parse formats: git@github.com:owner/repo.git or https://github.com/owner/repo.git
    if url.startswith('git@'):
        m = re.match(r'git@[^:]+:([^/]+)/(.+?)(?:\.git)?$', url)
        if m:
            return m.group(1), m.group(2)
    else:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lstrip('/')
        if path.endswith('.git'):
            path = path[:-4]
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
    raise RuntimeError(f'Unable to parse repo from URL: {url}')

def api_request(method, url, token, data=None):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'import-labels-script'
    }
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.load(resp)
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode('utf-8')
            return e.code, json.loads(err)
        except Exception:
            return e.code, {'message': str(e)}

def main():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print('Set GITHUB_TOKEN or GH_TOKEN in the environment (repo scope).', file=sys.stderr)
        sys.exit(2)

    owner, repo = get_repo()
    base = f'https://api.github.com/repos/{owner}/{repo}'

    labels = read_labels(LABELS_PATH)
    if not labels:
        print('No labels found to import.')
        return

    # fetch existing labels
    code, existing = api_request('GET', base + '/labels?per_page=100', token)
    if code != 200:
        print('Failed to fetch existing labels:', existing, file=sys.stderr)
        sys.exit(1)
    existing_map = {lbl['name']: lbl for lbl in existing}

    created = 0
    updated = 0
    failed = 0

    for lbl in labels:
        name = lbl['name']
        color = lbl['color']
        if name in existing_map:
            url = base + '/labels/' + urllib.parse.quote(name, safe='')
            code, body = api_request('PATCH', url, token, {'new_name': name, 'color': color})
            if 200 <= code < 300:
                print(f'updated: {name} (#{color})')
                updated += 1
            else:
                print(f'failed update {name}:', body, file=sys.stderr)
                failed += 1
        else:
            code, body = api_request('POST', base + '/labels', token, {'name': name, 'color': color})
            if 200 <= code < 300:
                print(f'created: {name} (#{color})')
                created += 1
            else:
                print(f'failed create {name}:', body, file=sys.stderr)
                failed += 1

    print('\nSummary:')
    print(f'  created: {created}')
    print(f'  updated: {updated}')
    print(f'  failed:  {failed}')

if __name__ == '__main__':
    main()
