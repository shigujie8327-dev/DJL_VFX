// Inlines src/cc-shim.js, build/djl-vfx.js and build/assets.js into src/template.html → dist/djl-skill-vfx.html.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const read = (...p) => fs.readFileSync(path.join(ROOT, ...p), 'utf8');
const shim = read('src', 'cc-shim.js').replace('module.exports = cc;', 'window.cc = cc;');
const html = read('src', 'template.html')
  .replace('/*__SHIM__*/', () => '(function(){' + shim + '})();')
  .replace('/*__BUNDLE__*/', () => read('build', 'djl-vfx.js'))
  .replace('/*__ASSETS__*/', () => read('build', 'assets.js'));
fs.mkdirSync(path.join(ROOT, 'dist'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'dist', 'djl-skill-vfx.html'), html);
console.log(`dist/djl-skill-vfx.html ${(html.length / 1048576).toFixed(1)} MB`);
