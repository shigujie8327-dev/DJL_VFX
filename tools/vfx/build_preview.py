"""Inline the Linchong VFX manifest into the preview page.

Writes LC_VFX_Preview.html at the repo root (open directly in a browser, works from file://).
With --artifact PATH also writes a skeleton-less copy for publishing as a hosted page.
"""
import argparse
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def build(artifact=None):
    with open(os.path.join(ROOT, 'Characters', 'Linchong', 'LC_VFX_Manifest.json'), encoding='utf-8') as f:
        manifest = json.load(f)
    with open(os.path.join(os.path.dirname(__file__), 'preview_template.html'), encoding='utf-8') as f:
        tpl = f.read()
    body = tpl.replace('/*MANIFEST*/null', json.dumps(manifest, ensure_ascii=False, separators=(',', ':')))
    page = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + body + '\n</html>\n')
    out = os.path.join(ROOT, 'LC_VFX_Preview.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    print('wrote', out)
    if artifact:
        with open(artifact, 'w', encoding='utf-8') as f:
            f.write(body)
        print('wrote', artifact)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact')
    build(ap.parse_args().artifact)
