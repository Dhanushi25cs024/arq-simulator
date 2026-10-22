# TECHNICAL REPORT: PERFORMANCE EVALUATION OF GO-BACK-N AND SELECTIVE REPEAT ARQ PROTOCOLS UNDER DETERMINISTIC FRAME LOSSES

**Course Code:** ITUC201 — Fundamentals of Computer Networks  
**Academic Degree:** Bachelor of Technology (B.Tech.), Semester 3  
**Academic Year:** 2026–2027  
**Student ID / Enrollment:** 25CS024  
**Assigned Topic:** Go-Back-N and Selective Repeat under losses  
**Task Category:** Advanced Investigation  
**Primary Research Question:** *How do retransmission counts change with window size and loss pattern?*  

---

## 1. Title Page and Identification
- **Institution:** Department of Computer Science & Engineering, Faculty of Technology & Applied Sciences
- **Student ID:** 25CS024
- **Subject:** ITUC201: Fundamentals of Computer Networks
- **Evaluation Weightage:** 20 Marks (CIE Component)
- **Software Deliverables:** Event-Driven ARQ Simulation Suite (`arq_simulator.py`), Interactive Dashboard (`app.py`), Data Tables, Charts, Presentation Deck, Video Script

---

## 2. Abstract
Reliable data transfer across imperfect physical communication links represents one of the foundational challenges of computer networking. This report investigates the operational mechanics and comparative performance of two canonical sliding-window Automatic Repeat reQuest (ARQ) error-control protocols: **Go-Back-N (GBN)** and **Selective Repeat (SR)**. A custom discrete-event network simulator was implemented in Python using a priority-queue (`heapq`) scheduling architecture. The investigation models a sequence of 10 data frames transmitted over a channel characterized by propagation delay, frame transmission delay, and deterministic first-transmission frame drops at sequence numbers 4 and 7. Controlled experiments systematically evaluated sender window sizes $W \in \{3, 5\}$. Quantitative metrics—including original transmissions, retransmission count, total channel transmissions, cumulative/individual ACK generation, timeout expirations, simulation completion time (in simulated time units), and in-order application delivery—were rigorously collected. The findings demonstrate that Selective Repeat achieves an invariant retransmission count of exactly 2 frames regardless of window size, retransmitting solely the corrupted frames due to receiver-side buffering. In contrast, Go-Back-N exhibits window-dependent retransmission overhead: window size 3 produced 6 retransmissions across 2 distinct timeout cycles, whereas window size 5 consolidated retransmission of the damaged frames into a single window burst of 5 frames, cutting completion time by 36.4%. A fully solved university examination numerical on channel bandwidth-delay product, utilization, and sequence number sizing is presented alongside installation and reproducibility guidelines.

---

## 3. Problem Statement and Objectives

### 3.1 Problem Statement
In real-world computer networks, packets traversing physical media (copper, fiber, wireless) are prone to bit errors, frame corruption, buffer overflows, and packet loss. While Stop-and-Wait ARQ provides reliable transfer, its link utilization is severely constrained by the channel's propagation delay (RTT). Sliding window protocols overcome this limitation via pipelining, allowing multiple frames to be in transit simultaneously before requiring an acknowledgment. However, when frames are lost in transit, the sender and receiver protocols adopt vastly divergent recovery strategies:
1. Does Go-Back-N's rejection of out-of-order frames impose an excessive retransmission penalty as window size expands?
2. How does Selective Repeat's localized buffer isolate losses from unaffected frames?
3. What is the quantitative impact of window size ($W=3$ vs. $W=5$) when multiple deterministic frame losses occur in close sequence?

### 3.2 Objectives
The specific engineering and academic objectives of this project are:
- To design, implement, and validate an event-driven discrete-event simulation engine in Python for both GBN and SR ARQ protocols.
- To enforce identical deterministic loss conditions (loss of Frame 4 and Frame 7 on their initial transmission attempt) across all configurations for controlled, bias-free comparative analysis.
- To trace and visualize the lifecycle of every frame, ACK, timeout, and retransmission via space-time ladder diagrams.
- To measure and analyze the sensitivity of retransmission counts and completion time to changes in window size ($W=3$ vs. $W=5$).
- To link experimental findings to foundational computer networking theory and solve a representative university examination numerical problem.

---

