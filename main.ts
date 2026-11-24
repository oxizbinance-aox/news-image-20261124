// NI24 entrypoint — copies the pre-rendered entry.png into the output dir.
// Node 22, stdlib only. No network. The copy is verified byte-for-byte
// (SHA-256 + PNG magic) so a corrupt or stale image fails loudly instead
// of shipping silently.
import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function sha256(buf: Buffer): string {
  return createHash("sha256").update(buf).digest("hex");
}

async function main(): Promise<void> {
  const bytes = await readFile(SRC);
  if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    throw new Error("entry.png is not a PNG (bad magic bytes)");
  }
  // IHDR: width at offset 16, height at offset 20 (big-endian uint32).
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    throw new Error(`entry.png must be 1024x1024, got ${width}x${height}`);
  }
  const digest = sha256(bytes);
  await mkdir(OUT_DIR, { recursive: true });
  const dest = join(OUT_DIR, "entry.png");
  await copyFile(SRC, dest);
  const again = await readFile(dest);
  if (sha256(again) !== digest) {
    throw new Error("copied entry.png does not match source hash");
  }
  console.log(`entry.png ${bytes.length} bytes sha256=${digest}`);
  console.log(`copied to ${dest} (verified)`);
}

await main();
