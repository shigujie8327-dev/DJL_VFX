// Minimal Cocos Creator 3.x runtime shim for the battle VFX: a tiny scene graph whose Graphics records
// draw commands and whose Sprite draws an image, both rendered onto one Canvas 2D in the stage's Y-up space.
'use strict';
const _decorator = { ccclass: () => (ctor) => ctor, property: () => () => {} };

class Color {
  constructor(r = 255, g = 255, b = 255, a = 255) { this.r = r; this.g = g; this.b = b; this.a = a; }
  set(r, g, b, a) { if (typeof r === 'object') { this.r = r.r; this.g = r.g; this.b = r.b; this.a = r.a; return this; } this.r = r; this.g = g; this.b = b; this.a = a ?? 255; return this; }
  clone() { return new Color(this.r, this.g, this.b, this.a); }
}
const css = (c) => `rgba(${c.r | 0},${c.g | 0},${c.b | 0},${(c.a ?? 255) / 255})`;

class Vec3 {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
  clone() { return new Vec3(this.x, this.y, this.z); }
  set(x, y, z) { if (typeof x === 'object') { this.x = x.x; this.y = x.y; this.z = x.z; } else { this.x = x; this.y = y; this.z = z ?? 0; } return this; }
}
const math = { clamp: (v, a, b) => (v < a ? a : v > b ? b : v) };

class Node {
  constructor(name = '') {
    this.name = name; this.children = []; this.parent = null; this._components = [];
    this._pos = new Vec3(); this._scale = new Vec3(1, 1, 1); this.angle = 0; this.layer = 0; this.isValid = true; this.active = true;
  }
  get position() { return this._pos; }
  get scale() { return this._scale; }
  setPosition(x, y, z) { if (typeof x === 'object') this._pos.set(x.x, x.y, x.z); else this._pos.set(x, y ?? 0, z ?? 0); }
  setScale(x, y, z) { if (typeof x === 'object') this._scale.set(x.x, x.y, x.z); else this._scale.set(x, y ?? x, z ?? 1); }
  addChild(n) { if (n.parent) n.removeFromParent(); n.parent = this; this.children.push(n); }
  removeFromParent() { if (!this.parent) return; const i = this.parent.children.indexOf(this); if (i >= 0) this.parent.children.splice(i, 1); this.parent = null; }
  setSiblingIndex(i) { const p = this.parent; if (!p) return; p.children.splice(p.children.indexOf(this), 1); p.children.splice(i, 0, this); }
  addComponent(Ctor) { const c = new Ctor(); c.node = this; this._components.push(c); c.__onAdd?.(); return c; }
  getComponent(Ctor) { return this._components.find((c) => c instanceof Ctor) || null; }
  destroy() {
    if (!this.isValid) return;
    this.isValid = false;
    for (const ch of [...this.children]) ch.destroy();
    for (const c of this._components) c.onDestroy?.();
    this.removeFromParent();
  }
  emit() {}
  on() {}
}

class Component {
  get isValid() { return !!this.node && this.node.isValid; }
  getComponent(C) { return this.node.getComponent(C); }
  addComponent(C) { return this.node.addComponent(C); }
}

class UITransform extends Component {
  constructor() { super(); this.width = 100; this.height = 100; this.anchorX = 0.5; this.anchorY = 0.5; }
  setContentSize(w, h) { if (typeof w === 'object') { this.width = w.width; this.height = w.height; } else { this.width = w; this.height = h; } }
  setAnchorPoint(x, y) { if (typeof x === 'object') { this.anchorX = x.x; this.anchorY = x.y; } else { this.anchorX = x; this.anchorY = y; } }
  get contentSize() { return { width: this.width, height: this.height }; }
}