## 4. Essential Theory of Sliding-Window ARQ
The Stop-and-Wait protocol achieves a link efficiency of $\eta = \frac{T_t}{T_t + 2T_p} = \frac{1}{1 + 2a}$, where $a = \frac{T_p}{T_t}$. When the propagation delay ($T_p$) is large relative to the transmission delay ($T_t$), $a \gg 1$ and link utilization drops toward zero.

Pipelining overcomes this bottleneck by allowing the sender to transmit up to $W$ frames continuously before waiting for an acknowledgment. The theoretical maximum utilization of a sliding-window protocol without errors is:
$$\eta_{ideal} = \min\left(1, \frac{W \cdot T_t}{T_t + 2T_p}\right) = \min\left(1, \frac{W}{1 + 2a}\right)$$
To achieve 100% link utilization ($\eta = 1$), the window size must satisfy:
$$W \ge 1 + 2a$$
When frames are lost, retransmission strategies govern both channel efficiency and buffer management.

---

## 5. Go-Back-N (GBN) Working Principle

### 5.1 Sender Logic
- **Window Boundaries:** The sender maintains a window of size $W_s$ bounded by $[send\_base, send\_base + W_s - 1]$. The variable $next\_seq\_num$ points to the next unsent frame.
- **Pipelined Transmission:** New frames are transmitted whenever $(next\_seq\_num - send\_base) < W_s$.
- **Timer Management:** GBN uses a **single logical timer** corresponding to the oldest unacknowledged frame ($send\_base$). If the window was previously empty, the timer starts upon sending $send\_base$. When an ACK arrives that advances $send\_base$, the timer is stopped if all frames are acknowledged, or restarted for the remaining in-flight frames.
- **Timeout Recovery:** When the timer expires, the sender assumes that frame $send\_base$ (and potentially all subsequent transmitted frames) were lost or unacknowledged. The sender "goes back N" frames and retransmits **all** frames currently in the pipeline: $[send\_base, next\_seq\_num - 1]$.

### 5.2 Receiver Logic
- **Receiver Window:** $W_r = 1$. The receiver maintains a single variable $expected\_seq\_num = rcv\_base$.
- **In-Order Arrival:** If the arriving frame sequence number matches $rcv\_base$, it is accepted, passed to the application layer, $rcv\_base$ increments by 1, and a **cumulative ACK** for $rcv\_base - 1$ is returned.
- **Out-of-Order Arrival:** If any frame arrives with $f\_id \ne rcv\_base$, the receiver **discards** it unconditionally and re-sends a duplicate cumulative ACK for the highest consecutively received frame ($rcv\_base - 1$). The receiver has zero buffer memory for out-of-order frames.

---

## 6. Selective Repeat (SR) Working Principle

### 6.1 Sender Logic
- **Window Boundaries:** The sender window $[send\_base, send\_base + W_s - 1]$ accommodates up to $W_s$ frames.
- **Independent Timers:** Each transmitted frame has its own **individual logical timer**.
- **Selective ACKs:** The sender receives individual ACKs confirming specific frames. Upon receiving ACK($k$), frame $k$ is marked as acknowledged and its specific timer is stopped.
- **Window Movement:** If $k = send\_base$, $send\_base$ advances forward past all contiguous acknowledged frames.
- **Timeout Recovery:** When the timer for frame $k$ expires, **only frame $k$** is retransmitted. Uncorrupted frames already acknowledged or in flight are not retransmitted.

### 6.2 Receiver Logic
- **Receiver Window:** $W_r = W_s$. The receiver window spans $[rcv\_base, rcv\_base + W_r - 1]$.
- **Buffering:** If an incoming frame $f\_id$ falls within $[rcv\_base, rcv\_base + W_r - 1]$, it is accepted and placed into a receiver buffer. An individual ACK($f\_id$) is transmitted back to the sender.
- **In-Order Delivery:** If $f\_id = rcv\_base$, the receiver delivers $rcv\_base$ and any consecutive buffered frames to the application layer, sliding $rcv\_base$ forward.
- **Duplicate Handling:** If a frame arrives with $f\_id \in [rcv\_base - W_r, rcv\_base - 1]$, it is recognized as an already delivered duplicate; the receiver re-generates ACK($f\_id$) to ensure the sender clears its window.

---

## 7. Comparative Analysis of GBN vs Selective Repeat

