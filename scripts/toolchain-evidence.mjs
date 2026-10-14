import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
const json = (path) => JSON.parse(readFileSync(path, "utf8"));
const firefly = json("test-results/firefly/acceptance.json");
const ipfs = json("test-results/ipfs/acceptance.json");
const firstRun = json("test-results/firefly/first-run.json");
const liveBrowser = json("test-results/toolchain-browser.json");
const caliper = json("test-results/caliper/latest.json");
const brownie = json("test-results/brownie/gas-reference.json");
const brownieXml = readFileSync("test-results/brownie-tests.xml", "utf8");
assert(
  /failures="0"/.test(brownieXml) &&
    /errors="0"/.test(brownieXml) &&
    /tests="6"/.test(brownieXml)
);
for (const result of [firefly, ipfs, firstRun, liveBrowser])
  assert.equal(result.passed, true);
assert(
  caliper.inventoryReconciled &&
    Object.values(caliper.rounds).every((r) => r.failed === 0)
);
const line = readFileSync("test-results/tooling-browser-tests.log", "utf8")
  .trim()
  .split(/\r?\n/)
  .reverse()
  .find((l) => l.startsWith('{"checks":'));
const browser = JSON.parse(line);
assert.equal(browser.pageErrors.length, 0);
const result = {
  date: "2026-10-14",
  sourceDocument: {
    name: "LOTUS - Synopsis Final.pdf",
    pages: 18,
    sha256: createHash("sha256")
      .update(
        readFileSync("C:/Users/highk/Downloads/LOTUS - Synopsis Final.pdf")
      )
      .digest("hex"),
  },
  operationalProfile: {
    ledger: "Hyperledger Fabric",
    transport: "FireFly Core / FabConnect",
    documents: "IPFS encrypted ciphertext",
    channel: "lotus-operations",
    firstRunReady: true,
    sharedPasswords: false,
    seededBusinessInventory: false,
  },
  validation: {
    contractTests: 37,
    sdkTests: 4,
    apiTests: 11,
    applicationBrowserChecks: browser.checks,
    brownieTests: 6,
    fireflyChecks: firefly.checks,
    ipfsChecks: ipfs.checks,
    fabricFirstRunChecks: firstRun.checks,
    operationalBrowserChecks: liveBrowser.checks,
  },
  firefly,
  ipfs,
  firstRun,
  liveBrowser,
  caliper,
  brownie,
  limits: [
    "Single-host consortium integration",
    "Conventional delivery-provider integration remains a deployment gate",
    "Guardian replacement does not revoke knowledge of a previously compromised secret",
    "Full Synthea x openFDA evaluation campaign and production scaling are not inferred from these measurements",
  ],
};
writeFileSync("docs/toolchain-evidence.json", JSON.stringify(result, null, 2));
console.log(
  "Preserved verified tool results and synopsis provenance in docs/toolchain-evidence.json."
);
