"""Build a role-based LOTUS blockchain coursework guide."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Frame, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "LOTUS_Blockchain_Coursework_Team_Guide.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_DIR / "arialbd.ttf")))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

NAVY = colors.HexColor("#12304A")
TEAL = colors.HexColor("#127C80")
PALE = colors.HexColor("#EAF3F4")
LIGHT = colors.HexColor("#F3F6F8")
GREY = colors.HexColor("#526271")
INK = colors.HexColor("#182B39")
LINE = colors.HexColor("#CED9DF")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleLotus", fontName="Arial-Bold", fontSize=27, leading=32,
                          textColor=NAVY, spaceAfter=13))
styles.add(ParagraphStyle(name="SubtitleLotus", fontName="Arial", fontSize=12, leading=17,
                          textColor=GREY, spaceAfter=15))
styles.add(ParagraphStyle(name="SectionLotus", fontName="Arial-Bold", fontSize=17, leading=21,
                          textColor=NAVY, spaceBefore=2, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle(name="H2Lotus", fontName="Arial-Bold", fontSize=10.6, leading=14,
                          textColor=TEAL, spaceBefore=10, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyLotus", fontName="Arial", fontSize=9.15, leading=13.3,
                          textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="BulletLotus", parent=styles["BodyLotus"], leftIndent=13,
                          firstLineIndent=-9, spaceAfter=4))
styles.add(ParagraphStyle(name="SmallLotus", fontName="Arial", fontSize=7.65, leading=10.4,
                          textColor=GREY, spaceAfter=4))
styles.add(ParagraphStyle(name="TableHeadLotus", fontName="Arial-Bold", fontSize=8.2,
                          leading=11, textColor=colors.white))
styles.add(ParagraphStyle(name="TableCellLotus", fontName="Arial", fontSize=8.1,
                          leading=11.3, textColor=INK))
styles.add(ParagraphStyle(name="CalloutLotus", fontName="Arial", fontSize=9.0, leading=13,
                          textColor=NAVY, leftIndent=10, rightIndent=8, spaceAfter=0))

story = []


def P(text, style="BodyLotus"):
    return Paragraph(text, styles[style])


def h(text):
    story.append(P(text, "H2Lotus"))


def p(text):
    story.append(P(text))


def bullets(items):
    for item in items:
        story.append(P("- " + item, "BulletLotus"))


def table(headers, rows, widths=None):
    data = [[P(escape(str(v)), "TableHeadLotus") for v in headers]]
    data += [[P(str(v), "TableCellLotus") for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, LINE),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))


def callout(label, body):
    t = Table([[P(f"<b>{label}</b> {body}", "CalloutLotus")]], colWidths=[176*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("LINEBEFORE", (0, 0), (0, 0), 3, TEAL),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))


def role(number, name, reg, work, takeaway):
    story.append(CondPageBreak(100*mm))
    story.append(P(f"{number:02d} / {escape(work)}", "SectionLotus"))
    story.append(P(f"<b>{escape(name)}</b>  |  Registration no. {reg}", "SubtitleLotus"))
    callout("Core explanation.", takeaway)


def sources(items):
    h("Where to verify this part")
    story.append(P("Repository paths are relative to the LOTUS project root. They identify the implemented source or the evidence record; the guide does not claim that commit history proves who typed each line.", "SmallLotus"))
    bullets([f"<b>{escape(path)}</b> - {escape(why)}" for path, why in items])


story.append(Spacer(1, 31*mm))
story.append(P("LOTUS", "TitleLotus"))
story.append(P("Blockchain coursework guide for the eight team responsibilities", "SubtitleLotus"))
story.append(Spacer(1, 4*mm))
callout("Project in one sentence.", "LOTUS records the exact medicine lot delivered to a pharmacy and a private patient commitment, then lets the patient identify a relevant recall and respond without publishing their identity.")
p("This guide follows the team-work table supplied with the request. It explains the present Hyperledger Fabric implementation first, then labels retained Solidity experiments and synthetic research results separately. It is a speaking and study guide, not a claim that the table proves individual source-code authorship.")
story.append(Spacer(1, 7*mm))
table(["Person", "Registration no.", "Coursework responsibility"], [
    ("Patoju Sai Avinash", "230968356", "Ledger Architecture"),
    ("Adabala Venkata Abhinav", "230968284", "Privacy & Key Custody"),
    ("K. Jaideep Varma", "230968076", "Rule Enforcement & Verification"),
    ("Dhruti P Shetty", "230968025", "Red Team / Adversary Simulation"),
    ("Ashmith C Shettigar", "230968023", "Measurement & Evaluation"),
    ("P Pattabhi Ram", "230968033", "Data Pipeline & Reproducibility"),
    ("Puripanda Venkata Praneeth", "230957112", "Patient-Side Product"),
    ("K. Poorna Sai Praneeth", "230968248", "Integration & Deployment"),
], [58*mm, 33*mm, 85*mm])
p("Prepared from the repository as it stood on 30 October 2026. All medicine, patient and staff data used in the coursework demonstration are fictional. Keep the stated research and deployment boundaries when presenting results.")

story.append(PageBreak())
story.append(P("Shared foundation", "SectionLotus"))
h("The blockchain question")
p("Ordinary drug traceability usually proves where a lot moved upstream, but the patient record can stop at a product code. If lot A is recalled while lots B to F are fine, product-code matching warns many unaffected people and can miss people whose records are unlinked. LOTUS adds a verifiable, lot-specific final handoff. Multiple organizations can check the same ordered history and enforce stock and permit rules without trusting one pharmacy's database alone.")
h("The actors and one complete path")
table(["Step", "Ledger fact", "Why it matters"], [
    ("1. Register", "Manufacturer creates product namespace, code, lot, quantity, expiry and optional document digest.", "The lot has an authoritative identity and initial stock."),
    ("2. Move", "Sender ships; named recipient accepts or rejects.", "Only accepted stock becomes usable downstream."),
    ("3. Permit", "Prescriber issues an expiring quantity balance tied to a one-time holder credential.", "A fill cannot exceed or outlive the prescription."),
    ("4. Dispense", "Pharmacy submits exact lot, quantity, permit credential and fresh patient commitment.", "Stock, permit and receipt change together or the transaction fails."),
    ("5. Recall", "Regulator issues one immutable decision for the exact lot.", "Later dispensing is blocked; the public bulletin can be checked."),
    ("6. Respond", "Patient locally finds the commitment and proves membership for a response.", "The ledger counts eligible responses without learning which leaf belongs to the person."),
], [21*mm, 89*mm, 66*mm])
h("What lives where")
bullets([
    "<b>Fabric world state and history:</b> actors, organizations, lots, stock buckets, shipments, permit balances and holder hashes, commitment leaves and roots, recalls, nullifiers, counts, CIDs and digests. The current chaincode shares domain rules with local development mode.",
    "<b>Patient browser:</b> root secret, permit secret, issued-code indices, receipts and recovery data in an encrypted IndexedDB vault. A fresh commitment is public per fill; the root secret is not.",
    "<b>FireFly/FabConnect:</b> ordinary command submission and durable committed-event indexing. Fabric remains the business authority. Permit credentials travel through Fabric Gateway transient data because FireFly stores ordinary request arguments.",
    "<b>IPFS:</b> encrypted document bytes. Fabric keeps the content identifier and digests so a retrieved document can be checked against the registered reference.",
    "<b>Separate research tools:</b> a Solidity/EVM prototype with Brownie gas measurements; Python synthetic recall evaluation and Node adversary simulations. These do not measure production Fabric throughput or clinical notification delivery.",
])
callout("Critical boundary.", "The supplied Fabric network has two configured endorsing organizations on one laptop. That proves integration and valid commits in a local environment, not independently governed production decentralization.")

role(1, "Patoju Sai Avinash", "230968356", "Ledger Architecture",
     "Explain why a shared ledger is needed, what each layer owns, and how a medicine lot becomes an auditable final-handoff record.")
h("Design decision: a permissioned shared ledger")
p("The operational ledger is Hyperledger Fabric 3.1.5. Organizations use certificates and MSP identities rather than public-wallet addresses. The local network has two peer organizations, TLS identities, a Raft orderer, a LOTUS channel, and an external Node chaincode service. Both organizations endorse the current chaincode definition. These are coursework integration settings; independently administered peers and production CA enrollment are future deployment work.")
p("Fabric orders transactions, checks endorsements and commits one consistent result. The contract named <b>Lotus</b> uses the certificate identity to find an enrolled actor. The actor must still be active and have the correct role and organization. A certificate alone is not a right to dispense or recall.")
h("Layered architecture")
table(["Layer", "Responsibility", "Concrete implementation"], [
    ("Client", "Role-specific staff actions; private patient checking.", "Responsive workspaces and patient PWA."),
    ("Application/API", "Authenticate users; construct commands; route private credentials; expose allowed views.", "services/api/src/server.js and fabric.js"),
    ("Transport", "Submit commands and index committed events.", "FireFly Core and FabConnect; Gateway for transient secrets."),
    ("Ledger", "Authorize and enforce invariant-preserving state transitions.", "chaincode/lotus/index.cjs + packages/domain/src/engine.js"),
    ("External bytes", "Store encrypted certificates, manifests and reports.", "IPFS; Fabric anchors CID and SHA-256 digests."),
], [28*mm, 64*mm, 84*mm])
h("Ledger data model")
p("The chaincode repository reads and writes Fabric keys such as <b>actor:</b>, <b>org:</b>, <b>lot:</b>, <b>stock:</b>, <b>shipment:</b>, <b>permit:</b>, <b>receipt:</b>, <b>leaf:</b>, <b>tree:</b>, <b>root:</b>, <b>recall:</b>, <b>nullifier:</b> and <b>command:</b>. A lot ID is a SHA-256-derived identifier over manufacturer organization, namespace, product code and lot number. Shipment resolution records who sent, who was named to receive, quantity and accepted or rejected status. Stock is partitioned into available, in-transit, quarantined, dispensed, returned and shrinkage quantities.")
p("A fill writes the commitment and receipt, updates the per-lot Poseidon Merkle tree, and records a root accepted for later proofs. Large lots roll to a new tree segment at 65,536 leaves. A recall stores the decision and the lot's receipt count at issue time. The public feed exposes selected lot/recall fields and commitment leaves, while authenticated snapshots are filtered by actor role and organization.")
h("Transaction lifecycle and audit meaning")
bullets([
    "An authenticated staff action receives a stable request ID. The domain engine hashes actor, command and payload, then stores a <b>command:</b> result; exact retries return the same result, changed content with the same ID fails.",
    "For an ordinary command, FireFly submits the chaincode call and waits for successful confirmation. The API then queries Fabric's <b>CommandResult</b> with actor and expected digest; an unconfirmed response remains uncertain, not silently retried as a new business operation.",
    "For a fill or transfer, Gateway sends the permit credential in transient data. The chaincode merges it into the in-memory command before checking the holder hash; the credential is removed from the public argument JSON.",
    "The chaincode emits <b>LotusCommitted</b> with the request ID and domain events. FireFly indexes those committed events. A journal in the application is a convenience record, not a full Fabric block explorer.",
])
h("What this architecture proves, and what it does not")
p("A valid Fabric commit shows the configured peers endorsed and ordered the state change under the current policy. It does not prove that the physical pack was genuine, that a human took the medicine, or that independent organizations administer the nodes. Public QR lookup checks registered lot data and status, not physical provenance by itself.")
sources([
    ("chaincode/lotus/index.cjs", "Fabric entry points, identity mapping, state access, command and public-feed boundaries"),
    ("packages/domain/src/engine.js", "state model, event creation and transaction rules"),
    ("infra/fabric/configtx.yaml; docs/WEB_APPLICATION_GUIDE.md", "local channel, endorsement and deployment boundary"),
    ("docs/TOOLCHAIN_MIGRATION.md", "current toolchain architecture and evidence mapping"),
])

role(2, "Adabala Venkata Abhinav", "230968284", "Privacy & Key Custody",
     "Explain how a patient can recognize their own lot and prove eligibility while the ledger never stores their name or root secret.")
h("Privacy is a placement rule")
p("The phone creates a random BN254 field element as the patient's root secret. For each allocated index i, it derives <b>nonce_i = Poseidon(secret, i)</b> and <b>commitment_i = Poseidon(secret, nonce_i)</b>. A different index gives a fresh public commitment for each fill. Deterministic derivation also means recovery of the root secret can reconstruct the commitment history, provided issued indices or a current backup are retained. The current patient app explicitly stores every issued index before showing a counter code; it does not rely on the older SDK's 20-miss discovery rule.")
p("The prescriber's separate 32-byte permit secret is represented on the ledger only by <b>keccak256(permitSecret)</b>. The counter QR contains the permit ID, permit secret, commitment, index and network, but not the patient's root secret. A pharmacist necessarily sees the person at the counter and this one fill's credential; the design limits cross-fill linkage from the ledger view.")
h("Browser vault and recovery")
bullets([
    "The patient vault is an IndexedDB record encrypted with AES-256-GCM. Its key is derived from a passphrase using PBKDF2-SHA-256 with 600,000 iterations and a random salt. The key remains in memory only while unlocked; the interface locks after five minutes of inactivity.",
    "The app saves the next index and issued-index list before displaying a QR. A storage error stops code creation, avoiding a displayed but unrecorded commitment.",
    "Shamir two-of-three sharing splits the root secret across separate guardian vaults. Two valid shares reconstruct it. A separate encrypted backup restores permits, receipts, acknowledgements and allocated indices. That package omits the full share set and must be refreshed after new activity.",
    "Replacing guardian shares changes future recovery arrangements. It cannot erase a secret already learned by a compromised device or two colluding old guardians. A stale backup cannot restore data created after its download.",
])
h("Anonymous proof path")
p("For a recalled lot or safety report, the browser builds a Merkle witness from the lot's published leaves and runs the Groth16 circuit. Its private inputs are the secret, index and Merkle path. Public inputs are the committed root, nullifier hash, external nullifier and signal hash. The circuit proves that the commitment derived from that secret is in the lot tree and that the nullifier is derived from the same secret, without revealing the leaf index. The signal hash binds the selected action or encrypted-report digest to the proof.")
p("Fabric chaincode verifies the Groth16 proof with the stored verification key, checks that the root was committed, checks the recall timing for acknowledgements, and rejects a consumed nullifier. The external topic includes the network plus report-lot or acknowledgement-recall scope. Thus a recipient can report once per lot and acknowledge once per recall without a named patient account.")
h("Release boundaries and residual leakage")
p("The public feed deliberately includes commitment leaves so local matching and proof generation work. It omits counter time, pharmacy, region and quantity for each leaf, but the number of leaves still reveals approximate activity. Regulator regional output suppresses cells below five and may hide a second cell to prevent subtraction. These are application projections; consortium administrators can see more ledger data, and production needs an independently reviewed privacy topology. Timing, IP addresses, a compromised unlocked phone and identifying words typed into a free-text report remain risks.")
sources([
    ("apps/web/src/application/vault.js", "encryption, index reservation, matching, proof and backup logic"),
    ("sdk/src/patient.js; sdk/src/guardians.js", "commitment, permit and Shamir functions"),
    ("circuits/lotus_membership.circom", "precise private/public proof relation"),
    ("packages/domain/src/engine.js", "root, nullifier, proof and regional-release checks"),
])

role(3, "K. Jaideep Varma", "230968076", "Rule Enforcement & Verification",
     "Explain the business invariants as ledger rules: no unauthorized actor, invented stock, overspent permit, duplicate code or post-recall fill can produce a valid commit.")
h("Authorization and registration")
p("The operator approves organizations and registers actors. The chaincode binds each enrolled Fabric certificate to an actor ID, then checks active actor, role and organization for each command. A manufacturer may register a lot; a prescriber may issue a permit; a pharmacy may dispense; a regulator may recall. Failed authorization is a rejected transaction, not merely a hidden button.")
h("Custody and stock conservation")
p("Registration creates manufacturer stock. Shipping moves units from available or quarantine into in-transit. The named recipient must accept before those units enter its available or quarantine bucket; rejection restores the sender's source bucket. Expired or recalled units may move through return handling, not normal sales. Quarantine and documented shrinkage move stock into explicit non-sale buckets. For a pharmacy, the core closure check is <b>dispensed + returned + shrinkage &lt;= inbound accepted units</b>, with no bucket allowed to go negative.")
h("A fill is one atomic rule set")
bullets([
    "The lot exists, is unexpired, and has not been recalled; the permit exists and is unexpired.",
    "Permit namespace and product code equal the selected lot; keccak256 of the supplied permit secret equals the stored holder commitment.",
    "Any existing pharmacy binding is respected; quantity is positive and does not exceed the remaining permit balance.",
    "The patient commitment is a valid field element and has never appeared under <b>used:</b> before.",
    "The pharmacy has accepted this lot, has available stock, and closure remains within accepted inbound units.",
    "Only after all checks does the command decrement stock and permit balance, append a leaf/root and write the receipt. A batch accepts 1 to 50 fills and fails as a whole if any item fails.",
])
h("Recall and anonymous signals")
p("Only a regulator can issue a Class I, II or III recall for a lot, with reason and patient instructions. A second recall for that same lot is rejected; the lot's recall ID blocks later fills. For an anonymous acknowledgement or adverse-event report, the relay actor submits a real proof. Chaincode checks a known root, valid action/severity, network-specific topic, unused nullifier and proof validity. Acknowledgements increment the recall's count. Reports increment the lot's report count, and the configured threshold of three creates a SafetySignal event; it does not itself issue a recall.")
h("Verification strategy")
p("The retained Solidity suite covers access control, custody, closure, permit balance, duplicate commitments, recall blocking, real proofs and randomized hostile sequences. The current API tests cover the same shared domain behavior, including idempotency, rollback and scoped views. Fabric acceptance checks execute the real custody/dispense/recall flow and proof verification inside chaincode. Browser checks validate the human handoff and rejection paths. These are layered correctness checks; they do not prove freedom from every bug.")
sources([
    ("packages/domain/src/engine.js", "authoritative command handlers and invariant checks"),
    ("chaincode/lotus/index.cjs", "certificate binding and Fabric execution"),
    ("services/api/test/application.test.js; services/api/test/fabric.mjs", "API and Fabric acceptance"),
    ("contracts/test/Invariants.test.js; contracts/test/RealProof.test.js", "retained EVM rule and proof regression"),
])

role(4, "Dhruti P Shetty", "230968025", "Red Team / Adversary Simulation",
     "Explain what an attacker can observe or try, which tests resisted it, and which privacy risks remain even when the cryptography works.")
h("Assets, adversaries and assumptions")
p("The protected assets are patient-to-lot linkage, cross-fill unlinkability, root-secret custody, custody/dispense integrity and honest safety-signal counts. Threats include a passive ledger observer, a curious pharmacy or regulator, colluding guardians, a malicious staff actor and a relay or network observer. The model assumes cryptographic primitives hold and the patient's phone is not compromised while unlocked. A test result is always conditional on its attacker model.")
h("Adversary exercises")
table(["Case", "Attack", "Finding and boundary"], [
    ("A1", "Compare same-patient and different-patient commitments using Hamming-distance distributions.", "The modeled classifier did not find a useful commitment-only link. It does not model auxiliary metadata."),
    ("A2", "Observe a patient at a quiet counter and correlate the next ledger event.", "Historical simulation found about 94% unique with immediate posting versus about 2% with hourly batches at four fills/hour. Batching is not enforced as an automatic production policy."),
    ("A3", "Infer rare-drug recipients from tiny regional counts.", "Cells below five are suppressed; complementary suppression can hide another cell. Small-group attacks still require governance review."),
    ("A4", "Combine two guardian shares held by people who know the patient.", "Two shares reconstruct the secret by design. A personal guardian can reduce professional collusion; old shares cannot be forgotten."),
    ("A5-A7", "Spam reports, prove for an unreceived lot, or alter an action/report after proof creation.", "Nullifier uniqueness, membership proof and public signal binding reject the tested attempts."),
    ("A8-A10", "Inspect regulator fields, invent stock, or sell a recalled lot.", "Projection checks, custody/closure rules and recall blocking resisted the tested cases."),
], [15*mm, 75*mm, 86*mm])
h("How to read the evidence")
p("The Node red-team script runs seeded simulations for linkability, timing, small-region inference, guardian collusion, sybil behavior and regulator-view fields. Contract tests separately exercise invalid witnesses, altered signals, hostile stock sequences and recall blocking. The timing numbers describe a model with Poisson arrivals, a 30-second observation window and a quiet-pharmacy scenario; they are not a measured attack on live Fabric transactions.")
h("Residual risk and recommended controls")
bullets([
    "A pharmacy can connect the person at its own counter with that particular fill. Posting time and network IP can still reveal patterns beyond the commitment value.",
    "An unlocked compromised phone reveals the root secret. Two guardians can reconstruct it, so share placement and replacement procedures matter.",
    "A dishonest operator or consortium peer may observe more state than an ordinary public reader. Independent governance and privacy-preserving feed publication need deployment review.",
    "An incorrect physical pack scan gives a wrong lot even if the ledger transaction is internally valid. Scanning and operational controls remain necessary.",
])
sources([
    ("redteam/attacks.mjs; redteam/run-all.mjs", "implemented attack simulations and generated-report path"),
    ("docs/THREAT_MODEL.md", "historical attack narrative and assumptions"),
    ("contracts/test/RealProof.test.js; contracts/test/Invariants.test.js", "proof and stock attack checks"),
    ("docs/WEB_APPLICATION_GUIDE.md", "current privacy and deployment limits"),
])

role(5, "Ashmith C Shettigar", "230968023", "Measurement & Evaluation",
     "Separate three questions: does the integrated Fabric path commit, does the synthetic model target recalls better, and what did the older EVM prototype cost in gas?")
h("Metric definitions")
p("For recall targeting, <b>precision = true positives / (true positives + false positives)</b>: among people alerted, how many actually received the recalled lot? <b>Sensitivity = true positives / (true positives + false negatives)</b>: among actual recipients, how many were reached? A high precision claim means fewer unnecessary alarms; a high sensitivity claim means fewer missed recipients. The synthetic model knows ground truth because it generated the cohort; a deployed system does not automatically know real clinical reach.")
h("Current Fabric integration measurement")
p("The recorded Caliper 0.7.1 run used the isolated <b>lotus-tooling</b> channel on one host, one worker and one in-flight write. It measured 24 successful public-feed reads, 12 lot registrations and 12 fills, with zero failures in that final serial run. Reads were evaluated; writes waited for valid commit and stock was reconciled. The median read was about 26 ms; median register and fill latencies were about 1.06 s and 1.09 s respectively. This is a small integration sample, not a production TPS ceiling or a multi-site benchmark. An earlier contention exercise exposed MVCC conflicts, so the final fixture explicitly serialized shared-state writes.")
h("Synthetic recall study")
p("The deterministic generator models 40 demo drugs, six lots per drug, 1 to 6 fills per person, 60 pharmacies and a 15% chance of no linked drug-level record. The evaluation samples up to 30 lot recalls and sweeps 0, 5, 10 and 20% phone loss plus 0, 0.5, 1 and 2% wrong-lot recording. It assumes 80% guardian recovery among lost phones. The conventional baseline alerts everyone with a linked product-code record. LOTUS matches the exact lot, and a combined scenario counts conventional reach alongside LOTUS.")
table(["10,000-patient modeled scenario", "Precision", "Sensitivity"], [
    ("20% phone loss, 1% wrong lot: product-code baseline", "0.174", "0.858"),
    ("Same scenario: LOTUS exact-lot matching", "0.989", "0.951"),
    ("Same scenario: LOTUS plus existing channels", "0.990", "0.994"),
], [112*mm, 32*mm, 32*mm])
p("The combined-channel precision definition in the research script counts LOTUS's flagged set while conventional alerts contribute only added reach; it is not the precision of every combined alert a real service would send. Present that caveat when comparing methods. Scaling runs at 1,000, 10,000 and 100,000 synthetic patients show model behavior, not deployment performance.")
h("Historical EVM cost reference")
p("Brownie compiles and tests the retained Solidity contracts on an isolated local EVM. Its recorded transaction gas includes roughly 223,813 for lot registration, 144,816 for permit issue, 281,061 for a first-leaf fill and 167,479 for recall. A separate historical Hardhat study found mean dispense gas near 373,000 with a lean Merkle tree versus about 933,000 before that optimization. Fabric does not charge EVM gas; these figures are algorithm and migration references, not the operating cost of the current Fabric application.")
h("What remains unmeasured")
p("No independent consortium latency, sustained throughput, live SMS/Web Push delivery rate, real patient sensitivity, production key-ceremony audit or full Synthea x openFDA campaign is established by the recorded smoke and benchmark runs. Caliper results should retain run ID, source commit, SHA-256 inputs, channel, worker settings and timestamp so the audience can reproduce the claim's scope.")
sources([
    ("docs/toolchain-evidence.json", "recorded counts, Caliper latencies, Brownie gas and scope"),
    ("tools/caliper/workload.cjs; scripts/caliper-run.mjs", "benchmark operations and validity checks"),
    ("pipeline/evaluate.py; docs/REPORT.md", "synthetic definitions and historical outcome table"),
    ("tools/brownie/tests/test_migration_reference.py", "EVM regression and gas sample"),
])

role(6, "P Pattabhi Ram", "230968033", "Data Pipeline & Reproducibility",
     "Explain exactly where recall inputs and modeled patients came from, how experiments are regenerated, and why an imported notice is not automatically a ledger recall.")
h("Two separate data tracks")
p("The first track fetches openFDA drug enforcement events and NDC directory details. It stores fields such as recall number, classification, product description, reason, firm, report date, lot-text field, status and product NDC. The regulator's import flow retains the source record and digest, tries to resolve an exact product and lot, and leaves ambiguous scope unresolved. A regulator must make a separate authorized recall decision. Offline demo records in the shipped JSON are explicitly marked <b>sample: true</b> and must not be presented as live FDA data.")
p("The second track generates a synthetic cohort for research. Without Synthea input, a fixed-seed Python generator uses demo product codes, a skewed popularity distribution, multiple lots, pharmacies and regions. When a Synthea medications CSV is supplied, it uses its medication codes as identifiers, but the remaining fill/lot scenario is still modeled. The generated patients and outcomes are not clinical observations.")
h("Experiment recipe")
table(["Stage", "Input and output", "Reproducibility control"], [
    ("Cohort", "cohort.py makes patient/fill histories for a chosen count and seed.", "Default fixed seed 7; deterministic built-in generator."),
    ("Failure sweep", "evaluate.py injects phone loss, recovery and wrong-lot records; writes eval.csv and scaling.csv.", "Same seeded random stream and explicit scenario parameters."),
    ("Figures", "figures.py plots accuracy and other research results.", "Generated from recorded CSV outputs."),
    ("Manifest", "manifest.py runs deterministic steps and records SHA-256 per output.", "verify mode reruns and checks byte-for-byte agreement."),
    ("Source import", "openfda.py fetches current enforcement and NDC records.", "Network data may change; retain source payload and digest. It is not part of the deterministic manifest."),
], [27*mm, 79*mm, 70*mm])
h("Why provenance matters to a blockchain project")
p("A valid ledger transaction can still encode a wrong source record or a wrongly interpreted lot. The pipeline therefore keeps source fields and hashes, does not invent exact-lot scope when a notice is ambiguous, and makes the decision to recall an explicit regulator action. The replay sandbox is isolated from the live operational channel and compares product-code counts to exact-lot counts. Those counts represent dispense records, not unique people.")
h("Minimal reproduction commands")
bullets([
    "<b>python pipeline/cohort.py --patients 10000 --seed 7</b> generates the deterministic cohort.",
    "<b>python pipeline/evaluate.py --patients 10000 --recalls 30 --seed 7</b> regenerates the default accuracy and scaling CSVs.",
    "<b>python pipeline/manifest.py verify</b> reruns the named deterministic steps and compares SHA-256 hashes with the checked-in manifest.",
    "<b>python pipeline/openfda.py --limit 50</b> fetches current data when network access is available; its output will vary with the source and date.",
])
sources([
    ("pipeline/cohort.py; pipeline/evaluate.py", "cohort assumptions, truth sets, failure sweeps and metrics"),
    ("pipeline/manifest.py; pipeline/MANIFEST.json", "reproduction recipe and recorded file digests"),
    ("pipeline/openfda.py; sdk/src/fda.js", "source retrieval and lot parsing"),
    ("docs/WEB_APPLICATION_GUIDE.md", "import and isolated replay behavior"),
])

role(7, "Puripanda Venkata Praneeth", "230957112", "Patient-Side Product",
     "Show that every patient screen corresponds to a privacy or ledger decision, from permit QR to signed receipt to locally matched recall.")
h("The patient journey")
table(["Patient action", "What the phone does", "Blockchain meaning"], [
    ("Create/unlock vault", "Generates or decrypts root secret and local history.", "Identity remains off the ledger."),
    ("Import permit QR", "Saves permit ID, secret, product and network in the encrypted vault.", "The ledger holds an expiring balance and holder hash."),
    ("Show counter code", "Reserves an index, saves it, then shows a fresh commitment and permit credential.", "Pharmacy may request one atomic exact-lot fill."),
    ("Import receipt", "Checks the signed committed receipt and saves the exact lot and index.", "Handover becomes a durable, verifiable record."),
    ("Check recalls", "Fetches broad public bulletin and compares its leaves with locally derived commitments.", "The patient self-identifies; no central patient list is created."),
    ("Respond privately", "Builds a real proof and submits an acknowledgement or encrypted safety report.", "Ledger verifies eligibility and one-use nullifier without a name."),
], [31*mm, 78*mm, 67*mm])
h("Important interaction details")
p("The patient interface is a phone-oriented installable PWA, not a native app. It supports camera QR scanning with a paste fallback. A phone displays its counter code to the pharmacy's scanner; after a committed fill, the phone scans the pharmacy's detailed receipt. A code is not a fill by itself. The pharmacy must receive a valid commit before handing over medicine. The app rejects altered receipt data and wrong network context. Prescriptions and issued indices remain inside the encrypted vault.")
h("Recall and proof experience")
p("The public recall bulletin can be seen before vault unlock. Once unlocked, <b>Check now</b> recomputes the patient's issued commitments and identifies any leaf in a recalled lot. Only a matched receipt enables the anonymous acknowledgement action. Proof generation uses the browser's wasm/zkey files; the server relays the proof, and chaincode verifies it. A side-effect narrative is encrypted to the safety recipient before upload, while the proof binds its digest and severity. The safety recipient may read the narrative; the ledger stores a digest/reference and count.")
h("Offline, recovery and accessibility boundaries")
p("The service worker caches the app shell, route assets and proof files. The browser also retains encrypted vault data and the last completed bulletin. Offline matching is visibly marked stale; it is not a current safety check, and new transactions need a connection. The app supports English, Hindi, Kannada and Telugu alert text, but complete localization and native-speaker review remain. Private checks occur while the app is open and unlocked; guaranteed closed-browser delivery is not implemented. Conventional recall channels continue in parallel.")
sources([
    ("apps/web/src/application/PatientWeb.jsx", "patient journey and alert/proof controls"),
    ("apps/web/src/application/vault.js", "vault, index allocation, matching and proof inputs"),
    ("apps/web/public/sw.js; apps/web/src/components/QrScanner.jsx", "offline shell and scanning"),
    ("apps/web/e2e/application.mjs", "browser acceptance and phone-layout checks"),
])

role(8, "K. Poorna Sai Praneeth", "230968248", "Integration & Deployment",
     "Explain the tested end-to-end stack, how each service is connected, how to reproduce a safe demo, and exactly where production work begins.")
h("Operational topology")
p("The current start profile uses Fabric as the authoritative business ledger, FireFly Core and two FabConnect connections for normal command/event transport, Gateway for transient permit credentials, and loopback Kubo IPFS for encrypted documents. The API authenticates staff and selects the correct certificate; the patient PWA consumes public feeds and submits anonymous proofs. The two Fabric organizations, orderer, FireFly processes, API and IPFS node run in one prepared WSL/Windows integration environment. Separate operations, tooling and acceptance channels prevent benchmark stock from becoming live demo stock.")
h("A full integration path")
bullets([
    "Manufacturer uploads a certificate or manifest: API encrypts bytes with AES-GCM, sends ciphertext to IPFS, and commits CID plus original and ciphertext SHA-256 digests. Authorized download verifies both digests before use.",
    "Operator invites staff and binds each actor to a distinct enrolled certificate. Manufacturing/distribution actors use the local Org2 pool; care/safety actors use Org1 in this integration setup.",
    "Normal commands go to FireFly's contract API, then FabConnect and Fabric; commit events return to FireFly. A command result is reconciled against Fabric using request ID, actor and digest.",
    "Fill and transfer commands route permit credentials through Gateway transient data. They are not copied into FireFly's persisted operation arguments.",
    "If Fabric, FireFly or configured IPFS is unavailable, the application shows failure. It never silently changes to a local SQLite ledger. The explicit local mode is a separate development authority.",
])
h("Coursework runbook and verification")
p("On the prepared machine, Node 22.13+ and the local runtimes are prerequisites. From the repository root, run <b>npm ci</b>, <b>npm run build</b>, then <b>npm start</b>. The app opens on localhost port 8787, with patient entry at <b>/patient</b>, staff at <b>/login</b>, public lookup at <b>/verify</b> and guardians at <b>/guardian</b>. First-run operator setup chooses credentials; demo inventory is not present in a normal empty profile. The separate <b>npm run demo:seed</b> command prepares fictional demonstration stock and preserves prior ledger history. A phone needs trusted HTTPS access and its own browser vault; localhost on the laptop is not a phone URL.")
p("Verification commands are <b>npm test</b> for Solidity/SDK/API reference suites, <b>npm run test:browser</b> for application journeys, <b>npm run test:fabric</b> for real Fabric acceptance, <b>npm run test:firefly</b> and <b>npm run test:ipfs</b> for their integrations, and <b>npm run bench:caliper</b> for the isolated performance run. Brownie is run separately for the historical Solidity regression and gas reference. The recorded evidence snapshot contains 37 contract, 4 SDK, 13 API, 40 application-browser, 25 FireFly, 7 IPFS, 9 first-run and 7 operational-browser checks; those are recorded results, not a claim of a fresh run today.")
h("Deployment gates")
p("Production needs independently managed peers/orderers, certificate authority enrollment and key custody, stronger regulator and feed privacy controls, a trusted time policy, reviewed proof setup, scalable queries and storage retention, backups, notification delivery providers, complete localization and broader load/real-world delivery measurement. The current static endorsement rule and pre-generated identity pool are local integration choices. A browser being closed can delay private matching; FireFly event indexing alone does not deliver a patient alert.")
sources([
    ("docs/TOOLCHAIN_MIGRATION.md; docs/WEB_APPLICATION_GUIDE.md", "stack configuration, accepted tests and remaining gates"),
    ("services/api/src/fabric.js; services/api/src/firefly.js; services/api/src/ipfs.js", "actual transport and encrypted document adapters"),
    ("scripts/start-fabric.mjs; scripts/fabric-native.sh", "startup and network"),
    ("docs/toolchain-evidence.json", "recorded test and benchmark snapshot"),
])

story.append(PageBreak())
story.append(P("Shared viva questions", "SectionLotus"))
table(["Question", "Short, accurate answer"], [
    ("Why blockchain?", "Separate organizations need one ordered, auditable custody and dispense state with shared rule enforcement and patient-verifiable public facts."),
    ("What is on-chain?", "Lot/custody/permit balances and holder hashes, commitments/roots, recalls, response nullifiers and counts, plus document references and digests."),
    ("What stays private?", "The root secret and permit credential in the phone vault; permit credential enters a Fabric proposal only as transient data. Encrypted document bytes live off-chain."),
    ("How is stock fraud stopped?", "Only accepted shipments create usable downstream stock; one transaction checks available quantity and closure against accepted inbound stock."),
    ("Why a zero-knowledge proof?", "It verifies membership in the recalled lot's commitment tree without revealing which receipt leaf is the patient's."),
    ("What stops duplicate reports?", "A topic-scoped nullifier derived from the root secret is accepted once; duplicate values are rejected."),
    ("What does Caliper show?", "A small, one-host Fabric integration run with valid commit latencies and reconciled stock, not a production throughput claim."),
    ("What does Brownie show?", "Historical Solidity/EVM regression behavior and gas costs. Fabric has no EVM gas."),
    ("Does a QR prove a genuine pack?", "It checks registered ledger data for a code/lot. Physical authentication and correct scanning still need operational controls."),
    ("Will a closed phone always receive a recall?", "No. The current app checks privately while open and unlocked; conventional recall channels must continue."),
], [53*mm, 123*mm])
h("Terms to remember")
bullets([
    "<b>Lot:</b> one manufacturer batch, distinguished from the broader drug/product code.",
    "<b>Custody:</b> sender-to-recipient transfer, completed by recipient acceptance.",
    "<b>Commitment:</b> a one-time public value derived from the patient's private secret and index.",
    "<b>Merkle root:</b> one digest committing to the ordered set of fill commitments for a lot segment.",
    "<b>Nullifier:</b> a topic-specific one-use tag that prevents duplicate anonymous responses.",
    "<b>Transient data:</b> Fabric proposal data available for chaincode validation without being recorded as ordinary transaction arguments in the ledger block.",
    "<b>CID:</b> content identifier used to locate IPFS ciphertext; the ledger also anchors digests for byte checks.",
])
callout("Presentation rule.", "Say 'tested local Fabric integration' for the current application, 'modeled synthetic outcome' for notification accuracy, and 'historical EVM reference' for gas. This keeps all three evidence types honest and understandable.")


class Document(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(str(filename), pagesize=A4, leftMargin=17*mm, rightMargin=17*mm,
                         topMargin=19*mm, bottomMargin=18*mm, title="LOTUS Blockchain Coursework Team Guide",
                         author="LOTUS project team", subject="Role-based blockchain architecture and implementation guide")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, leftPadding=0,
                      rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(17*mm, 16*mm, 193*mm, 16*mm)
        canvas.setFont("Arial", 7.3)
        canvas.setFillColor(GREY)
        canvas.drawString(17*mm, 11.5*mm, "LOTUS | Blockchain coursework")
        canvas.drawRightString(193*mm, 11.5*mm, str(doc.page))
        if doc.page > 1:
            canvas.setFont("Arial-Bold", 7.4)
            canvas.setFillColor(TEAL)
            canvas.drawString(17*mm, 286*mm, "TEAM GUIDE")
        canvas.restoreState()


Document(OUT).build(story)
print(OUT)
