# Five-minute LOTUS coursework demonstration

This run uses one laptop and one phone or tablet. The laptop hosts the local Fabric, FireFly and IPFS integration profile and presents the staff workspaces. The phone is the patient's encrypted browser vault. All accounts, medicines and reports in this run must be fictional.

## What the new demo controls do

- **Operator → Demo readiness** checks the selected ledger, active lots, accepted manufacturer → distributor → pharmacy custody and pharmacy stock. It deliberately cannot inspect prescriber permits or a patient's local vault.
- **Verify this lot / Open public lot check** opens a public check for that exact product and lot. The page fills the fields and performs the lookup automatically. Keep the page open to repeat the check after a recall.
- The patient page shows every regulator-issued recall from the public ledger feed, even before a patient unlocks a vault. After unlock, the vault separately marks whether any stored receipt matches; only a matched receipt enables the private acknowledgement.
- Existing `DEMO` namespace lots now work in the public check, pack scanner and prescriber namespace selector. Registered namespaces are loaded from the public feed. `DEMO` means fictional coursework data, not a product-code standard.
- The QR scanner first tries a rear camera and then an available webcam, making the laptop side of the phone → pharmacy handoff more reliable. It still offers paste as a fallback.
- On the phone, tap **Scan** once, allow camera access, then hold the complete code steady in the camera view. Use **Enlarge QR for scanning** on the laptop's prescription or receipt screen if the camera has trouble focusing. The phone cannot scan a QR displayed on its own screen: show the pharmacy receipt on the laptop for the phone to scan, and show the phone counter code to the laptop webcam.

## Preparation, before the clock starts

### Demo staff sign-ins

The following fictional staff sign-ins are active in this machine's demo profile. Their passwords were freshly set for this run; earlier demo passwords and sessions are revoked. These accounts use synthetic records only. Keep the profile on this laptop and tailnet; do not reuse these credentials on another deployment.

| Role | Email | Password |
| --- | --- | --- |
| Operator | `lotus-demo-operator-375368@example.test` | `3MEHO-3xqFtUqwlMIQ95Wn37` |
| Manufacturer | `lotus-demo-manufacturer-375368@example.test` | `5w_ue1jXD_kYqdMqAoc2PZKO` |
| Distributor | `lotus-demo-distributor-375368@example.test` | `5beNBlHzj6YJlE7FjZV23gQb` |
| Pharmacy | `lotus-demo-pharmacy-375368@example.test` | `PKFJyDy9Md4JVQUjB6G8-oSl` |
| Prescriber | `lotus-demo-prescriber-375368@example.test` | `zTT9LN4H0TvJxqjDzs2OvPkq` |
| Regulator | `lotus-demo-regulator-375368@example.test` | `qgGN4gAh-3sKDcSPFO0eKZ2h` |

This Fabric profile has one enrolled operator identity. The demo operator sign-in replaces its prior email and password while preserving that Fabric identity; the previous operator email and sessions are retired.

1. Build and start from the repository root: `npm run build`, then `npm start`. Startup now checks and starts offline IPFS, the local Fabric network and operational FireFly before opening the app. Keep the terminal running. Do not switch to the local ledger profile for this demonstration. Confirm the operator's Integrations page says **Fabric**, **FireFly connected** and **IPFS connected**. Historical Caliper and Brownie panels are evidence from separate runs.
2. Run `npm run demo:seed` in another terminal while the app is open. This repeatable initializer uses the fictional staff sign-ins above, restores four active lots with at least 50 units at the demo pharmacy, supplies accepted manufacturer → distributor → pharmacy custody, adds a pending pharmacy shipment and two prescriber permits when missing, and preserves earlier recalls. It does not create a patient vault. New permit handover secrets are saved only in the ignored `.lotus-data/demo-prescription-handovers.json` file. The demo app must be running on the local Fabric profile; update the credential table if the fictional staff passwords change.
3. Open **Operator → Demo readiness**. Choose an active fictional lot with **Both legs accepted** and positive pharmacy units. Open **Verify this lot** and confirm the public check shows the same lot and custody path. Leave this tab ready for a repeat check.
4. In the prescriber browser profile, open **Issue permit**. Select the chosen lot's namespace and product code, set a small quantity (for example, 2 base units) and a future expiry, and issue the permit. Scan the resulting prescription QR into the patient's phone under **Medicines → Add prescription**. Keep **Active permits** open to show the remaining balance briefly during the talk. If you use an existing permit, confirm it is unexpired and has enough balance.
5. In the patient browser, create or unlock the encrypted vault. Check that the imported permit matches the chosen product. Do not create the one-time counter code yet. The vault locks after five minutes of inactivity, so unlock it again immediately before the timed run.
6. In a separate pharmacy browser profile, open **Counter**. Confirm the same lot is available. In a separate regulator profile, open **Recalls** and prepare an exact-lot decision with a fictional reason and patient instructions; submit it only during the run. Use separate browser profiles or browsers, since ordinary tabs share the same staff session.
7. Test both QR directions: laptop webcam reading the phone's screen, and phone camera reading the laptop receipt. Aim the phone screen toward the laptop webcam. A small USB webcam or QR scanner is a useful optional accessory; a second laptop is unnecessary. The paste control is available for a rehearsed, private cross-device clipboard transfer of fictional data.
8. Give the phone a trusted HTTPS address. If both devices use the same signed-in tailnet, run `powershell -File scripts/demo-phone.ps1` after the app starts; it prints the patient URL. Tailscale Serve must be connected first. The default `127.0.0.1:8787` URL works only on the laptop. Open the phone URL, permit its camera, and test vault creation/import before presenting. Keep the phone awake and connected.
9. Rehearse once with a stopwatch. A fill, recall and browser proof are real commits, so they consume the prepared permit/code and change the lot state. Run `npm run demo:seed` to restore eligible stock before repeating the full run. Never claim an earlier result was produced live.

