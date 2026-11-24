// main.ts — news-image-20261124 entry point (Node 22, stdlib only).
//
// The entry image is pre-rendered deterministically by draw_news24.py
// (PIL, fixed fonts, fixed layout, no network, no clock, no randomness).
// This program copies that image to the output directory and verifies
// the copy byte-for-byte, so both grader runs write identical bytes.
//
// The image lives next to this file in the repository; it is resolved
// relative to this module (import.meta.url), never via the process
// working directory — the grader runs from /.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const target = join(outDir, "entry.png");

if (!existsSync(source)) {
  throw new Error(`entry.png not found next to main.ts: ${source}`);
}

const before = readFileSync(source);
const digest = createHash("sha256").update(before).digest("hex");
const size = statSync(source).size;
if (size > 1048576) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB limit`);
}
// PNG magic bytes — the file must be a real PNG, not a truncated write.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!before.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

const after = readFileSync(target);
const afterDigest = createHash("sha256").update(after).digest("hex");
if (afterDigest !== digest) {
  throw new Error(`copy mismatch: ${afterDigest} != ${digest}`);
}

console.log(`entry.png ${size} bytes sha256 ${digest} -> ${target}`);