| Feature / Metric | Go-Back-N (GBN) | Selective Repeat (SR) |
| :--- | :--- | :--- |
| **Receiver Window Size ($W_r$)** | Exactly 1 | Equal to Sender Window ($W_s$) |
| **Receiver Out-of-Order Buffering** | Discards all out-of-order frames | Buffers all valid out-of-order frames |
| **Acknowledgment Mechanism** | Cumulative ACKs (ACK $n$ confirms $\le n$) | Individual / Selective ACKs (ACK $n$ confirms only $n$) |
| **Sender Timer Architecture** | Single timer for oldest unACKed frame | Dedicated independent timer per frame |
| **Retransmission Scope on Timeout** | All outstanding frames ($send\_base$ to $next - 1$) | Exactly one frame (the timed-out frame) |
| **Bandwidth Efficiency under Loss** | Low (retransmits undamaged frames) | High (retransmits strictly lost frames) |
| **Implementation Complexity** | Simple (minimal memory at receiver) | Higher (buffer management & sorting) |
| **Sequence Number Constraint** | $W_s \le 2^m - 1$ | $W_s + W_r \le 2^m \implies W_s \le 2^{m-1}$ |

---

## 8. Simulation Architecture and Event-Driven Methodology

The simulator operates on a pure **Discrete-Event Simulation (DES)** model implemented via Python's standard library `heapq` module. Rather than polling or incrementing a fixed clock tick, time advances directly to the timestamp of the next earliest event in the priority queue.

```
+-------------------------------------------------------------------------------+
|                       DISCRETE-EVENT PRIORITY QUEUE (heapq)                   |
|  Events sorted chronologically: (time, event_counter, event_type, payload)    |
+---------------------------------------+---------------------------------------+
                                        | (pop lowest timestamp)
                                        v
                           +------------------------+
                           |  SIMULATION DISPATCHER |
                           +-----------+------------+
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        v                              v                              v
+---------------+              +---------------+              +---------------+
| FRAME_ARRIVAL |              |  ACK_ARRIVAL  |              |    TIMEOUT    |
| - GBN Check   |              | - Window Slide|              | - GBN: GoBackN|
| - SR Buffer   |              | - Timer Clear |              | - SR: Retrans |
| - Schedule ACK|              | - Send New Tx |              |   Single Frame|
+---------------+              +---------------+              +---------------+
```

Each event is defined as:
```python
@dataclass(order=True)
class SimulationEvent:
    time: float
    event_id: int
    event_type: str = field(compare=False)
    frame_id: Optional[int] = field(compare=False, default=None)
    data: dict = field(compare=False, default_factory=dict)
```
Ties in event timestamps are safely resolved by an auto-incrementing integer `event_id`, eliminating runtime comparison errors and guaranteeing deterministic execution.

---

## 9. Assumptions and Experimental Setup

1. **Simulation Time Units (TU):** All completion steps and latencies are measured in normalized simulation time units.
2. **Channel Latency Parameters:**
   - Frame Transmission Time ($T_t$) = $1.0\text{ TU}$
   - One-Way Propagation Delay ($T_p$) = $1.5\text{ TU}$
   - ACK Transmission Time ($T_{ack}$) = $0.2\text{ TU}$
   - ACK Propagation Delay ($T_{ack\_p}$) = $1.5\text{ TU}$
   - Round Trip Time ($\text{RTT}$) = $1.0 + 1.5 + 0.2 + 1.5 = 4.2\text{ TU}$
   - Retransmission Timeout ($\text{RTO}$) = $6.0\text{ TU}$ (configured comfortably above RTT to avoid spurious timeouts).
3. **Traffic Volume:** Exactly 10 data frames (Sequence numbers 0 through 9).
4. **Deterministic Loss Pattern:** Data frames **4 and 7** are dropped by the channel on their **first transmission attempt only**. Retransmissions of frames 4 and 7 are guaranteed to succeed unless configured otherwise.
5. **ACK Delivery:** The reverse channel is lossless in the baseline experiments.

---

## 10. Implementation Details and Algorithms

### 10.1 Go-Back-N State Machine
```
[Sender: Idle] --(Send frame < W)--> [Start Timer if inactive] --> [Channel]
[Receiver] --(Check seq == rcv_base)--> YES: [Deliver, ACK f_id, rcv_base++]
                                    --> NO:  [Discard, Re-send ACK rcv_base-1]
[Sender: On Timeout] --> [Retransmit ALL frames from send_base to next_seq_num - 1]
```

