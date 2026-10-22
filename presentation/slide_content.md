# Presentation Slide Deck: NetVista 3D ARQ Simulator
**Topic:** Go-Back-N and Selective Repeat ARQ under Deterministic Losses  
**Course:** ITUC201 — Fundamentals of Computer Networks (B.Tech CSE, Sem 3)  
**Student ID:** 25CS024  
**Total Slides:** 14  

---

### Slide 1: Title Slide
- **Title:** NetVista 3D: Performance Evaluation of Go-Back-N and Selective Repeat ARQ
- **Subtitle:** Event-Driven Simulation of Sliding Window Protocols under Frame Losses
- **Student ID:** 25CS024
- **Course:** ITUC201 — Fundamentals of Computer Networks
- **Department:** Faculty of Technology & Applied Sciences, Computer Science & Engineering
- **Academic Year:** 2026–2027

---

### Slide 2: Objectives & Research Problem Statement
- **Research Question:** *How do retransmission counts change with window size and loss pattern?*
- **Primary Objectives:**
  - Build a discrete-event simulator for Go-Back-N (GBN) and Selective Repeat (SR).
  - Subject both protocols to identical deterministic frame drops (Frames 4 and 7).
  - Compare small ($W=3$) vs large ($W=5$) window sizes.
  - Analyze trade-offs between buffer requirements, channel efficiency, and completion time.
  - Connect findings to university examination problems on channel utilization and sequence number sizing.

---

### Slide 3: Reliable Data Transmission & ARQ Overview
- **Why ARQ?** Physical channels introduce attenuation, noise, and frame corruption.
- **Stop-and-Wait Limitations:** Link efficiency $\eta = \frac{1}{1 + 2a}$, where $a = T_p / T_t$. Low throughput on high-latency links.
- **The Sliding Window Solution:** Pipelining allows sending up to $W$ frames concurrently before pausing for acknowledgments.
- **Theoretical 100% Saturation Condition:** $W \ge 1 + 2a$.
- **Error Recovery Classification:**
  - *Go-Back-N:* Discards out-of-order packets; retransmits from the point of failure.
  - *Selective Repeat:* Buffers out-of-order packets; retransmits solely the damaged frame.

---

### Slide 4: Go-Back-N (GBN) Working Principle
- **Sender Operation:**
  - Maintains sliding window $[send\_base, send\_base + W - 1]$.
  - Single logical timer attached to the oldest unacknowledged frame ($send\_base$).
  - When timer expires, sender retransmits **all** in-flight frames: $[send\_base, next\_seq - 1]$.
- **Receiver Operation:**
  - Window size $W_r = 1$. Strict in-order acceptance.
  - Any out-of-order frame is discarded immediately.
  - Generates **Cumulative ACKs**: ACK $n$ confirms receipt of all frames $\le n$.
  - Sends duplicate ACKs for the last in-order frame upon receiving out-of-order packets.

---

### Slide 5: Selective Repeat (SR) Working Principle
- **Sender Operation:**
  - Window size $W_s$ identical to receiver window $W_r$.
  - **Individual timers** for every unacknowledged frame.
  - On timeout of frame $k$, retransmits **only** frame $k$.
  - Window slides forward when the frame at $send\_base$ is acknowledged.
- **Receiver Operation:**
  - Window size $W_r = W_s$.
  - Accepts and **buffers** any uncorrupted frame within $[rcv\_base, rcv\_base + W_r - 1]$.
  - Generates **Individual / Selective ACKs** confirming exact frame numbers.
  - Delivers contiguous buffered frames to application layer and advances $rcv\_base$.

---

### Slide 6: Architectural Comparison: GBN vs Selective Repeat
- **Receiver Window:** GBN $W_r = 1$ vs SR $W_r = W_s$.
- **Receiver Buffering:** GBN has 0 buffer vs SR has $W_r$ buffer slots.
- **Acknowledgment:** GBN Cumulative vs SR Individual.
- **Timers:** GBN single timer vs SR per-frame timer.
- **Retransmissions:** GBN retransmits $N$ frames vs SR retransmits 1 frame.
- **Sequence Number Requirement:**
  - GBN: $W_s \le 2^m - 1$
  - SR: $W_s + W_r \le 2^m \implies W_s \le 2^{m-1}$ (prevents ambiguity).

---

### Slide 7: Event-Driven Simulator Architecture
- **Engine Design:** Python priority queue (`heapq`) based discrete-event simulation (DES).
- **Event Types:**
  - `FRAME_TX_READY`: Transmission burst scheduling.
  - `FRAME_ARRIVAL`: Delivery to receiver / loss check.
  - `ACK_ARRIVAL`: Sender window advancement and timer management.
  - `TIMEOUT_GBN` / `TIMEOUT_SR`: Re-transmission dispatch.
- **Simulation Clock:** Explicit normalized Time Units (TU).
- **Determinism:** Tie-breaking via unique incremental sequence IDs. Zero race conditions or polling loops.

