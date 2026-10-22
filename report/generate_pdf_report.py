#!/usr/bin/env python3
"""
Generates Technical_Report.pdf from simulation results and graphs using ReportLab.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for 'Page X of Y' footer."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Don't draw header on first page
        if self._pageNumber > 1:
            self.drawString(54, 755, "ITUC201: Fundamentals of Computer Networks | Technical Report — Student ID: 25CS024")
            self.setStrokeColor(colors.HexColor("#CCCCCC"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)
            
        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "NetVista 3D: Go-Back-N and Selective Repeat ARQ Performance Evaluation")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1e3799")
    SECONDARY = colors.HexColor("#0c2461")
    TEXT_DARK = colors.HexColor("#2f3640")
    ACCENT = colors.HexColor("#4a69bd")
    BG_LIGHT = colors.HexColor("#f8f9fa")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        alignment=0, # Left
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e272e"),
        backColor=colors.HexColor("#f1f2f6"),
        borderPadding=6,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'DocCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e3799"),
        backColor=colors.HexColor("#e8f0fe"),
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8
    )

    story = []
    
    # ----------------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("PERFORMANCE EVALUATION OF GO-BACK-N AND SELECTIVE REPEAT ARQ PROTOCOLS UNDER DETERMINISTIC FRAME LOSSES", title_style))
    story.append(Paragraph("<b>Subject:</b> ITUC201 — Fundamentals of Computer Networks | <b>Student ID:</b> 25CS024 | <b>Semester:</b> 3 (B.Tech CSE)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=12))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Student ID:</b>", body_style), Paragraph("25CS024", body_style),
         Paragraph("<b>Subject Code:</b>", body_style), Paragraph("ITUC201 (CNet)", body_style)],
        [Paragraph("<b>Assigned Topic:</b>", body_style), Paragraph("Go-Back-N & Selective Repeat under losses", body_style),
         Paragraph("<b>Assessment Type:</b>", body_style), Paragraph("Individual CIE (20 Marks)", body_style)],
        [Paragraph("<b>Implementation:</b>", body_style), Paragraph("Python 3.12 (heapq Event-Driven)", body_style),
         Paragraph("<b>Research Focus:</b>", body_style), Paragraph("Retransmissions vs Window Size (W=3, 5)", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[1.1*inch, 2.5*inch, 1.2*inch, 2.2*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f4f6fb")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#dcdde1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e1e2e6")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # ----------------------------------------------------------------------------------
    # ABSTRACT
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("1. Abstract", h1_style))
    abstract_text = (
        "This academic report presents an experimental investigation into the behavioral and performance "
        "dynamics of <b>Go-Back-N (GBN)</b> and <b>Selective Repeat (SR)</b> sliding-window Automatic Repeat reQuest (ARQ) "
        "protocols. A discrete-event network simulation engine was engineered in Python utilizing an event-driven priority "
        "queue (heapq). A rigorous experimental testbed evaluated the transmission of 10 data frames under deterministic "
        "first-attempt losses at frames 4 and 7 across sender window sizes of 3 and 5. Quantitative measurements confirm that "
        "Selective Repeat maintains a strictly invariant retransmission count of exactly 2 frames across both window sizes "
        "owing to receiver-side buffering. In contrast, Go-Back-N exhibits window-dependent retransmission cascades: window size 3 "
        "incurred 6 retransmissions across two distinct timeout events, whereas window size 5 consolidated recovery into a single "
        "in-flight window burst of 5 retransmissions, accelerating completion time by 36.4%. A fully worked university exam numerical "
        "analyzing bandwidth-delay product, channel utilization, and sequence-number field sizing is also provided."
    )
    story.append(Paragraph(abstract_text, body_style))

    # ----------------------------------------------------------------------------------
    # PROBLEM STATEMENT & OBJECTIVES
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("2. Problem Statement & Research Objectives", h1_style))
    p_stmt = (
        "<b>Core Research Question:</b> <i>How do retransmission counts change with window size and loss pattern?</i><br/>"
        "In packet-switched networking, transport efficiency hinges upon error-recovery mechanisms. While pipelined sliding "
        "windows enable high channel utilization over high-latency links, packet drops trigger retransmissions. This study "
        "empirically isolates and compares how GBN and SR react when multiple loss events occur in close sequence."
    )
    story.append(Paragraph(p_stmt, body_style))

    # ----------------------------------------------------------------------------------
    # PROTOCOL THEORY & COMPARISON
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("3. Sliding Window ARQ Mechanics", h1_style))
    theory_text = (
        "Sliding window protocols achieve high utilization by permitting the sender to transmit up to <i>W</i> packets "
        "before waiting for acknowledgment. The fundamental link utilization is governed by the ratio <i>a = T<sub>p</sub> / T<sub>t</sub></i>, "
        "where <i>T<sub>p</sub></i> is the one-way propagation delay and <i>T<sub>t</sub></i> is frame transmission time. "
        "To achieve 100% theoretical link saturation without errors, the sender window must satisfy <i>W &ge; 1 + 2a</i>."
    )
    story.append(Paragraph(theory_text, body_style))

    proto_table_data = [
        [Paragraph("<b>Architectural Dimension</b>", body_style), Paragraph("<b>Go-Back-N (GBN)</b>", body_style), Paragraph("<b>Selective Repeat (SR)</b>", body_style)],
        [Paragraph("Receiver Window (W<sub>r</sub>)", body_style), Paragraph("1 (Strict in-order reception)", body_style), Paragraph("Equal to W<sub>s</sub> (Permits out-of-order)", body_style)],
        [Paragraph("Receiver Buffering", body_style), Paragraph("None (Discards out-of-order frames)", body_style), Paragraph("Buffers all valid out-of-order frames", body_style)],
        [Paragraph("Acknowledgment Type", body_style), Paragraph("Cumulative (Confirms all &le; n)", body_style), Paragraph("Individual / Selective (Confirms exact frame n)", body_style)],
        [Paragraph("Sender Timer Structure", body_style), Paragraph("Single timer for oldest unACKed frame", body_style), Paragraph("Independent timer for each frame", body_style)],
        [Paragraph("Retransmission Scope", body_style), Paragraph("Entire window (send_base to next-1)", body_style), Paragraph("Only the specific timed-out frame", body_style)],
        [Paragraph("Sequence Number Bits", body_style), Paragraph("W<sub>s</sub> &le; 2<sup>m</sup> - 1", body_style), Paragraph("W<sub>s</sub> + W<sub>r</sub> &le; 2<sup>m</sup> &rarr; W<sub>s</sub> &le; 2<sup>m-1</sup>", body_style)]
    ]
    t_proto = Table(proto_table_data, colWidths=[1.8*inch, 2.6*inch, 2.6*inch])
    t_proto.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3799")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dcdde1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_proto)
    story.append(Spacer(1, 8))

    # ----------------------------------------------------------------------------------
    # ACTUAL RESULTS TABLE
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("4. Experimental Benchmark Results (Actual Simulator Runs)", h1_style))
    story.append(Paragraph("The four mandatory experimental configurations were executed under deterministic loss at data frames 4 and 7. "
                           "The measured metrics are presented below:", body_style))

    res_table_data = [
        [Paragraph("<b>Experiment ID</b>", body_style), Paragraph("<b>Window (W)</b>", body_style),
         Paragraph("<b>Orig Tx</b>", body_style), Paragraph("<b>Retrans</b>", body_style),
         Paragraph("<b>Total Tx</b>", body_style), Paragraph("<b>ACKs</b>", body_style),
         Paragraph("<b>Timeouts</b>", body_style), Paragraph("<b>Time (TU)</b>", body_style),
         Paragraph("<b>Delivery</b>", body_style)],
        [Paragraph("GBN_W3", body_style), Paragraph("3", body_style), Paragraph("10", body_style),
         Paragraph("<b>6</b>", body_style), Paragraph("16", body_style), Paragraph("14", body_style),
         Paragraph("2", body_style), Paragraph("36.8", body_style), Paragraph("10/10 [OK]", body_style)],
        [Paragraph("GBN_W5", body_style), Paragraph("5", body_style), Paragraph("10", body_style),
         Paragraph("<b>5</b>", body_style), Paragraph("15", body_style), Paragraph("13", body_style),
         Paragraph("1", body_style), Paragraph("23.4", body_style), Paragraph("10/10 [OK]", body_style)],
        [Paragraph("SR_W3", body_style), Paragraph("3", body_style), Paragraph("10", body_style),
         Paragraph("<b>2</b>", body_style), Paragraph("12", body_style), Paragraph("10", body_style),
         Paragraph("2", body_style), Paragraph("27.4", body_style), Paragraph("10/10 [OK]", body_style)],
        [Paragraph("SR_W5", body_style), Paragraph("5", body_style), Paragraph("10", body_style),
         Paragraph("<b>2</b>", body_style), Paragraph("12", body_style), Paragraph("10", body_style),
         Paragraph("2", body_style), Paragraph("19.0", body_style), Paragraph("10/10 [OK]", body_style)],
    ]
    t_res = Table(res_table_data, colWidths=[1.1*inch, 0.8*inch, 0.65*inch, 0.65*inch, 0.65*inch, 0.6*inch, 0.7*inch, 0.85*inch, 1.0*inch])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0c2461")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#b2bec3")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f2f6")]),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_res)
    story.append(Spacer(1, 10))

    # ----------------------------------------------------------------------------------
    # CHARTS EMBEDDING
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("5. Visual Data Analysis & Graphical Comparisons", h1_style))
    graphs_dir = os.path.join(os.path.dirname(output_path), "..", "graphs")

    chart1_path = os.path.join(graphs_dir, "comparison_retransmissions.png")
    chart2_path = os.path.join(graphs_dir, "comparison_completion_time.png")
    chart3_path = os.path.join(graphs_dir, "comparison_total_transmissions.png")
    chart4_path = os.path.join(graphs_dir, "window_size_sensitivity.png")

    if os.path.exists(chart1_path) and os.path.exists(chart2_path):
        img1 = Image(chart1_path, width=3.4*inch, height=2.1*inch)
        img2 = Image(chart2_path, width=3.4*inch, height=2.1*inch)
        t_charts1 = Table([[img1, img2]], colWidths=[3.5*inch, 3.5*inch])
        t_charts1.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_charts1)
        story.append(Spacer(1, 6))

    if os.path.exists(chart3_path) and os.path.exists(chart4_path):
        img3 = Image(chart3_path, width=3.4*inch, height=2.1*inch)
        img4 = Image(chart4_path, width=3.4*inch, height=2.1*inch)
        t_charts2 = Table([[img3, img4]], colWidths=[3.5*inch, 3.5*inch])
        t_charts2.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_charts2)
        story.append(Spacer(1, 10))

    # ----------------------------------------------------------------------------------
    # TIMELINES
    # ----------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("6. Space-Time Ladder Diagrams (Protocol Timelines)", h1_style))
    story.append(Paragraph("The diagrams below depict the discrete-event ladder traces for GBN (W=3) and Selective Repeat (W=3), "
                           "illustrating packet drops (Red X), duplicate ACKs, timeouts, and selective retransmissions.", body_style))

    timeline_gbn_path = os.path.join(graphs_dir, "timeline_GBN_W3.png")
    timeline_sr_path = os.path.join(graphs_dir, "timeline_SR_W3.png")

    if os.path.exists(timeline_gbn_path) and os.path.exists(timeline_sr_path):
        t_gbn_img = Image(timeline_gbn_path, width=3.35*inch, height=4.3*inch)
        t_sr_img = Image(timeline_sr_path, width=3.35*inch, height=4.3*inch)
        t_timelines = Table([[t_gbn_img, t_sr_img]], colWidths=[3.5*inch, 3.5*inch])
        t_timelines.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_timelines)
        story.append(Spacer(1, 8))

    # ----------------------------------------------------------------------------------
    # KEY SCIENTIFIC FINDINGS & INTERPRETATION
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("7. Observations and Scientific Interpretation", h1_style))
    finding_1 = (
        "<b>1. Selective Repeat Retransmission Invariance:</b> Selective Repeat incurred exactly <b>2 retransmissions</b> "
        "regardless of whether the window was 3 or 5. Because the receiver window accommodates out-of-order frames "
        "(W<sub>r</sub> = W<sub>s</sub>), Frames 5 and 6 (in W=3) or Frames 5, 6, 7, 8 (in W=5) were safely stored in receiver buffers. "
        "Only the damaged frames were retransmitted, completely insulating unaffected packets from loss."
    )
    story.append(Paragraph(finding_1, body_style))

    finding_2 = (
        "<b>2. Go-Back-N Window Dynamics (The 6 vs 5 Retransmission Phenomenon):</b><br/>"
        "&bull; <i>At W = 3:</i> Frame 4 loss occurred during burst [4, 5, 6]. Following timeout at t=13.5 TU, GBN retransmitted "
        "Frames 4, 5, and 6 (3 retransmissions). Later, Frame 7 was transmitted and lost, causing a second timeout and retransmission "
        "of Frames 7, 8, and 9 (3 retransmissions). Total retransmissions = <b>6</b> across 2 timeout events.<br/>"
        "&bull; <i>At W = 5:</i> Because the window is wider, Frames 4, 5, 6, 7, and 8 were transmitted in a single pipeline burst. "
        "Frame 4 and Frame 7 were both lost on their first attempt during this burst. When timeout on Frame 4 expired at t=13.5 TU, "
        "GBN retransmitted all five in-flight frames: [4, 5, 6, 7, 8]. Because Frame 7 was retransmitted during this burst, its attempt "
        "count became 2, which arrived safely! This <b>repaired Frame 7 simultaneously within the same window retransmission</b>, "
        "preventing a second timeout. Hence, GBN W=5 required only <b>5 retransmissions and 1 timeout</b>."
    )
    story.append(Paragraph(finding_2, body_style))

    finding_3 = (
        "<b>3. Pipelining Completion Time Benefit:</b> Increasing window size to W=5 reduced completion time from 36.8 TU to 23.4 TU "
        "in GBN (-36.4%) and from 27.4 TU to 19.0 TU in SR (-30.7%), verifying that larger windows maximize throughput."
    )
    story.append(Paragraph(finding_3, body_style))

    # ----------------------------------------------------------------------------------
    # SOLVED UNIVERSITY EXAM QUESTION
    # ----------------------------------------------------------------------------------
    story.append(Spacer(1, 6))
    story.append(Paragraph("8. Solved University Examination Numerical (ITUC201 Syllabus Standard)", h1_style))
    exam_q = (
        "<b>Problem:</b> A 100 km terrestrial link operates at 10 Mbps with propagation velocity v = 2 &times; 10<sup>8</sup> m/s. "
        "Data frame size is 1000 bytes (8000 bits), and ACKs are negligible.<br/>"
        "1. Calculate transmission delay (T<sub>t</sub>), propagation delay (T<sub>p</sub>), and link parameter a.<br/>"
        "2. Compute maximum throughput under Stop-and-Wait ARQ.<br/>"
        "3. Find the optimal window size (W<sub>opt</sub>) for 100% channel utilization.<br/>"
        "4. Determine the minimum sequence number field bits (m) for Go-Back-N and Selective Repeat.<br/><br/>"
        "<b>Solution:</b><br/>"
        "&bull; <b>Step 1:</b> T<sub>t</sub> = 8000 bits / (10 &times; 10<sup>6</sup> bps) = 0.8 ms. "
        "T<sub>p</sub> = 100,000 m / (2 &times; 10<sup>8</sup> m/s) = 0.5 ms.<br/>"
        "&bull; <b>Step 2:</b> a = T<sub>p</sub> / T<sub>t</sub> = 0.5 ms / 0.8 ms = <b>0.625</b>.<br/>"
        "&bull; <b>Step 3:</b> Stop-and-Wait Efficiency &eta;<sub>SW</sub> = 1 / (1 + 2a) = 1 / (1 + 2(0.625)) = 1 / 2.25 &approx; <b>44.44%</b>. "
        "Throughput = 0.4444 &times; 10 Mbps = <b>4.44 Mbps</b>.<br/>"
        "&bull; <b>Step 4:</b> Optimal Window W<sub>opt</sub> &ge; 1 + 2a = 1 + 1.25 = 2.25 &rarr; <b>&lceil;2.25&rceil; = 3 frames</b>.<br/>"
        "&bull; <b>Step 5: Sequence Number Bits (m):</b><br/>"
        "&nbsp;&nbsp;&bull; <b>Go-Back-N:</b> W<sub>s</sub> &le; 2<sup>m</sup> - 1 &rarr; 3 &le; 2<sup>m</sup> - 1 &rarr; 2<sup>m</sup> &ge; 4 &rarr; <b>m &ge; 2 bits</b>.<br/>"
        "&nbsp;&nbsp;&bull; <b>Selective Repeat:</b> W<sub>s</sub> + W<sub>r</sub> &le; 2<sup>m</sup> &rarr; 2(3) &le; 2<sup>m</sup> &rarr; 2<sup>m</sup> &ge; 6 &rarr; <b>m &ge; 3 bits</b>."
    )
    story.append(Paragraph(exam_q, callout_style))

    # ----------------------------------------------------------------------------------
    # CONCLUSION & REPRODUCIBILITY
    # ----------------------------------------------------------------------------------
    story.append(Paragraph("9. Conclusion & Execution Instructions", h1_style))
    concl_text = (
        "<b>Conclusion:</b> Selective Repeat offers superior channel efficiency under losses by confining retransmissions "
        "strictly to corrupted frames. Go-Back-N exhibits higher bandwidth waste but benefits significantly from window pipelining, "
        "which can consolidate multiple in-flight losses into a single retransmission cycle.<br/><br/>"
        "<b>Reproducing the Simulator:</b><br/>"
        "&bull; Automated CLI Benchmark: <code>python arq_simulator.py</code><br/>"
        "&bull; Interactive Streamlit Dashboard: <code>python -m streamlit run app.py</code>"
    )
    story.append(Paragraph(concl_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[PDF] Technical report generated successfully at: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    target_pdf = os.path.join(out_dir, "Technical_Report.pdf")
    build_pdf(target_pdf)