### 10.2 Selective Repeat State Machine
```
[Sender] --(Send frame < W)--> [Start individual Timer f_id] --> [Channel]
[Receiver] --(Check f_id in [rcv_base, rcv_base + W - 1])-->
       YES: [Buffer f_id, Send ACK f_id, Slide rcv_base past contiguous buffered]
[Sender: On Timeout(f_id)] --> [Retransmit ONLY f_id, Restart Timer(f_id)]
```

---

## 11. The Four Experiment Configurations

1. **Experiment 1 (GBN_W3):** Go-Back-N ARQ, Window Size $W=3$, Losses at Frames 4 and 7.
2. **Experiment 2 (GBN_W5):** Go-Back-N ARQ, Window Size $W=5$, Losses at Frames 4 and 7.
3. **Experiment 3 (SR_W3):** Selective Repeat ARQ, Window Size $W=3$, Losses at Frames 4 and 7.
4. **Experiment 4 (SR_W5):** Selective Repeat ARQ, Window Size $W=5$, Losses at Frames 4 and 7.

---

## 12. Actual Measured Results Table

The following measurements were obtained directly from the execution of `arq_simulator.py`. Zero values have been fabricated.

| Metric | Experiment 1: GBN (W=3) | Experiment 2: GBN (W=5) | Experiment 3: SR (W=3) | Experiment 4: SR (W=5) |
| :--- | :---: | :---: | :---: | :---: |
| **Protocol** | Go-Back-N | Go-Back-N | Selective Repeat | Selective Repeat |
| **Sender Window Size ($W_s$)** | 3 | 5 | 3 | 5 |
| **Total Unique Frames** | 10 | 10 | 10 | 10 |
| **Original Transmissions** | 10 | 10 | 10 | 10 |
| **Retransmissions** | **6** | **5** | **2** | **2** |
| **Total Data Frames Sent** | 16 | 15 | 12 | 12 |
| **ACK Packets Generated** | 14 | 13 | 10 | 10 |
| **Timeout Events** | 2 | 1 | 2 | 2 |
| **Processed DES Events** | 39 | 33 | 32 | 31 |
| **Completion Time (TU)** | **36.8** | **23.4** | **27.4** | **19.0** |
| **In-Order Delivery Verified** | **True (10/10)** | **True (10/10)** | **True (10/10)** | **True (10/10)** |

---

## 13. Visual Data Analysis & Comparison Graphs

The simulator generated four comprehensive comparison charts saved in the `graphs/` directory:

### 13.1 Retransmission Comparison (`graphs/comparison_retransmissions.png`)
Shows that Selective Repeat maintains an optimal retransmission count of 2 across both window sizes. GBN requires 6 retransmissions at $W=3$ and 5 retransmissions at $W=5$.

### 13.2 Completion Time Comparison (`graphs/comparison_completion_time.png`)
Depicts how increasing the window size to $W=5$ reduces total transfer time from 36.8 TU to 23.4 TU in GBN (a 36.4% acceleration) and from 27.4 TU to 19.0 TU in SR (a 30.7% acceleration) due to enhanced pipelining.

### 13.3 Total Data-Frame Transmissions (`graphs/comparison_total_transmissions.png`)
Breaks down channel occupancy into original data frames (10) and retransmitted frames (2 to 6).

### 13.4 Window Size Sensitivity (`graphs/window_size_sensitivity.png`)
Directly answers the primary research question by plotting retransmission curves as a function of window size.

---

## 14. Space-Time Ladder Timelines

High-resolution space-time diagrams were generated for each experiment:
- `graphs/timeline_GBN_W3.png`
- `graphs/timeline_GBN_W5.png`
- `graphs/timeline_SR_W3.png`
- `graphs/timeline_SR_W5.png`

Each diagram clearly delineates:
- Blue solid arrows: Original frame transmissions
- Red dashed arrows with bold 'X': First-attempt dropped frames (Frames 4 and 7)
- Green solid arrows: Normal ACKs advancing the window
- Orange dashed arrows: Duplicate cumulative ACKs
- Red dots: Timeout expirations on the Sender timeline
- Purple solid arrows: Protocol retransmissions

---

## 15. Technical Observations and Detailed Interpretation

