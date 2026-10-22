# NetVista 3D: Go-Back-N and Selective Repeat ARQ Simulator

**Course:** ITUC201 — Fundamentals of Computer Networks (B.Tech Computer Science & Engineering, Semester 3)  
**Academic Year:** 2026–2027  
**Student ID:** 25CS024  
**Assigned Topic:** Go-Back-N and Selective Repeat under losses  
**Task Category:** Advanced Investigation (20 Marks)  
**Primary Research Question:** *How do retransmission counts change with window size and loss pattern?*  

---

## 1. Project Overview

`NetVista 3D` is an academic-grade, event-driven network simulator designed to demonstrate, benchmark, and visualize the error-recovery and pipelining dynamics of two fundamental sliding-window protocols:
1. **Go-Back-N (GBN) ARQ**
2. **Selective Repeat (SR) ARQ**

The simulator models sender and receiver finite state machines, pipelining, transmission delays, propagation delays, timer management, cumulative vs. selective acknowledgments, receiver buffering vs. discarding, and deterministic first-attempt packet losses (specifically targeting data frames 4 and 7).

### Key Architectural & Interface Highlights
- **Priority-Queue Discrete-Event Architecture:** Implemented via Python's standard library `heapq`. Simulation time progresses strictly from event to event, avoiding artificial sleep loops, polling, or timing drift.
- **Fair Experimental Baseline:** Identical frame payloads (10 unique frames: 0 through 9), transmission delays ($1.0\text{ TU}$), propagation delays ($1.5\text{ TU}$), and retransmission timeout thresholds ($6.0\text{ TU}$) are maintained across all tests.
- **ARQ LIVE LAB Interactive Dashboard:**
  - **Live Sender–Channel–Receiver Animation:** Displays active frames flying across the channel with directional arrows and ACKs flying back.
  - **Prominent Loss Alerts:** Visualizes Frame 4 and Frame 7 drops midway on the channel with flashing red banners (`FRAME 4 LOST` / `FRAME 7 LOST`).
  - **Full Playback Controls:** Play/Pause/Resume, Step Forward, Reset, and Speed toggles (0.5x, 1x, 2x, 4x) with step scrubber.
  - **Numbered Frame Ribbon:** Displays boxes `[0]` to `[9]` with color-coded states (Waiting, In-Flight, Lost, Retransmitted, Buffered, Delivered) and moving Sender/Receiver window brackets.
  - **Live Statistics Panel:** 8 real-time cards tracking original transmissions, retransmissions, ACKs, timeouts, deliveries, and simulation time.
  - **Real-Time Event Log:** Auto-scrolling chronological event trace with color-coded badges.
- **Space-Time Ladder Diagrams:** Automatically produces graphical space-time timelines for every experiment, distinguishing original frames, dropped packets, normal ACKs, duplicate ACKs, timeouts, and retransmissions.
- **Dual Execution Interfaces:** A lightning-fast automated Command-Line Interface (`arq_simulator.py`) for reproducible research, and the interactive web dashboard (`app.py`).

---

## 2. Directory Structure

```text
ARQ_Project/
│
├── arq_simulator.py                 # Core discrete-event simulator & CLI runner
├── app.py                           # Interactive Streamlit dashboard
├── requirements.txt                 # External Python dependencies
├── README.md                        # Project documentation and reproduction guide
├── results.csv                      # Measured benchmark data from actual simulation runs
│
├── event_logs/                      # Chronological event trace logs in CSV format
│   ├── event_log_GBN_W3.csv         # Event log for Go-Back-N (Window = 3)
│   ├── event_log_GBN_W5.csv         # Event log for Go-Back-N (Window = 5)
│   ├── event_log_SR_W3.csv          # Event log for Selective Repeat (Window = 3)
│   └── event_log_SR_W5.csv          # Event log for Selective Repeat (Window = 5)
│
├── graphs/                          # Generated high-resolution visualization charts
│   ├── timeline_GBN_W3.png          # Space-time ladder diagram for GBN W=3
│   ├── timeline_GBN_W5.png          # Space-time ladder diagram for GBN W=5
│   ├── timeline_SR_W3.png           # Space-time ladder diagram for SR W=3
│   ├── timeline_SR_W5.png           # Space-time ladder diagram for SR W=5
│   ├── comparison_retransmissions.png # Bar chart: Retransmission count comparison
│   ├── comparison_completion_time.png # Bar chart: Simulated completion time comparison
│   ├── comparison_total_transmissions.png # Stacked bar chart: Total data frames sent
│   └── window_size_sensitivity.png  # Slope chart: Retransmissions vs window size
│
├── report/                          # Formal technical documentation
│   ├── Technical_Report.md          # 20-section academic report (editable source)
│   ├── Technical_Report.pdf         # Formatted PDF report with embedded charts & tables
│   └── generate_pdf_report.py       # ReportLab PDF build script
│
├── presentation/                    # University presentation deliverables
│   ├── ARQ_Presentation.pptx        # 14-slide widescreen presentation deck
│   ├── slide_content.md             # Editable slide text and structure
│   └── build_presentation.py        # python-pptx presentation build script
│
└── documentation/                   # Evaluation forms and media scripts
    ├── Video_Presentation_Script.md # Word-for-word 10–15 minute video presentation script
    ├── Student_Submission_Proforma.docx # Institutional submission proforma (pre-filled)
    └── create_proforma.py           # Script that populated the proforma
```

---

## 3. Experimental Configurations & Measured Results

The project rigorously evaluates four controlled experiment configurations:
1. **GBN (W=3):** Go-Back-N, Window Size 3, Frame Losses at [4, 7]
2. **GBN (W=5):** Go-Back-N, Window Size 5, Frame Losses at [4, 7]
3. **SR (W=3):** Selective Repeat, Window Size 3, Frame Losses at [4, 7]
4. **SR (W=5):** Selective Repeat, Window Size 5, Frame Losses at [4, 7]

