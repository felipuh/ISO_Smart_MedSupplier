/* global process */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const srcDir = path.join(root, 'src');
const messagesUrl = pathToFileURL(path.join(srcDir, 'i18n', 'messages.js')).href;
const { MESSAGES } = await import(messagesUrl);

const languages = ['es-LATAM', 'en', 'pt'];

const flattenKeys = (value, prefix = '') => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return [];
  return Object.entries(value).flatMap(([key, child]) => {
    const next = prefix ? `${prefix}.${key}` : key;
    if (child && typeof child === 'object' && !Array.isArray(child)) {
      return flattenKeys(child, next);
    }
    return [next];
  });
};

const walk = (dir) => {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  return entries.flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (['dist', 'node_modules'].includes(entry.name)) return [];
      return walk(fullPath);
    }
    return /\.(jsx?|tsx?)$/.test(entry.name) ? [fullPath] : [];
  });
};

const keySets = Object.fromEntries(
  languages.map((language) => [language, new Set(flattenKeys(MESSAGES[language]))])
);

let hasMissing = false;
for (const language of languages) {
  const reference = keySets['es-LATAM'];
  const missing = [...reference].filter((key) => !keySets[language].has(key));
  if (missing.length) {
    hasMissing = true;
    console.error(`\nMissing keys in ${language}:`);
    missing.slice(0, 200).forEach((key) => console.error(`  - ${key}`));
    if (missing.length > 200) console.error(`  ...and ${missing.length - 200} more`);
  }
}

const files = walk(srcDir);
const usedKeys = new Set();
const tCallPattern = /\bt\(\s*['"`]([A-Za-z0-9_.-]+)['"`]/g;
for (const file of files) {
  const source = fs.readFileSync(file, 'utf8');
  for (const match of source.matchAll(tCallPattern)) {
    if (!match[1].startsWith('literals.')) usedKeys.add(match[1]);
  }
}

const missingUsed = [...usedKeys].filter((key) => !keySets['es-LATAM'].has(key));
if (missingUsed.length) {
  hasMissing = true;
  console.error('\nUsed keys not defined in es-LATAM:');
  missingUsed.slice(0, 200).forEach((key) => console.error(`  - ${key}`));
}

const possibleHardcoded = [];
const visibleTextPattern = />\s*([^<>{}\n]*[A-Za-zÁÉÍÓÚáéíóúñÑ][^<>{}\n]*)\s*</g;
for (const file of files) {
  if (file.endsWith('i18n/messages.js')) continue;
  const source = fs.readFileSync(file, 'utf8');
  for (const match of source.matchAll(visibleTextPattern)) {
    const text = match[1].trim();
    if (!text || /^[A-Z][A-Za-z0-9]+$/.test(text)) continue;
    possibleHardcoded.push(`${path.relative(root, file)}: ${text}`);
  }
}

console.log(`Checked ${languages.length} languages and ${usedKeys.size} statically used i18n keys.`);
if (possibleHardcoded.length) {
  console.log('\nPossible visible hardcoded text, review only:');
  possibleHardcoded.slice(0, 80).forEach((item) => console.log(`  - ${item}`));
  if (possibleHardcoded.length > 80) console.log(`  ...and ${possibleHardcoded.length - 80} more`);
}

if (hasMissing) process.exit(1);