### 15.1 The Retransmission Invariance of Selective Repeat
In both $W=3$ and $W=5$, Selective Repeat incurred exactly **2 retransmissions**. When Frame 4 was dropped, the receiver successfully accepted and buffered Frames 5 and 6 (in $W=3$) or Frames 5, 6, 7, 8 (in $W=5$). Upon timeout expiration, the sender retransmitted *only* Frame 4. Once Frame 4 arrived, the receiver delivered the entire buffered sequence $[4, 5, 6]$ to the application layer. Similarly, when Frame 7 was dropped, only Frame 7 was retransmitted.

### 15.2 The Go-Back-N Window Dynamics (Explaining the 6 vs 5 Result)
A superficial expectation might assume that increasing GBN's window size always increases retransmissions. However, our rigorous simulation revealed an insightful counter-phenomenon:
- **At $W=3$:** When Frame 4 was lost, the sender window $[4, 5, 6]$ emptied. Timeout on Frame 4 triggered retransmission of Frames 4, 5, 6 (3 retransmissions). The window then advanced. Later, Frame 7 was transmitted and lost; the subsequent timeout on Frame 7 triggered retransmission of Frames 7, 8, 9 (3 retransmissions). Total retransmissions = $3 + 3 = 6$ across **2 distinct timeout events**.
- **At $W=5$:** The sender window $[4, 5, 6, 7, 8]$ allowed Frames 4, 5, 6, 7, 8 to be transmitted in one continuous pipeline burst. Frame 4 was lost. Frame 7 was *also* lost on its initial transmission attempt during this same burst! At $t=13.5\text{ TU}$, the timer for Frame 4 expired. Under Go-Back-N rules, the sender retransmitted the entire outstanding window: Frames 4, 5, 6, 7, and 8 (5 retransmissions). Because Frame 7 was retransmitted during this burst, its attempt number became 2, which successfully arrived at the receiver! Consequently, **Frame 7 was repaired simultaneously with Frame 4 in the very same retransmission burst**, avoiding a second timeout. Thus, GBN at $W=5$ experienced only **1 timeout event and 5 retransmissions**, completing in 23.4 TU rather than 36.8 TU.

---

## 16. Limitations of the Simulation
1. **Deterministic vs. Stochastic Channels:** In real networks, packet drops follow stochastic distributions (e.g., Gilbert-Elliot burst loss models or Poisson packet drop probabilities) rather than fixed sequence numbers.
2. **Reverse Channel Reliability:** ACKs were modeled without transmission errors or drops. In lossy wireless environments, ACK corruption triggers spurious timeouts.
3. **Fixed Window Sizing:** Modern transport protocols (such as TCP Reno and Cubic) employ dynamic congestion windows ($cwnd$) that expand and contract dynamically based on AIMD (Additive Increase / Multiplicative Decrease).

---

## 17. Solved University Examination Question (ITUC201 Syllabus Standard)

### Question:
A point-to-point satellite communication link has a bandwidth of $10\text{ Mbps}$ and a round-trip distance corresponding to a one-way propagation delay of $T_p = 250\text{ ms}$. Data frames are $1250\text{ bytes}$ ($10,000\text{ bits}$) each, and acknowledgment frames are negligibly small.
1. Compute the frame transmission delay ($T_t$).
2. Compute the link parameter $a = T_p / T_t$.
3. What is the maximum throughput achievable using Stop-and-Wait ARQ?
4. Determine the minimum window size ($W_{opt}$) required to achieve 100% link utilization under zero errors.
5. What is the minimum number of sequence number bits ($m$) required for **Go-Back-N** and **Selective Repeat** to support this optimal window size?

### Step-by-Step Solution:

#### Step 1: Transmission Delay ($T_t$)
$$T_t = \frac{\text{Frame Size } (L)}{\text{Bandwidth } (B)} = \frac{10,000\text{ bits}}{10 \times 10^6\text{ bps}} = 0.001\text{ s} = 1.0\text{ ms}$$

#### Step 2: Link Parameter ($a$)
$$a = \frac{T_p}{T_t} = \frac{250\text{ ms}}{1.0\text{ ms}} = 250$$

#### Step 3: Stop-and-Wait ARQ Throughput
The efficiency of Stop-and-Wait is:
$$\eta_{SW} = \frac{T_t}{T_t + 2T_p} = \frac{1}{1 + 2a} = \frac{1}{1 + 2(250)} = \frac{1}{501} \approx 0.001996 \quad (0.1996\%)$$
$$\text{Throughput}_{SW} = \eta_{SW} \times B = 0.001996 \times 10\text{ Mbps} = 19.96\text{ kbps}$$
*(This illustrates why Stop-and-Wait is unusable on high-latency satellite channels).*