### Measured Performance Benchmark Table (from `results.csv`)

| Experiment ID | Protocol | Window Size ($W$) | Original Tx | Retransmissions | Total Tx | ACKs Sent | Timeouts | Completion Time (TU) | Application Delivery |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GBN_W3** | Go-Back-N | 3 | 10 | **6** | 16 | 14 | 2 | 36.8 | 10/10 In-Order [OK] |
| **GBN_W5** | Go-Back-N | 5 | 10 | **5** | 15 | 13 | 1 | 23.4 | 10/10 In-Order [OK] |
| **SR_W3** | Selective Repeat | 3 | 10 | **2** | 12 | 10 | 2 | 27.4 | 10/10 In-Order [OK] |
| **SR_W5** | Selective Repeat | 5 | 10 | **2** | 12 | 10 | 2 | 19.0 | 10/10 In-Order [OK] |

### Key Scientific Findings:
1. **Selective Repeat Retransmission Invariance:** In SR, retransmissions remain strictly at **2 frames** regardless of window size ($W=3$ or $W=5$). Because the receiver buffers out-of-order frames, unaffected frames (e.g. 5, 6, 8, 9) are never retransmitted.
2. **Go-Back-N Window Dynamics (The 6 vs 5 Result):**
   - At $W=3$, Frame 4 and Frame 7 fall into separate window bursts, triggering two separate timeouts ($3 + 3 = 6$ retransmissions).
   - At $W=5$, both Frame 4 and Frame 7 were in flight within the same window burst $[4, 5, 6, 7, 8]$. When timeout on Frame 4 expired, the sender retransmitted all 5 frames. Because Frame 7 was retransmitted during this burst, it arrived safely as Attempt 2. This **repaired Frame 7 simultaneously within the same cycle**, avoiding a second timeout!
3. **Pipelining Acceleration:** Increasing window size to 5 cut completion time by 36.4% in GBN (36.8 to 23.4 TU) and 30.7% in SR (27.4 to 19.0 TU).

---

## 4. Definitions of Reported Metrics

- **Original Transmissions:** Number of unique data frames sent for the first time ($N=10$).
- **Retransmissions:** Count of subsequent frame retransmissions (attempt $\ge 2$). ACK retransmissions are excluded.
- **Total Data-Frame Transmissions:** Sum of original transmissions and retransmissions.
- **ACK Count:** Total acknowledgment frames transmitted by the receiver.
- **Timeout Count:** Number of timer expiration events triggering retransmissions.
- **Completion Time (TU):** Total elapsed simulated time units from the start of Frame 0 transmission until the final acknowledgment arrives at the sender.
- **In-Order Delivery:** Boolean verification that all 10 frames were delivered to the application layer in strict ascending sequence $\{0, 1, 2, \dots, 9\}$ without gaps or duplicates.

---

## 5. Software Requirements & Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Operating System: Windows, macOS, or Linux

### Installation
From the project folder, install the required packages:
```bash
pip install -r requirements.txt
```

---

## 6. How to Run

### Option A: Run the Automated CLI Benchmark (Recommended)
To execute all four experiments, print the results table, and generate all output files:
```bash
python arq_simulator.py
```
**Expected CLI Output:**
- Prints execution progress for all 4 experiments.
- Generates 4 event logs in `event_logs/`.
- Generates 4 ladder diagrams and 4 comparison graphs in `graphs/`.
- Updates `results.csv`.
- Prints the master benchmark table to the console.

### Option B: Run the Interactive Web Dashboard
To launch the interactive GUI:
```bash
python -m streamlit run app.py
```
*(Or simply: `streamlit run app.py`)*

The dashboard will launch in your browser at `http://localhost:8501`. You can:
- Toggle between Go-Back-N and Selective Repeat.
- Dynamically adjust window size (1 to 8), total frames, and loss frame IDs.
- Inspect the space-time ladder diagrams live.
- Filter and search the event log.
- View the solved ITUC201 university exam numerical problem.

---

## 7. Troubleshooting

- **`ModuleNotFoundError`:** Run `pip install -r requirements.txt` to ensure `matplotlib`, `streamlit`, `pandas`, `reportlab`, `python-docx`, and `python-pptx` are installed.
- **Matplotlib GUI Errors:** `arq_simulator.py` uses the non-interactive `'Agg'` backend (`matplotlib.use('Agg')`), allowing headless execution on any terminal or cloud server without display errors.
- **Rebuilding Reports/Slides:**
  - To regenerate the PDF report: `python report/generate_pdf_report.py`
  - To regenerate the PowerPoint presentation: `python presentation/build_presentation.py`
  - To regenerate the Word proforma: `python documentation/create_proforma.py`

---

## 8. Academic Integrity & AI Assistance Statement

This project was developed for individual assessment in **ITUC201: Fundamentals of Computer Networks**.
In accordance with the institutional academic integrity policy:
- **Core Concept & Verification:** All protocol state machines, timing models, mathematical derivations, and result interpretations were verified by the student against standard textbooks (*Kurose & Ross*, *Forouzan*, *Tanenbaum*).
- **AI-Assisted Development Note:** An AI coding assistant (Antigravity / DeepMind) was utilized as a development tool to accelerate code structure scaffolding, script formatting, ReportLab PDF styling, and LaTeX notation rendering. All simulation results were produced directly through actual code execution and validated for technical accuracy.
- **Declaration:** No experimental data was fabricated or hardcoded. All charts and numbers in the report, presentation, and tables stem from actual simulator outputs.
