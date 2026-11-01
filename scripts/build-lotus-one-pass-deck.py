"""Reorder LOTUS slides into one continuous stage turn per presenter.

Adds three topic slides so the data, privacy and deployment owners have a
visible slide for their own work, then writes a slide-wise speaking guide.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "presentation"
BASE = OUT / "LOTUS_Research_Presentation_With_Speaker_Notes.pptx"
FINAL = OUT / "LOTUS_One_Pass_Presentation.pptx"
GUIDE = OUT / "LOTUS_One_Pass_Speaker_Script.md"

prs = Presentation(BASE)
assert len(prs.slides) == 24, "Expected the 24-slide LOTUS deck"

BG = RGBColor(248, 248, 242)
INK = RGBColor(17, 52, 48)
GREEN = RGBColor(30, 91, 73)
MINT = RGBColor(219, 235, 220)
LIME = RGBColor(179, 211, 160)
CORAL = RGBColor(195, 80, 61)
GOLD = RGBColor(229, 178, 61)
PALE_GOLD = RGBColor(251, 242, 213)
GRAY = RGBColor(91, 106, 99)
LINE = RGBColor(192, 207, 195)
WHITE = RGBColor(255, 255, 255)


def box(slide, x, y, w, h, fill=WHITE, border=None, rounded=False):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if border:
        sh.line.color.rgb = border; sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    if rounded:
        try: sh.adjustments[0] = 0.12
        except Exception: pass
    return sh


def txt(slide, words, x, y, w, h, size=18, color=INK, bold=False, align=None):
    sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = sh.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, part in enumerate(words.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = part; p.font.name = "Aptos"; p.font.size = Pt(size)
        p.font.color.rgb = color; p.font.bold = bold
        if align is not None: p.alignment = align
    return sh


def stroke(slide, x1, y1, x2, y2, color=LINE, width=1.4):
    sh = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    sh.line.color.rgb = color; sh.line.width = Pt(width)
    return sh


def new_topic(title, source, section):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    box(sl, 0, 0, 13.333, 7.5, BG)
    box(sl, 0, 0, 0.18, 7.5, GREEN)
    txt(sl, title, 0.66, 0.32, 11.9, 0.55, 29, INK, True)
    stroke(sl, 0.66, 1.02, 12.67, 1.02, LINE, 1)
    txt(sl, source, 0.69, 6.88, 11.45, 0.20, 8, GRAY)
    txt(sl, section.upper(), 0.69, 7.12, 8.80, 0.18, 9, GRAY, True)
    txt(sl, "00", 12.35, 7.05, 0.32, 0.24, 10, GREEN, True, PP_ALIGN.RIGHT)
    return sl


def card(sl, title, body, x, y, w, h, accent=GREEN, fill=WHITE):
    box(sl, x, y, w, h, fill, LINE, True)
    box(sl, x, y, 0.08, h, accent)
    txt(sl, title, x+0.24, y+0.20, w-0.47, 0.37, 18, accent, True)
    txt(sl, body, x+0.24, y+0.69, w-0.47, h-0.90, 15, INK)


# Added after the original slides, then moved into the correct topic blocks.
pipeline = new_topic("Research pipeline and reproducibility", "Source: pipeline/README.md; pipeline/MANIFEST.json; docs/REPORT.md", "Literature survey")
steps = [
    ("Cohort", "Deterministic synthetic patients\nand medicine fills"),
    ("Recall scenarios", "Exact-lot recalls with phone-loss\nand recording-error sweeps"),
    ("Manifest", "Inputs and hashes retained\nfor repeatable runs"),
    ("Figures", "Precision, sensitivity and\nscaling comparisons"),
]
for i, (head, body) in enumerate(steps):
    x = 0.79 + i*3.15
    card(pipeline, head, body, x, 2.18, 2.86, 2.44, [GREEN, CORAL, GOLD, GREEN][i])
    if i < 3:
        stroke(pipeline, x+2.89, 3.38, x+3.12, 3.38, GREEN, 2)
txt(pipeline, "The pipeline is research evidence. Its simulated outcomes are separate from the current Fabric integration tests.", 1.05, 5.44, 11.23, 0.64, 18, GREEN, True, PP_ALIGN.CENTER)

privacy = new_topic("Privacy and key custody", "Source: docs/WEB_APPLICATION_GUIDE.md, Patient privacy and recovery", "Framework")
card(privacy, "Private vault", "The root secret and permit credentials stay in an AES-GCM encrypted browser vault.", 0.82, 1.52, 5.78, 1.86, GREEN)
card(privacy, "Fresh commitments", "A new commitment for each fill prevents a reusable patient key from appearing in the shared record.", 6.77, 1.52, 5.77, 1.86, CORAL)
card(privacy, "Two-of-three Guardians", "Separate Guardian shares can restore the root secret after phone loss.", 0.82, 3.71, 5.78, 1.86, GOLD)
card(privacy, "Encrypted backup", "A separate backup restores receipts, permits and issued-code history.", 6.77, 3.71, 5.77, 1.86, GREEN)
txt(privacy, "The phone matches recalls locally and generates an anonymous proof for an eligible response.", 1.03, 6.04, 11.23, 0.45, 17, GREEN, True, PP_ALIGN.CENTER)

integration = new_topic("Operational integration and deployment boundary", "Source: docs/TOOLCHAIN_MIGRATION.md; docs/WEB_APPLICATION_GUIDE.md", "Conclusion and future scope")
card(integration, "Ordinary commands", "FireFly and FabConnect submit authorized staff actions and index committed Fabric events.", 0.79, 1.48, 5.88, 1.81, GREEN)
card(integration, "Private credentials", "Fabric Gateway transient data carries permit credentials without storing them in FireFly operations.", 6.81, 1.48, 5.73, 1.81, CORAL)
card(integration, "Encrypted documents", "IPFS stores ciphertext; Fabric keeps the CID and content digests.", 0.79, 3.62, 5.88, 1.81, GOLD)
card(integration, "Deployment boundary", "The two-organization network runs on one host; independent administration and delivery integration remain future work.", 6.81, 3.62, 5.73, 1.81, GREEN)

# New slide order: each presenter has exactly one contiguous stage turn.
# Values 1-24 refer to the previous deck, 25-27 are the new topic slides.
new_order = [
    1, 2, 3, 4, 5, 6, 25,          # Pattabhi
    7, 8, 11,                     # Avinash
    9, 10, 12,                    # Jaideep
    26,                           # Abhinav
    14,                           # Puripanda Venkata Praneeth
    17,                           # Dhruti
    13, 15, 16, 18, 19,          # Ashmith
    27, 20, 21, 22, 23, 24,     # Poorna Sai Praneeth
]
assert len(new_order) == 27 and sorted(new_order) == list(range(1, 28))
ids = list(prs.slides._sldIdLst)
for el in ids: prs.slides._sldIdLst.remove(el)
for old_no in new_order: prs.slides._sldIdLst.append(ids[old_no-1])

# Speaker and presentation-ready notes in the new, sequential slide order.
slides = [
    ("P Pattabhi Ram", "LOTUS: lot-oriented medicine traceability and a private recall response. I will frame the research question, then each teammate will explain the part they worked on."),
    ("P Pattabhi Ram", "We will move from the problem and literature to the framework, rules, privacy, patient experience, adversarial tests, measurements and deployment implications."),
    ("P Pattabhi Ram", "The research starts at the pharmacy-to-patient handoff. Upstream systems can trace a lot to a pharmacy, but a patient record may contain only a medicine code. That makes recall targeting imprecise."),
    ("P Pattabhi Ram", "We ask whether an exact-lot fill can be verified without publishing patient identity, and whether that record can improve recall targeting. The evaluation pipeline turns these into controlled comparisons."),
    ("P Pattabhi Ram", "Traceability standards, healthcare ledgers and privacy proofs each address part of the problem. We reviewed where they stop short of linking a medicine lot to a private patient receipt."),
    ("P Pattabhi Ram", "The missing link is the final handoff. To study it reproducibly, we modelled exact-lot recalls and drug-code matching under the same patient and failure scenarios."),
    ("P Pattabhi Ram", "Our pipeline creates deterministic synthetic cohorts, applies recall, phone-loss and lot-error scenarios, and records a manifest so the figures can be regenerated. These modeled outcomes are separate from later Fabric integration measurements."),
    ("Patoju Sai Avinash", "That last-hop gap shapes the ledger framework. Read the four layers top to bottom: blockchain, chaincode rules, transaction data and stakeholders. The stages run from lot registration through private recall response and public verification."),
    ("Patoju Sai Avinash", "Fabric is the operational shared ledger. FireFly carries ordinary commands, Gateway transient data carries private permit credentials, IPFS holds encrypted documents, and the patient phone holds its root secret."),
    ("Patoju Sai Avinash", "The architecture is implemented with Fabric chaincode, FireFly/FabConnect, encrypted IPFS and a patient PWA. Caliper measures the local Fabric path; Brownie is a separate historical EVM reference."),
    ("K. Jaideep Varma", "A staff role authorizes action, and shipping alone does not create usable stock. The distributor or pharmacy must accept the shipment before the ledger updates available inventory."),
    ("K. Jaideep Varma", "During a fill, LOTUS checks product, lot, expiry, recall state, accepted stock, permit balance and commitment uniqueness in one transaction. A recall blocks later fills from that lot. The patient response in the right-hand diagram will be explained in the privacy section next."),
    ("K. Jaideep Varma", "We tested these rules through contract, API and browser checks. The cases include wrong roles, duplicate commitments, missing stock, invalid permits and failed batch rollback. The counts establish behavior in the tested environments."),
    ("Adabala Venkata Abhinav", "A valid ledger record must still protect the patient's identity. The root secret and permit credentials stay in an encrypted browser vault; every fill uses a fresh commitment. A two-of-three Guardian scheme restores the secret after phone loss, while an encrypted backup restores receipts and permit history. The phone matches recalls locally and proves eligibility without disclosing its receipt."),
    ("Puripanda Venkata Praneeth", "The patient sees those privacy choices as a simple phone flow: import a QR permit, show a one-time counter code, scan a signed receipt, and check public recalls against the local vault. A matched patient can send an anonymous acknowledgement. Closed-browser delivery remains future work."),
    ("Dhruti P Shetty", "We then tested what an adversary could still infer. In a historical quiet-pharmacy simulation, immediate submission made 94% of dispenses identifiable by timing; hourly batching reduced that modeled figure to 2%. We also examined linkability, small regional counts and Guardian collusion."),
    ("Ashmith C Shettigar", "With implementation and adversarial boundaries established, we measured the Fabric path. One worker completed 24 reads, 12 lot registrations and 12 fills with zero failures. Median writes took about 1.1 seconds including valid commit; this is a single-host integration result, not a production throughput ceiling."),
    ("Ashmith C Shettigar", "The synthetic recall study asks a different question: targeting accuracy. At 20% phone loss and 1% lot-recording errors, LOTUS plus existing channels had modeled sensitivity of 0.994 versus 0.858 for drug-code matching."),
    ("Ashmith C Shettigar", "The reproducible scenarios scale from 1,000 to 100,000 synthetic patients. Under 10% phone loss and 1% lot error, LOTUS precision remains around 0.98 to 0.99. These numbers are model outputs, not measured clinical delivery."),
    ("Ashmith C Shettigar", "Fabric does not charge EVM gas. The Brownie values belong to our retained Solidity prototype and should not be presented as current Fabric costs."),
    ("Ashmith C Shettigar", "In that historical EVM prototype, a lean Merkle tree reduced mean dispense gas from about 933,000 to 373,000. The graph describes that optimization, while the Caliper slide describes the present Fabric path."),
    ("K. Poorna Sai Praneeth", "Those results sit inside a specific operational boundary. FireFly submits ordinary commands, Gateway transient data protects permit credentials, IPFS stores encrypted documents, and Fabric records the authoritative result. The supplied network is a single-host integration with two configured organizations."),
    ("K. Poorna Sai Praneeth", "Together, the rules and local tests establish an exact-lot transaction flow. The research simulation supports more targeted recalls, while the integration checks prove that the current components work together. Real delivery outcomes remain unmeasured."),
    ("K. Poorna Sai Praneeth", "LOTUS demonstrates a verifiable path from lot creation to a private patient response. The scope of this conclusion is a tested local integration and separate synthetic evaluation, not an independently operated production consortium."),
    ("K. Poorna Sai Praneeth", "Production requires independently administered peers and identities, reviewed key custody, stronger feed privacy, notification-provider integration and broader load and delivery measurement."),
    ("K. Poorna Sai Praneeth", "These sources cover traceability, cryptographic methods and the implementation. The historical research report and the current Fabric migration evidence are kept separate throughout our discussion."),
    ("K. Poorna Sai Praneeth", "Thank you. We welcome your questions."),
]
assert len(slides) == len(prs.slides)

for no, (sl, (speaker, words)) in enumerate(zip(prs.slides, slides), 1):
    sl.notes_slide.notes_text_frame.text = f"Speaker: {speaker}\n\n{words}\n\nThe presenter enters once and remains for this contiguous topic block."
    for shape in sl.shapes:
        if not shape.has_text_frame or abs(shape.left - Inches(12.35)) > Inches(0.04) or abs(shape.top - Inches(7.05)) > Inches(0.04):
            continue
        runs = shape.text_frame.paragraphs[0].runs
        if runs: runs[0].text = f"{no:02d}"

prs.save(FINAL)

lines = [
    "# LOTUS presentation: one stage turn per speaker",
    "",
    "The deck has 27 slides. Title and agenda are assigned to the opening speaker but omitted below, as requested. Each person enters once for one continuous block.",
    "",
    "| Slides | Speaker | Topic block |",
    "| --- | --- | --- |",
    "| 1-7 | P Pattabhi Ram | Research problem, literature and reproducible pipeline |",
    "| 8-10 | Patoju Sai Avinash | Ledger framework and architecture |",
    "| 11-13 | K. Jaideep Varma | Rules and verification |",
    "| 14 | Adabala Venkata Abhinav | Privacy and key custody |",
    "| 15 | Puripanda Venkata Praneeth | Patient-side product |",
    "| 16 | Dhruti P Shetty | Adversary simulation |",
    "| 17-21 | Ashmith C Shettigar | Measurement and evaluation |",
    "| 22-27 | K. Poorna Sai Praneeth | Integration, conclusions and deployment |",
    "",
    "## Slide-wise script",
    "",
]
for no, (speaker, words) in enumerate(slides, 1):
    if no <= 2: continue
    lines += [f"### Slide {no} — {speaker}", "", f'“{words}”', ""]
GUIDE.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {FINAL} ({len(prs.slides)} slides) and {GUIDE}")
