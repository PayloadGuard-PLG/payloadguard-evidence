import json
import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# CONFIG
SOURCE_DATA = "audit_data.json"
IMG_DIR = "/data/data/com.termux/files/home/storage/shared/Download/payloadguard_blueprints"
OUTPUT_PDF = os.path.join(IMG_DIR, "PayloadGuard_Verification_Report_FINAL.pdf")

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.drawString(0.75 * inch, 0.75 * inch, f"DOC-ID: PLG-VER-{datetime.datetime.now().strftime('%Y%m%d')} | CONFIDENTIAL")
    canvas.drawRightString(7.5 * inch, 0.75 * inch, f"Page {doc.page}")
    canvas.restoreState()

def build_report():
    if not os.path.exists(SOURCE_DATA):
        print("❌ Audit data missing. Run 'run_system_audit.py' first.")
        return

    with open(SOURCE_DATA) as f:
        data = json.load(f)
        findings = data["findings"]
        meta = data["meta"]

    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='base', frames=frame, onPage=header_footer)
    doc.addPageTemplates([template])
    
    styles = getSampleStyleSheet()
    # Custom Styles
    style_code = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=7, textColor=colors.black)
    style_th = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)

    story = []

    # --- COVER PAGE ---
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("SYSTEM VERIFICATION REPORT", styles['Title']))
    story.append(Paragraph("PayloadGuard Verification Pipeline", styles['Heading2']))
    story.append(Spacer(1, 0.5 * inch))
    
    audit_summary = [
        ["Audit Date:", meta["audit_timestamp"]],
        ["Scope:", "Full System Verification (Gates C1-C6)"],
        ["Artifacts Analyzed:", str(meta["total_files"])],
        ["Verification Engine:", "Termux Mobile Pipeline v2.4"]
    ]
    t = Table(audit_summary, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')]))
    story.append(t)
    story.append(PageBreak())

    # --- SECTION 1: SYSTEM INTEGRITY (HASHES) ---
    story.append(Paragraph("1. System Integrity & Chain of Custody", styles['Heading1']))
    story.append(Paragraph("The following cryptographic hashes (SHA-256) establish the exact state of the system at the time of verification.", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    hash_data = [["Filename", "Integrity Hash (SHA-256)", "Size"]]
    for item in findings:
        hash_data.append([
            Paragraph(item["filename"], style_code),
            Paragraph(item["integrity_hash"], style_code),
            f"{item['metrics']['loc']} LOC"
        ])

    t_hash = Table(hash_data, colWidths=[2*inch, 3.5*inch, 1*inch], repeatRows=1)
    t_hash.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_hash)
    story.append(PageBreak())

    # --- SECTION 2: VERIFICATION BY GATE ---
    story.append(Paragraph("2. Verification Findings (Traceability)", styles['Heading1']))
    story.append(Paragraph("Each component is traced to a specific Regulatory Gate (C1-C6).", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Sort findings by Gate
    findings_by_gate = {}
    for item in findings:
        g = item["gate"]
        if g not in findings_by_gate: findings_by_gate[g] = []
        findings_by_gate[g].append(item)

    for gate_id in sorted(meta["gate_definitions"].keys()):
        gate_info = meta["gate_definitions"][gate_id]
        gate_items = findings_by_gate.get(gate_id, [])
        
        # Gate Header
        story.append(Paragraph(f"Gate {gate_id}: {gate_info['title']}", styles['Heading2']))
        story.append(Paragraph(f"<i>Objective: {gate_info['desc']}</i>", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        if not gate_items:
            story.append(Paragraph("No artifacts mapped to this gate.", styles['Normal']))
        else:
            g_data = [["Component", "Metrics", "Verification Status"]]
            for gi in gate_items:
                g_data.append([
                    gi["filename"],
                    f"Complexity: {gi['metrics']['complexity_proxy']}",
                    "PASS" if gi["status"] == "VERIFIED" else "FAIL"
                ])
            
            t_g = Table(g_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            t_g.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.navy),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t_g)
        
        story.append(Spacer(1, 0.3 * inch))

    story.append(PageBreak())

    # --- SECTION 3: VISUAL BLUEPRINTS ---
    story.append(Paragraph("3. Architectural Evidence (Blueprints)", styles['Heading1']))
    
    if os.path.exists(IMG_DIR):
        for img_file in sorted(os.listdir(IMG_DIR)):
            if img_file.endswith(".png"):
                story.append(Paragraph(f"Exhibit: {img_file}", styles['Heading3']))
                try:
                    img_path = os.path.join(IMG_DIR, img_file)
                    im = Image(img_path, width=6*inch, height=4*inch, kind='proportional')
                    story.append(im)
                    story.append(Spacer(1, 0.2 * inch))
                except: pass

    story.append(Paragraph("--- END OF AUDIT ---", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Regulatory Report Generated: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_report()
