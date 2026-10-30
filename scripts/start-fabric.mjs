import { closeSync, mkdirSync, openSync } from "node:fs";
import { execFileSync, spawn } from "node:child_process";
import { resolve, sep } from "node:path";
import { createApp } from "../services/api/src/server.js";

const root = process.cwd();
const wait = (ms) => new Promise((done) => setTimeout(done, ms));
async function reachable(url) {
  try {
    const response = await fetch(url, {
      method: url.includes("/api/v0/") ? "POST" : "GET",
      signal: AbortSignal.timeout(1200),
    });
    return response.ok;
  } catch {
    return false;
  }
}
async function waitFor(url, label, logPath) {
  for (let attempt = 0; attempt < 60; attempt++) {
    if (await reachable(url)) return;
    await wait(500);
  }
  throw new Error(`${label} did not become ready. Check ${logPath}.`);
}
function wslPath(path) {
  const absolute = resolve(path);
  if (process.platform !== "win32") return absolute;
  if (!/^[A-Za-z]:\\/.test(absolute))
    throw new Error(`Cannot map this path into WSL: ${absolute}`);
  return `/mnt/${absolute[0].toLowerCase()}${absolute.slice(2).split(sep).join("/")}`;
}
function runLinuxScript(script, args = []) {
  const linuxScript = wslPath(resolve("scripts", script));
  const command = process.platform === "win32" ? "wsl.exe" : "bash";
  const commandArgs = process.platform === "win32"
    ? ["-d", "Ubuntu", "--", "bash", linuxScript, ...args]
    : [linuxScript, ...args];
  execFileSync(command, commandArgs, {
    cwd: root,
    stdio: "inherit",
    timeout: 10 * 60 * 1000,
    maxBuffer: 8 * 1024 * 1024,
  });
}
async function ensureLocalServices() {
  const dataDir = resolve(process.env.LOTUS_DATA_DIR || ".lotus-data");
  mkdirSync(dataDir, { recursive: true });
  const ipfsUrl = process.env.LOTUS_IPFS_API || "http://127.0.0.1:15001";
  const ipfsLog = resolve(dataDir, "ipfs-start.log");
  if (!(await reachable(`${ipfsUrl}/api/v0/version`))) {
    console.log("Starting offline IPFS document storage…");
    const log = openSync(ipfsLog, "a");
    const child = spawn(process.execPath, [resolve("scripts/ipfs-start.mjs")], {
      cwd: root,
      detached: process.platform === "win32",
      windowsHide: true,
      stdio: ["ignore", log, log],
    });
    closeSync(log);
    child.unref();
    await waitFor(`${ipfsUrl}/api/v0/version`, "IPFS", ipfsLog);
  }

  console.log("Checking the local Fabric network…");
  runLinuxScript("fabric-native.sh");
  console.log("Starting FireFly for the operational channel…");
  runLinuxScript("firefly-start.sh", [wslPath(resolve(".tooling/firefly/operations"))]);
  await waitFor(
    "http://127.0.0.1:5300/api/v1/namespaces/lotus-org1/status",
    "FireFly",
    resolve(".tooling/firefly/operations/logs")
  );
}

await ensureLocalServices();
const service = createApp({
  dataDir: resolve(process.env.LOTUS_DATA_DIR || ".lotus-data"),
  mode: "fabric",
  fabricConfig: resolve(".fabric-network/gateway.json"),
  fireflyConfig: resolve(".tooling/firefly/operations/client.json"),
  ipfsApi: process.env.LOTUS_IPFS_API || "http://127.0.0.1:15001",
});
const port = Number(process.env.PORT || 8787),
  host = process.env.HOST || "127.0.0.1";
const server = service.app.listen(port, host, () =>
  console.log(
    `LOTUS: http://${host}:${port} | Fabric through FireFly | encrypted IPFS documents`
  )
);
server.on("error", (error) => {
  console.error(error.message);
  process.exit(1);
});
const close = async () => {
  await new Promise((done) => server.close(done));
  await service.close();
  process.exit(0);
};
process.on("SIGINT", close);
process.on("SIGTERM", close);
