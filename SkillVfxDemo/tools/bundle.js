// Transpiles the Cocos project's VFX TypeScript (SkillVfxRegistry and everything it imports) into one
// browser script (build/djl-vfx.js) that exposes window.DJL. 'cc' resolves to src/cc-shim.js at runtime.
// Usage: node tools/bundle.js <path to DouJiangLuV2>
const fs = require('fs'), path = require('path');
let ts;
try { ts = require('typescript'); } catch (e) { ts = require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'typescript')); }
const PROJECT = process.argv[2] || process.env.DJL_PROJECT;
if (!PROJECT) { console.error('usage: node tools/bundle.js <DouJiangLuV2 project path>'); process.exit(1); }
const SCRIPTS = path.join(PROJECT, 'assets', 'scripts');
const UI2 = path.join(SCRIPTS, 'cocos', 'presentation', 'battle-ui-2');
const ROOT = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(p, 'utf8');
const files = {
  entry: read(path.join(ROOT, 'src', 'entry.ts')),
  // battle-core domain types are only needed for the character data; tiny stand-ins keep the bundle presentation-only.
  'domain/CharacterDefinition': 'export const createCharacterDefinition = (d: any) => d;',
  'domain/BattleEnums': "export const SkillRange = { NEAR: 'NEAR', FAR: 'FAR', ANY: 'ANY' } as const;",
  'domain/SkillDefinition': 'export {};',
  'characters/definitions': read(path.join(SCRIPTS, 'battle-core', 'characters', 'definitions.ts')),
  'characters/balanceConfig': read(path.join(SCRIPTS, 'battle-core', 'characters', 'balanceConfig.ts')),
  BattleScene2PresentationConfig: read(path.join(UI2, 'BattleScene2PresentationConfig.ts')),
};
for (const dir of ['vfx', 'sfx']) for (const f of fs.readdirSync(path.join(UI2, dir))) if (f.endsWith('.ts')) files[`${dir}/${f.slice(0, -3)}`] = read(path.join(UI2, dir, f));
let out = '(function(){\nconst __defs = {};\n';
for (const [id, src] of Object.entries(files)) {
  const js = ts.transpileModule(src, { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS, experimentalDecorators: true, useDefineForClassFields: false } }).outputText;
  out += `__defs[${JSON.stringify(id)}] = function(module, exports, require){\n${js}\n};\n`;
}
out += `const __cache = {};
function __norm(parts) { const o = []; for (const p of parts) { if (p === '.' || p === '') continue; if (p === '..') o.pop(); else o.push(p); } return o.join('/'); }
function __req(from, spec) {
  if (spec === 'cc') return window.cc;
  const id = spec.startsWith('.') ? __norm(from.split('/').slice(0, -1).concat(spec.split('/'))) : spec;
  if (!__defs[id]) throw new Error('module not found: ' + spec + ' from ' + from);
  if (__cache[id]) return __cache[id].exports;
  const m = { exports: {} }; __cache[id] = m;
  __defs[id](m, m.exports, (s) => __req(id, s));
  return m.exports;
}
window.DJL = __req('', './entry');
})();\n`;
fs.mkdirSync(path.join(ROOT, 'build'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'build', 'djl-vfx.js'), out);
console.log(`bundled ${Object.keys(files).length} modules, ${out.length} bytes`);
