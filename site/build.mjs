// Bundles main.js + three.js + fonts into one self-contained ../docs/index.html
//   cd site && npm install && npm run build
import { build } from 'esbuild';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const font = (p) => readFileSync(join(here, '..', '.github', 'scripts', 'fonts', p)).toString('base64');

const out = await build({
  entryPoints: [join(here, 'main.js')],
  bundle: true, minify: true, format: 'iife', target: 'es2020', write: false,
  legalComments: 'none',
});
const js = out.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');

const html = readFileSync(join(here, 'template.html'), 'utf8')
  .replace('__UNBOUNDED__', () => font('unbounded-latin-700-normal.woff2'))
  .replace('__GROTESK__', () => font('space-grotesk-latin-500-normal.woff2'))
  .replace('__BUNDLE__', () => js);

mkdirSync(join(here, '..', 'docs'), { recursive: true });
writeFileSync(join(here, '..', 'docs', 'index.html'), html);
writeFileSync(join(here, '..', 'docs', '.nojekyll'), '');
console.log(`docs/index.html  ${(html.length / 1024).toFixed(0)} KB`);
