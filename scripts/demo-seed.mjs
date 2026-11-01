import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { newPermit } from '../sdk/src/index.js';

const base = process.env.LOTUS_DEMO_BASE || 'http://127.0.0.1:8787';
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+$/.test(base))
  throw new Error('Demo seeding is limited to the local LOTUS app.');

const roles = ['operator', 'manufacturer', 'distributor', 'pharmacy', 'prescriber', 'regulator'];
const guide = readFileSync(resolve('docs/FIVE_MINUTE_DEMO.md'), 'utf8');
const credentials = Object.fromEntries(roles.map((role) => {
  const line = guide.split(/\r?\n/).find((row) => row.startsWith(`| ${role[0].toUpperCase()}${role.slice(1)} |`));
  const fields = line?.match(/`([^`]+)`/g)?.map((field) => field.slice(1, -1));
  if (!fields || fields.length !== 2 || !fields[0].endsWith('@example.test'))
    throw new Error(`Missing fictional ${role} sign-in in the demo guide.`);
  return [role, { email: fields[0], password: fields[1] }];
}));

async function connect(role) {
  const response = await fetch(`${base}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials[role]),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(`${role} login: ${data.error?.message || response.status}`);
  const cookie = response.headers.get('set-cookie')?.split(';')[0];
  if (!cookie || !data.csrf) throw new Error(`${role} session was not established.`);
  return {
    role,
    async call(path, body) {
      const result = await fetch(`${base}/api${path}`, {
        method: body ? 'POST' : 'GET',
        headers: {
          'Content-Type': 'application/json',
          Cookie: cookie,
          'X-CSRF-Token': data.csrf,
        },
        ...(body ? { body: JSON.stringify(body) } : {}),
      });
      const value = await result.json();
      if (!result.ok)
        throw new Error(`${role} ${path}: ${value.error?.code || result.status} ${value.error?.message || ''}`);
      return value;
    },
    command(name, payload) {
      return this.call('/commands', { command: name, payload, requestId: randomUUID() }).then((result) => result.result);
    },
  };
}

const catalog = [
  ['LOTUS Demo Relief Tablets 10 mg', 'LOTUS-COURSE-RELIEF'],
  ['LOTUS Demo Hydration Sachets', 'LOTUS-COURSE-HYDRATE'],
  ['LOTUS Demo Skin Gel', 'LOTUS-COURSE-GEL'],
  ['LOTUS Demo Cold Care Syrup', 'LOTUS-COURSE-COLD'],
];
const expiry = Math.floor(Date.now() / 1000) + 365 * 86400;
const accounts = {};
for (const role of roles) accounts[role] = await connect(role);

const session = await accounts.operator.call('/session');
if (session.ledger !== 'fabric' || session.network !== 'lotus-fabric-v2')
  throw new Error('Start the fictional Fabric profile before seeding.');

const pharmacy = (await accounts.pharmacy.call('/workspace')).user;
const distributor = (await accounts.distributor.call('/workspace')).user;
if (!pharmacy.orgId || !distributor.orgId)
  throw new Error('Demo distributor and pharmacy need approved organizations.');

const operator = await accounts.operator.call('/workspace');
const availableAtPharmacy = (lot) => operator.stocks.some((stock) =>
  stock.orgId === pharmacy.orgId && stock.lotId === lot.id && BigInt(stock.available) >= 50n);
let ready = operator.lots.filter((lot) =>
  !lot.recallId && lot.expiry > Date.now() / 1000 && availableAtPharmacy(lot));
console.log(`Existing eligible lots at the demo pharmacy: ${ready.length}`);

