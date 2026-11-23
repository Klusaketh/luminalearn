/**
 * Copies the Pyodide runtime (Python compiled to WebAssembly) from node_modules into public/pyodide,
 * so the coding sandbox loads it from this site instead of a third-party CDN.
 * Runs before `next dev` and `next build`; the copy is git-ignored.
 */
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = join(frontendDir, "node_modules", "pyodide");
const target = join(frontendDir, "public", "pyodide");
const FILES = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"];

if (!existsSync(source)) {
  console.error("[pyodide] node_modules/pyodide is missing. Run `npm ci` in frontend/ first.");
  process.exit(1);
}
mkdirSync(target, { recursive: true });
let copied = 0;
for (const file of FILES) {
  const from = join(source, file);
  const to = join(target, file);
  if (!existsSync(to) || statSync(to).size !== statSync(from).size) {
    copyFileSync(from, to);
    copied += 1;
  }
}
console.log(`[pyodide] runtime ready in public/pyodide (${copied} file(s) updated).`);