#### Step 4: Optimal Window Size ($W_{opt}$) for 100% Utilization
To pipeline frames and fully saturate the channel:
$$W_{opt} \ge 1 + 2a = 1 + 2(250) = 501\text{ frames}$$
Therefore, the sender must be able to transmit at least **501 frames** per RTT.

#### Step 5: Required Sequence Number Bits ($m$)
- **For Go-Back-N:**
  In GBN, the sender window must satisfy $W_s \le 2^m - 1$:
  $$2^m - 1 \ge 501 \implies 2^m \ge 502$$
  Since $2^8 = 256$ and $2^9 = 512$:
  $$m \ge 9\text{ bits}$$
  *(With $m=9$, $2^9 - 1 = 511 \ge 501$).*

- **For Selective Repeat:**
  In SR, the sender and receiver windows satisfy $W_s + W_r \le 2^m$. For symmetric windows ($W_s = W_r$):
  $$2 W_s \le 2^m \implies W_s \le 2^{m-1}$$
  $$2^{m-1} \ge 501$$
  Since $2^8 = 256$ and $2^9 = 512$:
  $$m - 1 \ge 9 \implies m \ge 10\text{ bits}$$
  *(With $m=10$, maximum window size is $2^9 = 512 \ge 501$).*

---

## 18. Conclusion

This academic investigation resolves the research question:
> **"How do retransmission counts change with window size and loss pattern?"**

1. **Selective Repeat is immune to window size penalties:** Because the receiver buffers out-of-order packets, the retransmission count is strictly bounded to the number of damaged frames ($R = 2$ in all tests), maximizing bandwidth utilization.
2. **Go-Back-N retransmission count depends intimately on loss dispersion relative to window size:** 
   - When lost frames are separated by more than $W$, each loss triggers an independent Go-Back-N cascade ($3 + 3 = 6$ retransmissions at $W=3$).
   - When the window is large enough to encompass both lost frames simultaneously, the window retransmission repairs subsequent in-flight losses within the same cycle ($5$ retransmissions at $W=5$), eliminating duplicate timeouts.
3. **Pipelining dramatically accelerates completion time:** Window expansion from $W=3$ to $W=5$ reduced completion time by 36.4% in GBN and 30.7% in SR, proving the overwhelming utility of pipelined ARQ over Stop-and-Wait on high-latency links.

---

## 19. References
1. Kurose, J. F., & Ross, K. W. (2021). *Computer Networking: A Top-Down Approach* (8th ed.). Pearson. Chapter 3: Transport Layer (Principles of Reliable Data Transfer, pp. 200–225).
2. Forouzan, B. A. (2017). *Data Communications and Networking* (5th ed.). McGraw-Hill Education. Chapter 11: Data Link Control (Framing, Flow and Error Control, pp. 311–340).
3. Tanenbaum, A. S., & Wetherall, D. J. (2014). *Computer Networks* (5th ed.). Pearson. Chapter 3: The Data Link Layer (Sliding Window Protocols, pp. 216–235).
4. Stallings, W. (2014). *Data and Computer Communications* (10th ed.). Pearson Education. Chapter 7: Flow Control and Error Control.

---

## 20. Instructions for Installation, Execution, and Reproduction

### 20.1 System Prerequisites
- Python 3.10 or higher
- Required packages: `pip install -r requirements.txt`

### 20.2 Reproducing All Experiments via CLI
Run the automated benchmark suite from the project root:
```bash
python arq_simulator.py
```
This single command will:
- Run all 4 experiments (GBN W=3, GBN W=5, SR W=3, SR W=5).
- Verify 100% in-order delivery of frames 0 through 9.
- Output detailed event logs to `event_logs/event_log_*.csv`.
- Output four space-time ladder diagrams to `graphs/timeline_*.png`.
- Output four comparison charts to `graphs/comparison_*.png`.
- Save the master benchmark data to `results.csv`.
- Print a formatted summary table to the console.

### 20.3 Launching the Interactive Web Dashboard
To explore custom parameters, loss sequences, or window sizes interactively:
```bash
python -m streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.
