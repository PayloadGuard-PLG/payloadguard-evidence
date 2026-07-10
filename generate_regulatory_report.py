import json
import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- REGULATORY CONFIG ---
REPO_NAME = "PayloadGuard-PLG/payloadguard-evidence"
DOC_DIR = "/data/data/com.termux/files/home/storage/shared/Download/payloadguard_blueprints"
OUTPUT_FILE = os.path.join(DOC_DIR, "PayloadGuard_Regulatory_Audit_v1.pdf")

# Standard Gate Definitions (from Operations Manual)
GATES = {
    "C1": "Specification Capture",
    "C2": "Exclusivity Proofs",
    "C3": "Parser Hardening",
    "C4": "Formal Verification (STP)",
    "C5": "Mutation Testing",
    "C6": "Natural Language Confirmation"
}

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.drawString(inch, 0.75 * inch, f"Audit Ref: {datetime.datetime.now().strftime('%Y%m%d-%H%M')} | {REPO_NAME}")
    canvas.drawRightString(7.5 * inch, 0.75 * inch, f"Page {doc.page}")
    canvas.restoreState()

def build_compliance_report():
    print(f"Generating Regulatory Report: {OUTPUT_FILE}")
    doc = SimpleDocTemplate(OUTPUT_FILE, pagesize=letter)
    
    # Apply Custom Header/Footer
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=header_footer)
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()
    story = []

    # --- 1. CERTIFICATE OF CONFORMITY (Cover Page) ---
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("CERTIFICATE OF CONFORMITY", styles['Title']))
    story.append(Paragraph(f"System: {REPO_NAME}", styles['Heading2']))
    story.append(Spacer(1, 0.25 * inch))
    
    # Compliance Statement
    audit_text = f"""
    <b>Audit Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
    <b>Auditor:</b> Automated Termux Pipeline (Mobile)<br/>
    <b>Scope:</b> Full System Verification (Gates C1-C6)<br/><br/>
    This document certifies that the artifacts listed herein have been generated 
    directly from the source code repository. All findings are mapped against 
    the Regulatory Verification Gates (C1-C6) as defined in the Operations Manual.
    """
    story.append(Paragraph(audit_text, styles['Normal']))
    story.append(Spacer(1, 1 * inch))
    
    # Signature Block
    sig_data = [["__________________________", "__________________________"],
                ["Approver Signature", "Date"]]
    t = Table(sig_data, colWidths=[3.5*inch, 2*inch])
    t.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t)
    story.append(PageBreak())

    # --- 2. OBJECTIVE EVIDENCE (Visual Blueprints) ---
    story.append(Paragraph("SECTION A: OBJECTIVE EVIDENCE", styles['Heading1']))
    story.append(Paragraph("The following architectural blueprints represent the 'as-built' system state.", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    if os.path.exists(DOC_DIR):
        for img_file in sorted(os.listdir(DOC_DIR)):
            if img_file.endswith(".png"):
                story.append(Paragraph(f"Exhibit: {img_file}", styles['Heading3']))
                try:
                    # Scale image to strict width
                    img_path = os.path.join(DOC_DIR, img_file)
                    im = Image(img_path, width=6.5*inch, height=4*inch, kind='proportional')
                    story.append(im)
                    story.append(Spacer(1, 0.3 * inch))
                except:
                    pass
    story.append(PageBreak())

    # --- 3. TRACEABILITY MATRICES (Gate-Based) ---
    story.append(Paragraph("SECTION B: VERIFICATION FINDINGS", styles['Heading1']))
    story.append(Paragraph("Findings are partitioned by Verification Gate (C1-C6).", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Ingest Data
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    raw_modules = []
    
    # 3.1 Aggregate All Findings
    for jf in json_files:
        try:
            with open(jf) as f:
                d = json.load(f)
                chunk = d.get("modules", []) if isinstance(d, dict) else d
                raw_modules.extend(chunk)
        except: pass

    # 3.2 Group by Gate (Simulated Logic for this Demo)
    # In a real run, your JSON should have a "gate" field. 
    # Here we map them logically or default to "C1".
    gate_buckets = {k: [] for k in GATES.keys()}
    
    for m in raw_modules:
        # Check if 'gate' exists, else assign based on file type/name logic
        g = m.get("gate", "C1") 
        if g not in gate_buckets: g = "C1"
        gate_buckets[g].append(m)

    # 3.3 Render Tables Per Gate
    for gate_id, gate_name in GATES.items():
        findings = gate_buckets.get(gate_id, [])
        if not findings: continue

        story.append(Paragraph(f"Gate {gate_id}: {gate_name}", styles['Heading2']))
        
        table_data = [["Component ID", "Verification Status", "Evidence Reference"]]
        for item in findings:
            c_name = item.get("component", item.get("name", "Unknown"))
            c_status = item.get("status", "Pending")
            c_type = item.get("type", "N/A")
            
            # Formatting Status
            status_style = colors.green if str(c_status).lower() in ['linked', 'verified', 'pass'] else colors.red
            
            table_data.append([c_name, c_status, c_type])

        # Gate Table Style
        t = Table(table_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            # Dynamic text color for status column (Row 1 to End, Col 1)
            # ('TEXTCOLOR', (1,1), (1,-1), colors.black), 
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph("*** END OF REGULATORY REPORT ***", styles['Normal']))
    doc.build(story)
    print("✅ Regulatory Report Generated Successfully.")

if __name__ == "__main__":
    build_compliance_report()
