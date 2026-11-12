#!/usr/bin/env python3
"""Check this recipe's pin: kindling.json's engine field and compose.yaml's image name the same gr8 image, by digest.

  python3 check.py        exit 0 when they agree, 1 with the reason when not
"""
import json
import re
import sys

k = json.load(open('kindling.json'))
e = k.get('engine') or {}
bad = []
for f in ('repo', 'ref', 'commit', 'pin', 'image', 'image_digest'):
    if not e.get(f):
        bad.append(f'kindling.json engine.{f} is missing')
if e.get('commit') and not re.fullmatch(r'[0-9a-f]{40}', e['commit']):
    bad.append('engine.commit is not a full commit hash')
if e.get('ref') and not re.fullmatch(r'v\d+\.\d+(\.\d+)?|stable|main', e['ref']):
    bad.append('engine.ref is not a release tag, stable or main')
m = re.search(r'image: \$\{GR8_IMAGE:-([^}\s]+)\}', open('compose.yaml').read())
want = f"{e.get('image')}@{e.get('image_digest')}"
if not m:
    bad.append('compose.yaml has no pinned default image')
elif m.group(1) != want:
    bad.append(f'compose.yaml pins {m.group(1)}, kindling.json says {want}')
ids = [c['id'] for c in k['configs']]
if k.get('default_config') not in ids:
    bad.append('default_config names no config')
for b in bad:
    print('check: ' + b, file=sys.stderr)
print(f"check: {'FAIL' if bad else 'ok'}: engine {e.get('ref')} {str(e.get('commit'))[:7]}, {len(ids)} config(s)")
sys.exit(1 if bad else 0)
