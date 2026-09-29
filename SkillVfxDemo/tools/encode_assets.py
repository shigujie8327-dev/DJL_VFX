"""Encodes the stage, character masters, skill icons, sprite VFX textures and skill sounds of the Cocos
project into build/assets.js (window.ASSETS) as data URIs, downscaled to web sizes.
Usage: python tools/encode_assets.py <path to DouJiangLuV2>     (needs Pillow; ffmpeg for .wav sounds)"""
import base64, glob, io, json, os, subprocess, sys
from PIL import Image

project = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('DJL_PROJECT')
if not project:
    sys.exit('usage: python tools/encode_assets.py <DouJiangLuV2 project path>')
RES = os.path.join(project, 'assets', 'resources')
V3 = os.path.join(RES, 'battle-ui-2', 'v3')
SFX = os.path.join(RES, 'battle-ui-2', 'sfx')
HEROES = ['huarong', 'linchong', 'luzhishen', 'wusong', 'husanniang', 'wuyong']

def webp(im, q=82):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=3)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def key(path, base):
    return os.path.relpath(path, base).replace(os.sep, '/').rsplit('.', 1)[0]

out = {'img': {}, 'tex': {}, 'sfx': {}}
out['img']['bg'] = webp(Image.open(os.path.join(V3, 'battle', 'backgrounds', 'battle_stage_master.png')).convert('RGB').crop((0, 0, 1920, 780)), 78)
for h in HEROES:
    im = Image.open(os.path.join(V3, 'characters', h, f'{h}_battle_master.png')).resize((1024, 1024), Image.BILINEAR)
    out['img']['ch_' + h] = webp(im, 84)
for f in glob.glob(os.path.join(V3, 'ui', 'icons', '*', '*.png')):
    hero = os.path.basename(os.path.dirname(f)); name = os.path.splitext(os.path.basename(f))[0]
    out['img'][f'ic_{hero}_{name}'] = webp(Image.open(f), 88)
# Sprite VFX textures, keyed by their resources path (what the VFX libraries reference).
for f in glob.glob(os.path.join(RES, 'Characters', '**', '*.png'), recursive=True):
    im = Image.open(f); w, h = im.size; s = min(1.0, 1024 / max(w, h))
    if s < 1: im = im.resize((round(w * s), round(h * s)), Image.BILINEAR)
    out['tex'][key(f, RES)] = webp(im, 82)
for f in glob.glob(os.path.join(SFX, '**', '*.*'), recursive=True):
    if f.endswith('.mp3'): data = open(f, 'rb').read()
    elif f.endswith('.wav'): data = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-b:a', '96k', '-f', 'mp3', '-'], capture_output=True, check=True).stdout
    else: continue
    out['sfx'][key(f, SFX)] = 'data:audio/mpeg;base64,' + base64.b64encode(data).decode()

root = os.path.join(os.path.dirname(__file__), '..')
os.makedirs(os.path.join(root, 'build'), exist_ok=True)
with open(os.path.join(root, 'build', 'assets.js'), 'w', encoding='utf-8') as fh:
    fh.write('window.ASSETS=' + json.dumps(out) + ';\n')
for k in out: print(k, len(out[k]), sum(len(v) for v in out[k].values()) // 1024, 'KB')