---

### Slide 8: Experimental Setup & Parameters
- **Data Volume:** 10 discrete frames (Sequence numbers 0 to 9).
- **Latency Setup:**
  - Frame transmission delay ($T_t$) = $1.0\text{ TU}$
  - Propagation delay ($T_p$) = $1.5\text{ TU}$
  - ACK transmission delay = $0.2\text{ TU}$, ACK propagation = $1.5\text{ TU}$
  - Round Trip Time (RTT) $\approx 4.2\text{ TU}$
  - Retransmission Timeout (RTO) = $6.0\text{ TU}$
- **Deterministic Loss Rule:** Frames **4 and 7** are dropped on **first transmission attempt only**. Retransmissions succeed.
- **Fairness:** Identical channel delays, frames, and drop points across all four experiments.

---

### Slide 9: Demonstration of Losses at Frames 4 and 7
- **Frame 4 Loss Event:**
  - First attempt of Frame 4 is dropped by channel.
  - In GBN: Subsequent frames arriving at receiver are discarded; duplicate ACKs returned.
  - In SR: Subsequent frames arriving at receiver are buffered; individual ACKs returned.
- **Frame 7 Loss Event:**
  - First attempt of Frame 7 is dropped by channel.
  - Similar recovery triggered depending on protocol rules and active window state.

---

### Slide 10: Experimental Results: Window Size W = 3
- **GBN (W=3):**
  - Retransmissions = **6** (Frames 4, 5, 6 after Timeout 4; Frames 7, 8, 9 after Timeout 7).
  - Timeouts = **2**
  - Completion Time = **36.8 TU**
- **SR (W=3):**
  - Retransmissions = **2** (Only Frame 4 and Frame 7).
  - Timeouts = **2**
  - Completion Time = **27.4 TU**
- **Takeaway:** Selective Repeat saves 4 data-frame retransmissions and finishes 25.5% faster!

---

### Slide 11: Experimental Results: Window Size W = 5
- **GBN (W=5):**
  - Retransmissions = **5** (Frames 4, 5, 6, 7, 8 in a single burst).
  - Timeouts = **1**
  - Completion Time = **23.4 TU**
- **SR (W=5):**
  - Retransmissions = **2** (Only Frame 4 and Frame 7).
  - Timeouts = **2**
  - Completion Time = **19.0 TU**
- **Key Discovery:** In GBN W=5, Frame 7 was repaired within the Frame 4 retransmission burst, avoiding a second timeout!

---

### Slide 12: Graphs & Scientific Interpretation
- **Retransmission Invariance:** SR requires exactly 2 retransmissions across both $W=3$ and $W=5$.
- **Window Consolidation in GBN:** Larger window consolidated two separate loss events into a single window retransmission.
- **Pipelining Speedup:**
  - GBN: Completion time improved from 36.8 TU down to 23.4 TU (-36.4%).
  - SR: Completion time improved from 27.4 TU down to 19.0 TU (-30.7%).
- **Receiver Buffer Value:** Buffering at receiver directly conserves network bandwidth.

---

### Slide 13: Solved University Examination Numerical
- **Problem:** $100\text{ km}$ link, $10\text{ Mbps}$, $v = 2 \times 10^8\text{ m/s}$, Frame = $1000\text{ bytes}$ ($8000\text{ bits}$).
- **Calculations:**
  - $T_t = 8000 / (10 \times 10^6) = 0.8\text{ ms}$
  - $T_p = 100,000 / (2 \times 10^8) = 0.5\text{ ms}$
  - $a = T_p / T_t = 0.5 / 0.8 = 0.625$
  - Stop-and-Wait Efficiency = $\frac{1}{1 + 2(0.625)} = 44.44\%$
  - Optimal Window $W_{opt} \ge 1 + 2a = 2.25 \implies \mathbf{3\text{ frames}}$
- **Required Sequence Bits ($m$):**
  - GBN: $W_s \le 2^m - 1 \implies 3 \le 2^m - 1 \implies \mathbf{m \ge 2\text{ bits}}$
  - SR: $2 W_s \le 2^m \implies 6 \le 2^m \implies \mathbf{m \ge 3\text{ bits}}$

---

### Slide 14: Conclusion & References
- **Conclusion:**
  - Selective Repeat isolates frame errors through receiver buffering; retransmissions equal the exact number of damaged frames.
  - Go-Back-N retransmits undamaged frames, but larger windows improve overall completion time via pipelining.
- **Software Deliverables:**
  - CLI Simulator: `python arq_simulator.py`
  - Interactive Dashboard: `python -m streamlit run app.py`
- **Key References:**
  - Kurose & Ross, *Computer Networking: A Top-Down Approach* (8th ed., Pearson).
  - Forouzan, *Data Communications and Networking* (5th ed., McGraw-Hill).