## Timed run

| Clock | Device and action | What to say |
| --- | --- | --- |
| 0:00–0:25 | Laptop, **Operator → Integrations**, then **Demo readiness**. Show selected Fabric, FireFly/IPFS status, accepted custody and pharmacy stock. | “This is one local integration network. Different staff roles submit authorized changes to the same medicine record.” |
| 0:25–0:50 | Laptop, click **Verify this lot**. Show registered product, expiry and accepted custody summary with no login. | “A public lookup shows the lot's approved path without exposing patient or counter details.” |
| 0:50–1:05 | Laptop, **Prescriber → Active permits**. Show product, expiry and remaining quantity. | “The patient has already imported this expiring permit into a private vault.” |
| 1:05–2:30 | Phone, **Counter code → Create fresh counter code**. Pharmacy laptop scans it, selects an eligible lot from **Select ledger lot (virtual shelf)**, enters 1 unit and clicks **Validate and record fill**. No physical pack scan is needed. Wait for **Fill committed**. Phone taps **Home → Check now**, then opens **Medicines → Add the detailed pharmacy receipt** and scans the receipt QR. | “The one-time code and exact ledger lot must both pass the rules. The recorded receipt is the handover point; stock and permit balance change together.” |
| 2:30–3:05 | Laptop, regulator submits the prepared **exact-lot recall**. Wait for **Recall committed**. | “Only this lot is recalled; a new fill from it is blocked.” |
| 3:05–4:05 | Phone, refresh `/patient`. Show the public recall bulletin (visible while locked), then unlock the vault and tap **Home → Check now**. Open **Alerts → Send anonymous acknowledgement** for the matched receipt. Wait for **Anonymous acknowledgement accepted**. | “The bulletin is public. The phone privately checks whether its saved receipt belongs to the recalled lot; the acknowledgement proves eligibility without sending the vault or exact receipt.” |
| 4:05–4:35 | Laptop, refresh **Regulator → Recalls** for the acknowledgement count, then reopen the same public verification link and press **Check lot status** if needed. Show **This lot has an official recall**. | “The regulator sees a response count, and the public status changes for the same product and lot.” |
| 4:35–4:50 | State the boundary. | “These peers and services run on one laptop. This demonstrates an integrated Fabric workflow, not independent consortium administration or guaranteed closed-browser recall delivery.” |

The remaining ten seconds are a buffer. Keep a previously verified screenshot of the anonymous acknowledgement as a clearly labelled fallback if proof generation on the actual phone exceeds its rehearsal time. The live run should never present a pre-run result as a new commit.

## Questions likely to follow

- **Where is the blockchain?** The workspace ledger badge identifies Fabric; FireFly submits ordinary commands and indexes commits. The public check reads committed lot and recall state. The operator's application journal is an application record, not a full Fabric block explorer.
- **Where are documents?** The manufacturer can attach a fictional certificate. IPFS holds encrypted bytes; Fabric holds its CID and digests. Open **Manufacturer → Documents** after the timed run to show an authorized retrieval.
- **Where is privacy?** The phone keeps the root secret and permit credential in its encrypted vault. Local matching and the anonymous proof are visible in the patient run. The regulator's recall table displays counts, not a patient list.
- **What else can the app do?** The workspaces include returns/quarantine, losses, batch fills, transfers, safety reports, imports, regional records, guardian recovery and an offline cached bulletin. Show these only during questions so the main story stays under five minutes.
- **What do the measurements mean?** Caliper results are historical tests on an isolated Fabric channel. Brownie is an EVM regression and gas reference, not a Fabric transaction cost.

See [web application guide](WEB_APPLICATION_GUIDE.md) for full setup, phone security requirements and deployment limits.