const created = [];
for (const [name, code] of catalog) {
  if (ready.length >= 4) break;
  if (ready.some((lot) => lot.code === code)) continue;
  const lotNumber = `COURSE-${Date.now().toString(36).toUpperCase()}-${created.length + 1}`;
  console.log(`Preparing ${name} for the demo pharmacy...`);
  const { lot } = await accounts.manufacturer.command('registerLot', {
    namespace: 'DEMO', code, name, lotNumber, quantity: '1200', expiry,
  });
  const first = await accounts.manufacturer.command('ship', {
    lotId: lot.id, toOrgId: distributor.orgId, quantity: '900',
  });
  await accounts.distributor.command('receive', { shipmentId: first.shipment.id, action: 'accept' });
  const second = await accounts.distributor.command('ship', {
    lotId: lot.id, toOrgId: pharmacy.orgId, quantity: '650',
  });
  await accounts.pharmacy.command('receive', { shipmentId: second.shipment.id, action: 'accept' });
  created.push(lot);
  ready.push(lot);
  console.log(`Accepted 650 units of ${lot.lotNumber} at the demo pharmacy.`);
}

if (ready.length < 4)
  throw new Error(`Only ${ready.length} eligible lots are available. Check lot state and rerun.`);

const refreshed = await accounts.operator.call('/workspace');
if (!refreshed.shipments.some((item) => item.status === 'pending' && item.toOrgId === pharmacy.orgId)) {
  const pendingLot = created[0];
  if (pendingLot) {
    await accounts.distributor.command('ship', {
      lotId: pendingLot.id, toOrgId: pharmacy.orgId, quantity: '40',
    });
    console.log('Created one pending pharmacy shipment for the Incoming workspace.');
  }
}

const prescriber = await accounts.prescriber.call('/workspace');
const existingProducts = new Set(prescriber.permits
  .filter((permit) => permit.expiry > Date.now() / 1000 && BigInt(permit.balance) > 0n)
  .map((permit) => `${permit.namespace}:${permit.code}`));
const handovers = [];
for (const lot of ready.slice(0, 2)) {
  if (existingProducts.has(`${lot.namespace}:${lot.code}`)) continue;
  const credential = newPermit();
  const result = await accounts.prescriber.command('issuePermit', {
    namespace: lot.namespace,
    code: lot.code,
    quantity: '8',
    expiry: Math.floor(Date.now() / 1000) + 30 * 86400,
    holderCommit: credential.holderCommit,
  });
  handovers.push({ ...result.permit, permitSecret: credential.permitSecret, network: session.network, v: 2 });
  console.log(`Issued a fictional prescriber permit for ${lot.name}.`);
}
if (handovers.length) {
  const output = resolve('.lotus-data/demo-prescription-handovers.json');
  const previous = existsSync(output) ? JSON.parse(readFileSync(output, 'utf8')) : [];
  const byId = new Map([...previous, ...handovers].map((handover) => [handover.id, handover]));
  writeFileSync(output, JSON.stringify([...byId.values()], null, 2));
  console.log('Saved new private handover credentials in the ignored local demo data folder.');
}

const finalState = await accounts.operator.call('/workspace');
const finalReady = finalState.lots.filter((lot) =>
  !lot.recallId && lot.expiry > Date.now() / 1000 &&
  finalState.stocks.some((stock) => stock.orgId === pharmacy.orgId && stock.lotId === lot.id && BigInt(stock.available) > 0n));
const pharmacyState = await accounts.pharmacy.call('/workspace');
const counterOptions = pharmacyState.lots.filter((lot) =>
  !lot.recallId && lot.expiry > Date.now() / 1000 &&
  pharmacyState.stocks.some((stock) =>
    stock.orgId === pharmacyState.user.orgId && stock.lotId === lot.id && BigInt(stock.available) > 0n));
if (counterOptions.length < 4)
  throw new Error(`Pharmacy counter has only ${counterOptions.length} selectable lots after seeding.`);
console.log(`Ready: ${finalReady.length} eligible pharmacy lots, ${finalState.recalls.length} preserved recalls.`);
console.log(`Pharmacy counter options: ${counterOptions.length}.`);
