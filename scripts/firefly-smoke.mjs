import { readFileSync } from "node:fs";
import { FireFlyClient } from "../services/api/src/firefly.js";
import { FabricLedger } from "../services/api/src/fabric.js";
import { randomUUID } from "node:crypto";
const config = JSON.parse(
  readFileSync(".fabric-network/tooling-gateway.json", "utf8")
);
const client = new FireFlyClient(
  ".tooling/firefly/runtime/client.json",
  config
);
const data = await client.call(config.publicReader, "Snapshot");
console.log(
  JSON.stringify(
    {
      querySucceeded: true,
      organizations: data.organizations?.length,
      keys: Object.keys(data),
    },
    null,
    2
  )
);
const actors = JSON.parse(readFileSync(".tooling/context.json", "utf8")).actors;
const ledger = new FabricLedger(
  { options: {} },
  ".fabric-network/tooling-gateway.json",
  ".tooling/firefly/runtime/client.json"
);
try {
  const result = await ledger.run(
    actors.manufacturer,
    "registerLot",
    {
      name: "FireFly committed medicine",
      namespace: "NDC",
      code: "FF-TEST",
      lotNumber: randomUUID(),
      quantity: "10",
      expiry: Math.floor(Date.now() / 1000) + 86400,
    },
    randomUUID()
  );
  console.log(
    JSON.stringify({
      transport: ledger.transport,
      registeredLot: result.lot.id,
    })
  );
} finally {
  await ledger.close();
}
