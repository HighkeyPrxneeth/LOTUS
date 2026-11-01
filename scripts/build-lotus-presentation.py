"""Build the LOTUS research presentation from checked project evidence.

Run with the Codex primary runtime Python, which includes python-pptx and Pillow.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_THEME_COLOR
from PIL import Image, ImageDraw, ImageFont
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "presentation"
OUT.mkdir(parents=True, exist_ok=True)
EVIDENCE = json.loads((ROOT / "docs" / "toolchain-evidence.json").read_text(encoding="utf-8"))

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

BG = RGBColor(248, 248, 242)
INK = RGBColor(17, 52, 48)
GREEN = RGBColor(30, 91, 73)
MINT = RGBColor(219, 235, 220)
LIME = RGBColor(179, 211, 160)
CORAL = RGBColor(195, 80, 61)
PALE_CORAL = RGBColor(250, 232, 223)
GOLD = RGBColor(229, 178, 61)
PALE_GOLD = RGBColor(251, 242, 213)
GRAY = RGBColor(91, 106, 99)
LINE = RGBColor(192, 207, 195)
WHITE = RGBColor(255, 255, 255)


def rect(slide, x, y, w, h, fill=None, line=None, radius=False, lw=1):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill or BG
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    else:
        sh.line.fill.background()
    if radius:
        try:
            sh.adjustments[0] = 0.14
        except Exception:
            pass
    return sh


def text(slide, content, x, y, w, h, size=18, color=INK, bold=False, align=None,
         font="Aptos", margin=0, valign=MSO_ANCHOR.MIDDLE):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.015)
    tf.vertical_anchor = valign
    for i, part in enumerate(str(content).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = part
        p.font.name = font
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        if align is not None:
            p.alignment = align
    return box


def line(slide, x1, y1, x2, y2, color=LINE, lw=1.5, arrow=False, dash=None):
    sh = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    sh.line.color.rgb = color
    sh.line.width = Pt(lw)
    if dash:
        sh.line.dash_style = dash
    if arrow:
        # Arrowheads remain editable in PowerPoint.
        from pptx.oxml.xmlchemy import OxmlElement
        ln = sh._element.spPr.get_or_add_ln()
        tail = OxmlElement("a:tailEnd")
        tail.set("type", "triangle")
        ln.append(tail)
    return sh


def new_slide(title=None, section=None, source=None):
    slide = prs.slides.add_slide(blank)
    rect(slide, 0, 0, 13.333, 7.5, BG)
    rect(slide, 0, 0, 0.18, 7.5, GREEN)
    if title:
        text(slide, title, 0.66, 0.32, 11.9, 0.55, 29, INK, True)
        line(slide, 0.66, 1.02, 12.67, 1.02, LINE, 1)
    if section:
        text(slide, section.upper(), 0.69, 7.12, 8.8, 0.18, 9, GRAY, True)
    if source:
        text(slide, source, 0.69, 6.88, 11.45, 0.2, 8, GRAY)
    text(slide, f"{len(prs.slides):02d}", 12.35, 7.05, 0.32, 0.24, 10, GREEN, True, PP_ALIGN.RIGHT)
    return slide


def label(slide, s, x, y, w, color=GREEN, fill=MINT, size=12):
    rect(slide, x, y, w, 0.35, fill, radius=True)
    text(slide, s, x+0.05, y+0.01, w-0.1, 0.32, size, color, True, PP_ALIGN.CENTER)


def bullet(slide, s, x, y, w, size=18, color=INK):
    rect(slide, x, y+0.12, 0.09, 0.09, CORAL)
    text(slide, s, x+0.24, y, w-0.24, 0.64, size, color)


def image_fit(slide, path, x, y, w, h):
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w/iw, h/ih)
    nw, nh = iw*scale, ih*scale
    slide.shapes.add_picture(str(path), Inches(x+(w-nw)/2), Inches(y+(h-nh)/2), width=Inches(nw), height=Inches(nh))


def pill(slide, s, x, y, w, fill=GREEN, color=WHITE):
    rect(slide, x, y, w, 0.46, fill, radius=True)
    text(slide, s, x+0.09, y+0.01, w-0.18, 0.42, 14, color, True, PP_ALIGN.CENTER)


def card(slide, title, body, x, y, w, h, accent=GREEN, fill=WHITE):
    rect(slide, x, y, w, h, fill, LINE, radius=True)
    rect(slide, x, y, 0.08, h, accent)
    text(slide, title, x+0.26, y+0.19, w-0.48, 0.36, 17, accent, True)
    text(slide, body, x+0.26, y+0.65, w-0.48, h-0.85, 15, INK, valign=MSO_ANCHOR.TOP)


def sequence_panel(slide, title, x, y, w, h, actors, messages):
    rect(slide, x, y, w, h, WHITE, LINE, radius=True)
    text(slide, title, x+0.22, y+0.12, w-0.44, 0.34, 16, GREEN, True)
    inner_l, inner_r = x+0.70, x+w-0.70
    centers = [inner_l+i*(inner_r-inner_l)/(len(actors)-1) for i in range(len(actors))]
    for c, actor in zip(centers, actors):
        rect(slide, c-0.55, y+0.58, 1.10, 0.58, MINT, GREEN, radius=True)
        text(slide, actor, c-0.50, y+0.61, 1.00, 0.50, 10, INK, True, PP_ALIGN.CENTER)
        line(slide, c, y+1.19, c, y+h-0.25, LINE, 1)
    space = (h-1.62)/max(len(messages),1)
    for j, (src, dst, msg) in enumerate(messages):
        yy = y+1.44+j*space
        x1, x2 = centers[src], centers[dst]
        if src == dst:
            rect(slide, x1-0.64, yy-0.10, 1.28, 0.44, PALE_GOLD, GOLD, radius=True)
            text(slide, msg, x1-0.59, yy-0.07, 1.18, 0.35, 9.2, INK, align=PP_ALIGN.CENTER)
        else:
            line(slide, x1, yy+0.16, x2, yy+0.16, GREEN, 1.4, arrow=True)
            text(slide, msg, min(x1,x2)+0.02, yy-0.09, abs(x2-x1)-0.04, 0.25, 9.6, INK, align=PP_ALIGN.CENTER)


# 1. Cover
s = new_slide()
rect(s, 0.18, 0, 13.153, 7.5, INK)
rect(s, 9.95, 0, 3.38, 7.5, GREEN)
for i, yy in enumerate([1.45, 2.35, 3.25, 4.15, 5.05]):
    rect(s, 10.30, yy, 0.70, 0.52, MINT if i%2==0 else LIME, radius=True)
    if i<4: line(s, 11.04, yy+0.26, 11.57, yy+1.16, LIME, 2)
text(s, "LOTUS", 0.85, 0.72, 7.8, 1.0, 58, WHITE, True)
text(s, "Lot-oriented medicine traceability\nand private recall response", 0.88, 2.04, 8.65, 1.50, 30, WHITE)
text(s, "Research presentation  |  Manipal Institute of Technology", 0.9, 5.55, 8.2, 0.36, 16, LIME)
text(s, "Patoju Sai Avinash · Adabala Venkata Abhinav · K. Jaideep Varma · Dhruti P Shetty\nAshmith C Shettigar · P Pattabhi Ram · Puripanda Venkata Praneeth · K. Poorna Sai Praneeth", 0.9, 6.06, 8.9, 0.77, 11, WHITE)

# 2. Agenda
s = new_slide("Agenda", "Outline")
agenda = ["Introduction", "Research questions and objectives", "Literature survey", "LOTUS framework and process flows", "Implementation framework", "Results and discussion", "Conclusion and future scope", "References"]
for i,a in enumerate(agenda):
    col, row = divmod(i, 4)
    x, y = 0.85+col*6.1, 1.46+row*1.22
    text(s, f"0{i+1}", x, y, 0.48, 0.33, 14, CORAL, True)
    text(s, a, x+0.55, y-0.04, 5.1, 0.56, 20, INK, True)
    line(s, x, y+0.72, x+5.45, y+0.72, LINE)

# 3. Introduction
s = new_slide("Introduction", "Problem", "Source: LOTUS report and current web application guide")
text(s, "The last handoff is the blind spot", 0.84, 1.37, 10.5, 0.48, 26, GREEN, True)
for i,(head,body) in enumerate([
    ("Tracked upstream", "Manufacturers and distributors record product lots and custody."),
    ("Ambiguous at dispensing", "A patient record may contain the drug code without the exact lot."),
    ("Broad or missed alerts", "A drug-wide alert reaches unaffected people and can miss actual recipients."),
]):
    card(s, head, body, 0.84+i*4.16, 2.25, 3.83, 2.52, [GREEN,CORAL,GOLD][i])
pill(s, "LOTUS closes the pharmacy-to-patient handoff", 2.15, 5.32, 9.03, GREEN)
text(s, "It records a verifiable lot receipt while the patient's identifying secret remains on the phone.", 2.22, 5.98, 8.92, 0.45, 18, INK, align=PP_ALIGN.CENTER)

# 4. Research questions/objectives
s = new_slide("Research questions and objectives", "Research framing")
card(s, "RQ1", "How can a medicine lot be followed through dispensing without publishing patient identity?", 0.78, 1.40, 5.8, 1.66, GREEN)
card(s, "RQ2", "Can exact-lot, private matching improve recall targeting while preserving a verifiable response count?", 6.75, 1.40, 5.8, 1.66, CORAL)
text(s, "Objectives", 0.83, 3.62, 3.0, 0.43, 22, GREEN, True)
for i,t in enumerate(["Record accepted custody and enforce available stock", "Issue expiring permits and commit exact-lot fills", "Let the phone match recalls locally and acknowledge anonymously"]):
    bullet(s, t, 0.87, 4.18+i*0.67, 11.6, 18)

# 5. Literature survey
s = new_slide("Literature survey", "Related work", "Sources: FDA DSCSA; GS1 EPCIS 2.0; MedRec; MediLedger; LOTUS report references")
cols = [("Drug traceability", "DSCSA / EPCIS", "Product-level serialization, verification and event exchange"),
        ("Health data access", "MedRec", "Blockchain permissions for health records"),
        ("Industry ledger", "MediLedger", "Cross-organization pharmaceutical verification"),
        ("Private proof", "Poseidon / Groth16", "Membership proof without revealing the patient leaf")]
for i,(a,b,c) in enumerate(cols):
    x=0.8+(i%2)*6.18; y=1.42+(i//2)*2.24
    card(s,a,c,x,y,5.87,1.91,[GREEN,CORAL,GOLD,GREEN][i])
    label(s,b,x+3.28,y+0.19,2.24,fill=PALE_GOLD if i>1 else MINT,size=10)

# 6. literature gap / process
s = new_slide("Literature survey: the remaining gap", "Related work")
text(s, "Existing systems focus on the pack and the organization.\nLOTUS extends the verified path to a private patient receipt.", 0.82, 1.35, 11.75, 0.9, 25, GREEN, True)
stages=[("Manufacturer", "Lot + certificate"),("Distributor", "Ship + accept"),("Pharmacy", "Received stock"),("Patient", "Exact-lot receipt")]
for i,(a,b) in enumerate(stages):
    x=0.92+i*3.17
    rect(s,x,3.1,2.65,1.6,WHITE,LINE,radius=True)
    label(s,a,x+0.20,3.35,2.25,size=12)
    text(s,b,x+0.20,4.02,2.25,0.42,15,INK,align=PP_ALIGN.CENTER)
    if i<3: line(s,x+2.66,3.90,x+3.13,3.90,GREEN,2,arrow=True)
rect(s,10.43,2.93,0.08,1.96,CORAL)
text(s,"LOTUS handoff",10.62,5.13,1.65,0.43,12,CORAL,True)

# 7. Framework exact four-layer composition
s = new_slide("LOTUS: proposed framework", "Framework", "Figure 1. LOTUS medicine traceability framework. Project adaptation of supplied four-layer diagram.")
text(s, "Four aligned layers connect ledger state to the people who act on it.", 0.78, 1.15, 11.7, 0.37, 16, GRAY)
row_labels=[("BLOCKCHAIN",1.76,0.83),("SMART CONTRACT",2.79,0.73),("TRANSACTION DATA",3.73,1.08),("STAKEHOLDERS",5.09,1.08)]
for name,y,h in row_labels:
    text(s,name,0.71,y+0.20,1.42,h-0.25,12,GREEN,True,PP_ALIGN.RIGHT)
    line(s,2.28,y,2.28,y+h,GREEN,1.2)
    line(s,2.28,y,2.45,y,GREEN,1.2)
    line(s,2.28,y+h,2.45,y+h,GREEN,1.2)
centers=[2.95+i*1.43 for i in range(7)]
for i,c in enumerate(centers):
    rect(s,c-0.30,1.93,0.60,0.48, MINT if i%2==0 else LIME,GREEN,radius=True)
    text(s,f"B{i+1}",c-0.22,2.03,0.44,0.21,10,GREEN,True,PP_ALIGN.CENTER)
    if i<6: line(s,c+0.32,2.17,centers[i+1]-0.33,2.17,GREEN,1.5,arrow=True)
for c,caption in [(4.48,"LOTUS chaincode"),(10.10,"Role + proof rules")]:
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(c-0.33), Inches(2.95), Inches(0.66), Inches(0.66))
    sh.fill.solid(); sh.fill.fore_color.rgb=GOLD; sh.line.fill.background()
    text(s,"✓",c-0.24,3.06,0.48,0.40,20,WHITE,True,PP_ALIGN.CENTER)
text(s,"Chaincode enforces custody, permit, stock, recall and proof rules",5.08,3.07,4.47,0.42,13,INK,align=PP_ALIGN.CENTER)
events=["Lot registered","Ship / accept","Permit issued","Fill + receipt","Exact-lot recall","Local match + proof","Public lot check"]
roles=["Manufacturer","Distributor","Prescriber","Pharmacy","Regulator","Patient","Public / auditor"]
for i,c in enumerate(centers):
    text(s,events[i],c-0.56,4.07,1.12,0.65,11.3,INK,align=PP_ALIGN.CENTER)
    rect(s,c-0.40,5.26,0.80,0.69,[MINT,LIME,PALE_GOLD,PALE_CORAL,MINT,PALE_GOLD,LIME][i],GREEN,radius=True)
    text(s,["M","D","Rx","P","R","Pt","V"][i],c-0.30,5.36,0.60,0.45,19,GREEN,True,PP_ALIGN.CENTER)
    text(s,roles[i],c-0.59,6.06,1.18,0.52,10.5,INK,align=PP_ALIGN.CENTER)

# 8. architecture
s = new_slide("System architecture", "Framework", "Source: docs/TOOLCHAIN_MIGRATION.md, application architecture")
nodes=[("Staff workspaces",0.82,1.58,2.3,0.75), ("LOTUS API",3.78,1.58,2.10,0.75),
       ("FireFly + FabConnect",6.56,1.58,2.63,0.75), ("Fabric + chaincode",9.83,1.58,2.52,0.75),
       ("Encrypted patient PWA",0.82,4.39,2.3,0.75),("Public bulletin",3.78,4.39,2.10,0.75),
       ("Fabric Gateway",6.56,4.39,2.63,0.75),("Encrypted IPFS",9.83,4.39,2.52,0.75)]
for name,x,y,w,h in nodes:
    rect(s,x,y,w,h,WHITE,GREEN,radius=True,lw=1.5)
    text(s,name,x+0.08,y+0.09,w-0.16,h-0.18,15,GREEN,True,PP_ALIGN.CENTER)
for a,b in [((3.12,1.96),(3.78,1.96)),((5.88,1.96),(6.56,1.96)),((9.19,1.96),(9.83,1.96)),
            ((3.12,4.76),(3.78,4.76)),((5.88,4.76),(6.56,4.76)),((9.19,4.76),(9.83,4.76))]:
    line(s,*a,*b,GREEN,2,arrow=True)
line(s,4.82,4.35,4.82,2.39,GREEN,1.7,arrow=True)
line(s,7.87,4.35,7.87,2.39,GREEN,1.7,arrow=True)
line(s,11.08,4.35,11.08,2.39,GREEN,1.7,arrow=True)
text(s,"public read + anonymous response",0.85,5.43,4.5,0.43,14,GRAY)
text(s,"credential in transient data",6.28,5.43,3.2,0.43,14,GRAY)
text(s,"document CID + digest on Fabric",9.43,5.43,3.18,0.43,14,GRAY)
label(s,"Single-host integration network",4.35,6.08,4.60,fill=PALE_GOLD,size=13)

# 9. sequence diagrams A+B
s = new_slide("Process flows: onboarding and custody", "Sequence diagrams")
sequence_panel(s,"Figure 2. Actor registration",0.60,1.32,6.05,5.20,
               ["Operator","Staff","API","Fabric"],
               [(0,2,"Invite + role"),(1,2,"Accept invitation"),(2,3,"Enroll authorized identity"),(3,2,"Commit role state")])
sequence_panel(s,"Figure 3. Lot and custody",6.82,1.32,5.91,5.20,
               ["Maker","Distributor","Pharmacy","Ledger"],
               [(0,3,"Register lot + digest"),(0,1,"Ship units"),(1,3,"Accept shipment"),(1,2,"Forward units"),(2,3,"Accept + update stock")])

# 10. sequence diagrams C+D
s = new_slide("Process flows: fill and recall", "Sequence diagrams")
sequence_panel(s,"Figure 4. Permit and dispensing",0.60,1.32,6.05,5.20,
               ["Prescriber","Patient","Pharmacy","Ledger"],
               [(0,3,"Issue expiring permit"),(1,2,"Fresh counter code"),(2,3,"Transient proof + exact lot"),(3,2,"Commit fill + receipt"),(2,1,"Signed receipt QR")])
sequence_panel(s,"Figure 5. Recall and response",6.82,1.32,5.91,5.20,
               ["Regulator","Ledger","Phone","Regulator"],
               [(0,1,"Issue exact-lot recall"),(1,2,"Public bulletin"),(2,2,"Match saved receipt locally"),(2,1,"Anonymous proof + nullifier"),(1,3,"Acknowledgement count")])

# 11 implementation
s = new_slide("Implementation framework", "Implementation", "Source: docs/TOOLCHAIN_MIGRATION.md; docs/WEB_APPLICATION_GUIDE.md")
items=[("Ledger", "Hyperledger Fabric 3.1.5", "Lot, custody, permit, fill, recall and proof rules"),
       ("Integration", "FireFly 1.5 + FabConnect", "Authenticated commands and durable events"),
       ("Private data", "Encrypted IPFS + PWA vault", "Document ciphertext and patient-held secret"),
       ("Evaluation", "Caliper + Brownie", "Fabric latency; separate EVM gas reference")]
for i,(a,b,c) in enumerate(items):
    x=0.78+(i%2)*6.23; y=1.45+(i//2)*2.38
    accent=[GREEN,CORAL,GOLD,GREEN][i]
    rect(s,x,y,5.88,2.05,WHITE,LINE,radius=True)
    rect(s,x,y,0.08,2.05,accent)
    text(s,a,x+0.25,y+0.18,5.32,0.35,17,accent,True)
    text(s,b,x+0.25,y+0.66,5.32,0.32,14,GRAY,True)
    text(s,c,x+0.25,y+1.14,5.32,0.60,15,INK,valign=MSO_ANCHOR.TOP)

# 12 verification
s = new_slide("Results: implementation checks", "Results and discussion", "Source: docs/toolchain-evidence.json (14 Oct 2026 delivery snapshot)")
checks=[("Contract",37),("API",13),("Browser",40),("FireFly",25),("IPFS",7),("Fabric first run",9)]
for i,(name,n) in enumerate(checks):
    x=0.83+(i%3)*4.20; y=1.56+(i//3)*2.17
    rect(s,x,y,3.82,1.74,WHITE,LINE,radius=True)
    text(s,str(n),x+0.22,y+0.23,1.05,0.75,38,[GREEN,CORAL,GOLD][i%3],True)
    text(s,name,x+1.28,y+0.31,2.26,0.62,18,INK,True)
    text(s,"passing checks",x+1.28,y+0.98,2.20,0.26,12,GRAY)
text(s,"These checks verify the local integration and workflows. They do not measure real-world recall delivery.",0.87,6.07,11.73,0.42,17,INK,align=PP_ALIGN.CENTER)

# 13 Caliper latency
s = new_slide("Results: Fabric latency", "Results and discussion", "Source: Hyperledger Caliper, isolated single-host tooling channel; 1 worker, 1 in-flight write")
rounds=EVIDENCE["caliper"]["rounds"]
names=[("Public read","public-feed"),("Register lot","register-lot"),("Dispense","dispense")]
for i,(name,key) in enumerate(names):
    d=rounds[key]; x=0.86+i*4.15
    text(s,name,x,1.52,3.65,0.37,20,GREEN,True,PP_ALIGN.CENTER)
    p50=d["p50LatencyMs"]; p95=d["p95LatencyMs"]
    for j,(lab,val,col) in enumerate([("Median",p50,GREEN),("95th percentile",p95,CORAL)]):
        yy=2.21+j*1.40
        text(s,lab,x,yy,3.65,0.27,13,GRAY)
        rect(s,x,yy+0.38,3.65*val/1600,0.42,col,radius=True)
        text(s,f"{val:,.0f} ms",x,yy+0.83,3.65,0.3,16,col,True)
    label(s,f"{d['successful']} success · {d['failed']} failed",x+0.35,5.50,2.95,fill=MINT,size=12)
text(s,"Writes include valid commit. This run measures local integration latency, not a production capacity ceiling.",0.91,6.17,11.5,0.42,16,INK,align=PP_ALIGN.CENTER)

# 14 process evidence
s = new_slide("Results: live application flow", "Results and discussion", "Source: current browser application; screenshot from local test-results/patient-mobile.png")
img=ROOT/"test-results"/"patient-mobile.png"
image_fit(s,img,0.73,1.27,3.08,5.34)
steps=[("1", "Counter fill", "Pharmacy validates permit, exact lot and available stock."),
       ("2", "Recall decision", "Regulator commits a recall for one lot; later fills are blocked."),
       ("3", "Private match", "The patient's vault finds its saved receipt locally."),
       ("4", "Anonymous response", "A proof contributes to a count without sharing the receipt.")]
for i,(num,head,body) in enumerate(steps):
    y=1.40+i*1.27
    rect(s,4.02,y,0.47,0.47,[GREEN,CORAL,GOLD,GREEN][i],radius=True)
    text(s,num,4.02,y+0.02,0.47,0.43,16,WHITE,True,PP_ALIGN.CENTER)
    text(s,head,4.76,y-0.02,7.18,0.34,18,GREEN,True)
    text(s,body,4.76,y+0.37,7.20,0.52,15,INK)

# 15 synthetic accuracy
s = new_slide("Results: recall targeting in simulation", "Results and discussion", "Historical research simulation; 10,000 synthetic patients, 30 lot recalls, 1% lot errors")
image_fit(s,ROOT/"docs"/"figures"/"accuracy.png",0.55,1.23,12.18,4.75)
text(s,"At 20% phone loss, LOTUS + existing channels reaches 0.994 sensitivity; drug-code matching reaches 0.858.",0.80,6.17,11.72,0.40,16,GREEN,True,align=PP_ALIGN.CENTER)

# 16 scaling
s = new_slide("Results: simulated cohort scaling", "Results and discussion", "Historical research simulation; source: docs/REPORT.md, Section 7.2")
headers=["Patients","Dispenses","NDC precision","LOTUS precision","LOTUS + channels sensitivity"]
rows=[["1,000","3,528","0.186","0.981","0.995"],["10,000","34,858","0.165","0.993","0.997"],["100,000","349,415","0.174","0.992","0.997"]]
xs=[0.76,2.58,4.49,6.83,9.13]; ws=[1.70,1.77,2.16,2.17,3.42]
for i,(h,x,w) in enumerate(zip(headers,xs,ws)):
    rect(s,x,1.67,w,0.72,GREEN)
    text(s,h,x+0.10,1.74,w-0.20,0.57,12,WHITE,True,PP_ALIGN.CENTER)
for j,row in enumerate(rows):
    yy=2.49+j*0.94
    for i,(v,x,w) in enumerate(zip(row,xs,ws)):
        rect(s,x,yy,w,0.82,WHITE if j%2==0 else MINT,LINE)
        text(s,v,x+0.08,yy+0.12,w-0.16,0.54,18,GREEN if i>=3 else INK,i>=3,PP_ALIGN.CENTER)
text(s,"Scenario: 10% phone loss and 1% lot errors. These are modeled recall outcomes, not live deployment measurements.",0.86,6.09,11.56,0.48,16,INK,align=PP_ALIGN.CENTER)

# 17 timing privacy
s = new_slide("Results: counter timing privacy", "Results and discussion", "Historical red-team simulation; source: docs/figures/timing_attack.png")
image_fit(s,ROOT/"docs"/"figures"/"timing_attack.png",0.67,1.30,12.00,4.74)
text(s,"At a quiet pharmacy, instant submission exposes timing. Hourly batching cuts modeled identification from 94% to 2%.",0.84,6.13,11.58,0.45,16,GREEN,True,PP_ALIGN.CENTER)

# 18 cost boundary
s = new_slide("Results: cost boundary", "Results and discussion", "Source: docs/toolchain-evidence.json; Brownie is an isolated EVM reference, not a Fabric cost")
rect(s,0.86,1.41,5.39,4.57,MINT,LINE,radius=True)
text(s,"Operational Fabric",1.19,1.78,4.71,0.49,26,GREEN,True)
text(s,"No EVM gas fee is charged for Fabric transactions. The relevant local metric is successful commit latency and operational infrastructure cost.",1.20,2.54,4.64,1.54,20,INK,valign=MSO_ANCHOR.TOP)
label(s,"Caliper: 12/12 committed fills",1.37,4.79,4.34,fill=WHITE,size=14)
rect(s,6.55,1.41,5.90,4.57,WHITE,LINE,radius=True)
text(s,"Historical EVM reference",6.87,1.78,5.20,0.43,24,CORAL,True)
gas=EVIDENCE["brownie"]["gas"]
for i,(name,key) in enumerate([("Register lot","register_lot"),("Issue permit","issue_permit"),("Dispense","dispense_first_leaf"),("Recall","recall")]):
    val=gas[key]; yy=2.43+i*0.71
    text(s,name,6.87,yy,1.77,0.25,12,INK)
    rect(s,8.52,yy+0.04,2.20*val/300000,0.21,CORAL,radius=True)
    text(s,f"{val:,} gas",10.63,yy-0.01,1.50,0.28,11,CORAL,True,PP_ALIGN.RIGHT)
text(s,"EVM values support comparison of the retained Solidity prototype only.",6.88,5.48,5.18,0.32,12,GRAY)

# 19 historical gas optimization graph
s = new_slide("Results: historical dispense gas", "Results and discussion", "Historical EVM prototype; source: docs/figures/gas_dispense.png. Fabric does not charge EVM gas.")
image_fit(s,ROOT/"docs"/"figures"/"gas_dispense.png",0.67,1.31,12.00,4.80)
text(s,"The lean Merkle tree reduced mean EVM dispense gas from 933k to 373k in the retained prototype.",0.86,6.19,11.53,0.42,16,GREEN,True,PP_ALIGN.CENTER)

# 20 discussion
s = new_slide("Discussion: answers to the research questions", "Results and discussion")
card(s,"RQ1: verifiable last hop", "Accepted custody and atomic stock accounting support an exact-lot fill. The phone holds the patient secret; the ledger stores a fresh commitment and receipt evidence.",0.80,1.48,5.85,3.51,GREEN)
card(s,"RQ2: targeted private response", "Synthetic evaluation shows much higher alert precision than drug-code matching. Real proof checks and browser tests establish the implemented response flow on the local network.",6.81,1.48,5.73,3.51,CORAL)
rect(s,1.54,5.45,10.24,0.85,PALE_GOLD,radius=True)
text(s,"Scope: the synthetic outcomes, local Fabric measurements and deployment claims answer different questions.",1.82,5.58,9.72,0.58,17,INK,True,PP_ALIGN.CENTER)

# 21 conclusion
s = new_slide("Conclusion", "Conclusion and future scope")
for i,(a,b) in enumerate([
    ("Exact-lot trace", "Accepted custody, available stock and a committed fill connect the medicine lot to the final handoff."),
    ("Private patient check", "The browser vault matches public recalls against its own receipts and can prove membership anonymously."),
    ("Measured integration", "Fabric, FireFly and IPFS workflows passed local checks; Caliper recorded commit latency on one host."),
]):
    card(s,a,b,0.79+i*4.18,1.63,3.84,3.59,[GREEN,CORAL,GOLD][i])
text(s,"LOTUS demonstrates a verifiable recall path from lot creation to a private patient response.",1.08,5.82,11.24,0.55,22,GREEN,True,PP_ALIGN.CENTER)

# 22 future scope
s = new_slide("Future scope", "Conclusion and future scope")
future=[("Independent consortium", "Separate peer and orderer administration, production identity enrollment and key custody."),
        ("Recall delivery", "Connect conventional channels and prove closed-browser delivery and reach."),
        ("Privacy hardening", "Production proof setup, timing policy, signed feeds and publication controls."),
        ("Broader evaluation", "Real integrations, larger workloads and clinical delivery outcomes.")]
for i,(a,b) in enumerate(future):
    card(s,a,b,0.82+(i%2)*6.18,1.47+(i//2)*2.25,5.86,1.91,[GREEN,CORAL,GOLD,GREEN][i])

# 23 references
s = new_slide("References", "Sources")
refs=[
    "[1] U.S. FDA. Drug Supply Chain Security Act (DSCSA), 2013.",
    "[2] GS1. EPCIS Standard, version 2.0, 2022.",
    "[3] Azaria et al. MedRec: Blockchain for Medical Data Access, 2016.",
    "[4] Walonoski et al. Synthea, JAMIA 25(3), 2018.",
    "[5] Grassi et al. Poseidon, USENIX Security, 2021.",
    "[6] Groth. On the Size of Pairing-Based Non-interactive Arguments, EUROCRYPT, 2016.",
    "[7] Hyperledger Fabric, FireFly, Caliper and IPFS project documentation.",
    "[8] LOTUS repository: REPORT.md, TOOLCHAIN_MIGRATION.md and toolchain-evidence.json.",
]
for i,r in enumerate(refs):
    y=1.33+i*0.65
    text(s,r,0.87,y,11.63,0.47,15,INK)
    line(s,0.87,y+0.54,12.44,y+0.54,LINE,0.7)

# 24 close
s = new_slide()
rect(s,0.18,0,13.153,7.5,INK)
text(s,"Thank you",1.00,1.69,11.25,1.08,54,WHITE,True,PP_ALIGN.CENTER)
text(s,"Questions?",1.00,3.26,11.25,0.72,31,LIME,True,PP_ALIGN.CENTER)
text(s,"LOTUS · Manipal Institute of Technology",1.00,6.12,11.25,0.37,17,WHITE,align=PP_ALIGN.CENTER)

speaker_notes = {
    1: ("Patoju Sai Avinash", "Introduce LOTUS as lot-oriented medicine traceability with a private patient recall response."),
    2: ("Patoju Sai Avinash", "Preview the sequence: problem, research framing, framework, implementation, evidence, conclusion. Motivation is intentionally omitted."),
    3: ("Patoju Sai Avinash", "The manufacturer-to-pharmacy route can be traced, but a patient record may lack the exact lot. This creates broad or missed recall alerts."),
    4: ("P Pattabhi Ram", "Frame the two questions: verifiable last-hop dispensing without patient identity on the ledger, and better targeted recall response. Mention the evaluation plan."),
    5: ("P Pattabhi Ram", "Briefly position DSCSA/EPCIS, MedRec, MediLedger and zero-knowledge proofs. Explain which part each covers."),
    6: ("P Pattabhi Ram", "The gap is the pharmacy-to-patient lot handoff. The research pipeline later models this exact-lot question with reproducible synthetic cohorts."),
    7: ("Patoju Sai Avinash", "Read the four layers from top to bottom: Fabric blocks, LOTUS chaincode rules, transaction data, and stakeholders. Map lot registration through public verification."),
    8: ("Patoju Sai Avinash", "Explain that ordinary commands pass through FireFly/FabConnect to Fabric. Permit credentials use Gateway transient data. Encrypted documents go to IPFS; the phone keeps the root secret."),
    9: ("K. Jaideep Varma", "Registration requires an authorized role. A shipment does not increase usable stock until the receiver accepts it. Describe the ledger checks shown by both sequence diagrams."),
    10: ("K. Jaideep Varma, then Adabala Venkata Abhinav", "Jaideep: the fill atomically checks accepted stock, permit balance, product, lot, expiry, recall state and a unique commitment; a recall blocks later fills. Abhinav: the phone matches a saved receipt locally, submits a zero-knowledge proof and uses a nullifier to prevent repeat acknowledgement. The root secret stays in an encrypted vault; two of three Guardian shares can recover it with an encrypted backup for history."),
    11: ("K. Poorna Sai Praneeth", "Identify the current stack: Fabric, FireFly/FabConnect, IPFS, patient PWA and Caliper. Brownie gas is a separate historical EVM reference."),
    12: ("K. Poorna Sai Praneeth", "The numbers are passing local integration and workflow checks, not proof of clinical delivery or production-scale operation."),
    13: ("Ashmith C Shettigar", "Caliper used one worker and one in-flight write on a single-host channel. Report 24 reads, 12 registrations, 12 fills, zero failures, and about 1.1-second median write commit latency."),
    14: ("Puripanda Venkata Praneeth", "Walk through the phone-oriented PWA: QR permit import, one-time counter code, signed receipt import, public recall bulletin, local match and anonymous acknowledgement. Closed-browser delivery remains future work."),
    15: ("P Pattabhi Ram", "This is a historical synthetic cohort chart, not measured patient delivery. State the 10,000-patient, 30-recall scenario and compare exact-lot matching with drug-code matching."),
    16: ("P Pattabhi Ram", "Explain deterministic cohort generation and the manifest. At 10% phone loss and 1% lot error, precision stays around 0.98-0.99 across 1,000 to 100,000 synthetic patients."),
    17: ("Dhruti P Shetty", "The historical red-team simulation found a timing side channel at a quiet pharmacy: 94% modeled identification with instant submission versus 2% with hourly batching. Mention linkability, small-region counts and Guardian collusion as other tested threats."),
    18: ("Ashmith C Shettigar", "Fabric has no EVM gas fee. Brownie figures are measured on a retained Solidity prototype and must not be described as Fabric costs."),
    19: ("Ashmith C Shettigar", "The historical lean-tree prototype reduced mean dispense gas from about 933k to 373k. This curve is EVM evidence only."),
    20: ("Patoju Sai Avinash", "Answer RQ1 with accepted custody and atomic exact-lot dispensing; answer RQ2 with private local matching and the qualified synthetic recall results."),
    21: ("Patoju Sai Avinash", "Conclude that LOTUS demonstrates a verifiable path from lot creation to private patient response in a local integration network."),
    22: ("K. Poorna Sai Praneeth", "Explain the production gates: independently administered peers and identities, key custody, stronger feed privacy, real notification delivery and broader evaluation."),
    23: ("Patoju Sai Avinash", "Keep references on screen briefly. Distinguish the historical LOTUS research report from the current migration and evidence files."),
    24: ("Patoju Sai Avinash", "Thank the audience and invite questions. If asked about clinical reach, say the recall accuracy figures are synthetic; current Fabric checks prove the local integrated workflow."),
}
for slide_no, (speaker, note) in speaker_notes.items():
    prs.slides[slide_no - 1].notes_slide.notes_text_frame.text = f"Speaker: {speaker}\n\n{note}\n\nFull script: LOTUS_Speaker_Guide.md"

pptx_path=OUT/"LOTUS_Research_Presentation_With_Speaker_Notes.pptx"
prs.save(pptx_path)
print(f"Wrote {pptx_path} ({len(prs.slides)} slides)")

# A separate, high resolution raster of the exact-format framework is useful
# for dropping into a different deck without copying the full slide.
fw = prs.slides[6]
manifest = OUT/"LOTUS_Presentation_Notes.txt"
manifest.write_text(
    "LOTUS research deck, 24 slides. Reference flow: SandalwoodNet_new.pdf.\n"
    "Slide 7 is the four-layer, editable supply-chain framework replacement.\n"
    "Slides 9-10 contain four editable sequence diagrams.\n"
    "Slides 13 and 18 use measured local Fabric and historical EVM evidence respectively.\n"
    "Slides 15-17 and 19 are explicitly labelled historical research simulations or EVM evidence.\n"
    "The deck does not claim independently operated consortium infrastructure or proven clinical notification delivery.\n",
    encoding="utf-8",
)