// Graphics: records ops between clear() calls, replayed at render time. Mirrors Cocos path semantics:
// after fill()/stroke(), the next moveTo (or shape) starts a new path; fill then stroke reuses the same path.
class Graphics extends Component {
  constructor() { super(); this.ops = []; this._lw = 1; this._lineCap = 'round'; this._lineJoin = 'round'; }
  set lineWidth(v) { this._lw = v; this.ops.push(['lw', v]); }
  get lineWidth() { return this._lw; }
  set strokeColor(c) { this.ops.push(['ss', css(c)]); }
  set fillColor(c) { this.ops.push(['fs', css(c)]); }
  set lineCap(v) { this._lineCap = v; }
  set lineJoin(v) { this._lineJoin = v; }
  clear() { this.ops.length = 0; this.ops.push(['lw', this._lw]); }
  moveTo(x, y) { this.ops.push(['m', x, y]); }
  lineTo(x, y) { this.ops.push(['l', x, y]); }
  bezierCurveTo(a, b, c, d, e, f) { this.ops.push(['b', a, b, c, d, e, f]); }
  quadraticCurveTo(a, b, c, d) { this.ops.push(['q', a, b, c, d]); }
  arc(cx, cy, r, a0, a1, ccw) { this.ops.push(['arc', cx, cy, r, a0, a1, !ccw]); }
  circle(x, y, r) { this.ops.push(['ell', x, y, r, r]); }
  ellipse(x, y, rx, ry) { this.ops.push(['ell', x, y, rx, ry]); }
  rect(x, y, w, h) { this.ops.push(['rect', x, y, w, h]); }
  roundRect(x, y, w, h) { this.ops.push(['rect', x, y, w, h]); }
  close() { this.ops.push(['z']); }
  fill() { this.ops.push(['F']); }
  stroke() { this.ops.push(['S']); }
  __render(ctx) {
    let fresh = true;
    const begin = () => { if (fresh) { ctx.beginPath(); fresh = false; } };
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (const o of this.ops) {
      switch (o[0]) {
        case 'lw': ctx.lineWidth = o[1]; break;
        case 'ss': ctx.strokeStyle = o[1]; break;
        case 'fs': ctx.fillStyle = o[1]; break;
        case 'm': begin(); ctx.moveTo(o[1], o[2]); break;
        case 'l': ctx.lineTo(o[1], o[2]); break;
        case 'b': ctx.bezierCurveTo(o[1], o[2], o[3], o[4], o[5], o[6]); break;
        case 'q': ctx.quadraticCurveTo(o[1], o[2], o[3], o[4]); break;
        case 'arc': begin(); ctx.arc(o[1], o[2], o[3], o[4], o[5], o[6]); break;
        case 'ell': begin(); ctx.moveTo(o[1] + o[3], o[2]); ctx.ellipse(o[1], o[2], Math.max(0, o[3]), Math.max(0, o[4]), 0, 0, Math.PI * 2); ctx.closePath(); break;
        case 'rect': begin(); ctx.rect(o[1], o[2], o[3], o[4]); break;
        case 'z': ctx.closePath(); break;
        case 'F': ctx.fill(); fresh = true; break;
        case 'S': ctx.stroke(); fresh = true; break;
      }
    }
  }
}
Graphics.LineCap = { BUTT: 0, ROUND: 1, SQUARE: 2 };
Graphics.LineJoin = { BEVEL: 0, ROUND: 1, MITER: 2 };

class Texture2D { constructor(img) { this.image = img || null; this.isValid = true; } }
class SpriteFrame { constructor() { this.texture = null; this.isValid = true; } }
class Sprite extends Component {
  constructor() { super(); this.spriteFrame = null; this._color = new Color(); this.sizeMode = 0; this.trim = true; this.type = 0; this.fillType = 0; this.fillStart = 0; this.fillRange = 1; }
  set color(c) { this._color.set(c.r, c.g, c.b, c.a); }
  get color() { return this._color; }
  __render(ctx) {
    const img = this.spriteFrame?.texture?.image;
    if (!img || this._color.a <= 0) return;
    const ui = this.node.getComponent(UITransform);
    const w = ui ? ui.width : img.width, h = ui ? ui.height : img.height;
    const ax = ui ? ui.anchorX : 0.5, ay = ui ? ui.anchorY : 0.5;
    ctx.globalAlpha = this._color.a / 255;
    ctx.scale(1, -1);
    const x0 = -ax * w, y0 = -(1 - ay) * h;
    if (this.type === Sprite.Type.FILLED) {
      const r = Math.max(0, Math.min(1, this.fillRange));
      if (r > 0.001) ctx.drawImage(img, 0, 0, img.width * r, img.height, x0, y0, w * r, h);
    } else ctx.drawImage(img, x0, y0, w, h);
    ctx.globalAlpha = 1;
  }
}
Sprite.SizeMode = { CUSTOM: 0, TRIMMED: 1, RAW: 2 };
Sprite.Type = { SIMPLE: 0, SLICED: 1, TILED: 2, FILLED: 3 };
Sprite.FillType = { HORIZONTAL: 0, VERTICAL: 1, RADIAL: 2 };

// Audio: the demo installs the output via cc.__audio.
class AudioClip { constructor(key) { this.key = key; } }
class AudioSource extends Component {
  constructor() { super(); this.clip = null; this.loop = false; this.volume = 1; this._h = null; }
  playOneShot(clip, vol) { cc.__audio?.(clip.key, vol); }
  play() { this.stop(); if (this.clip) this._h = cc.__audioLoop?.(this.clip.key, this.volume, this.loop) ?? null; }
  stop() { if (this._h) { this._h.stop(); this._h = null; } }
}

const resources = {
  load(path, Type, cb) {
    const r = cc.__resolve?.(path, Type);
    setTimeout(() => (r ? cb(null, r) : cb(new Error('missing ' + path), null)), 0);
  },
};

// Walk the tree: update every component, then render in sibling order.
function updateTree(node, dt) {
  if (!node.isValid) return;
  for (const c of [...node._components]) if (c.update && node.isValid) c.update(dt);
  for (const ch of [...node.children]) updateTree(ch, dt);
}
function renderTree(node, ctx) {
  if (!node.isValid || !node.active) return;
  ctx.save();
  ctx.translate(node._pos.x, node._pos.y);
  if (node.angle) ctx.rotate(node.angle * Math.PI / 180);
  if (node._scale.x !== 1 || node._scale.y !== 1) ctx.scale(node._scale.x, node._scale.y);
  for (const c of node._components) if (c.__render) { ctx.save(); c.__render(ctx); ctx.restore(); }
  for (const ch of node.children) renderTree(ch, ctx);
  ctx.restore();
}

const cc = { _decorator, Color, Vec3, math, Node, Component, UITransform, Graphics, Sprite, SpriteFrame, Texture2D, AudioClip, AudioSource, resources, updateTree, renderTree, __resolve: null, __audio: null };
module.exports = cc;
