# INDIVIDUAL TECHNICAL VIDEO PRESENTATION SCRIPT
## Project: NetVista 3D — Go-Back-N and Selective Repeat ARQ Simulator
**Course:** ITUC201: Fundamentals of Computer Networks (B.Tech Semester 3)  
**Student ID:** 25CS024  
**Assigned Topic:** Go-Back-N and Selective Repeat under losses  
**Task Type:** Advanced Investigation  
**Suggested Video Duration:** 10 to 15 Minutes  

---

### PRESENTATION PREPARATION CHECKLIST
Before clicking "Record" on OBS / Screen Recorder:
1. Open the PowerPoint slide deck `ARQ_Presentation.pptx` in presentation mode or full-screen window.
2. Have a terminal window ready in the project folder `ARQ_Project` with the command `python arq_simulator.py` prepared.
3. Open a browser window to `http://localhost:8501` with the Streamlit dashboard running (`python -m streamlit run app.py`).
4. Ensure your microphone is clear and background noise is minimal.
5. Keep your student identity card or student ID handy if required for verification.

---

### SLIDE-BY-SLIDE SPOKEN SCRIPT AND SCREEN CUES

#### [0:00 – 1:00] Slide 1: Title Slide & Introduction
- **What to Show on Screen:** Slide 1 (`ARQ_Presentation.pptx` Title Slide).
- **Spoken Narration:**
  > "Respected faculty, evaluator, and colleagues, good day. My name is presenting under Student ID **25CS024**. Today, I am demonstrating my individual advanced computer networks project for **ITUC201: Fundamentals of Computer Networks**, titled **'NetVista 3D: Performance Evaluation of Go-Back-N and Selective Repeat ARQ under Deterministic Losses'**.
  >
  > In this project, I have designed and implemented an event-driven discrete-event network simulator in Python using a priority-queue architecture. The core question I am addressing today is: *'How do retransmission counts change with window size and loss pattern?'* Over the next 12 minutes, I will walk you through the theoretical principles, live executable demonstration, benchmark results, and syllabus examination connections."

---

#### [1:00 – 2:15] Slide 2: Objectives & Research Problem Statement
- **What to Show on Screen:** Slide 2 (Objectives & Core Research Question).
- **Spoken Narration:**
  > "Let us look at our primary research problem. In real-world data link and transport protocols, physical channels are imperfect. While pipelining allows multiple frames to be in transit before requiring an acknowledgment, packet loss introduces overhead.
  >
  > The primary objectives of this study are:
  > First, to build an authentic event-driven simulator in Python for both Go-Back-N and Selective Repeat ARQ without relying on artificial delay loops.
  > Second, to enforce a fair, controlled test environment where exactly 10 frames are transmitted, and frames 4 and 7 suffer deterministic drops on their first attempt.
  > Third, to systematically measure and compare window sizes 3 and 5.
  > And finally, to analyze how receiver buffering fundamentally alters retransmission overhead and link completion time."

---

#### [2:15 – 3:30] Slide 3: Reliable Data Transmission & The ARQ Concept
- **What to Show on Screen:** Slide 3 (Reliable Data Transmission & Sliding Window Concept).
- **Spoken Narration:**
  > "To appreciate sliding window protocols, we must remember the severe limitation of Stop-and-Wait ARQ. In Stop-and-Wait, the sender transmits a single frame and waits for an ACK. Its efficiency is given by eta equals 1 over 1 plus 2a, where 'a' is the ratio of propagation delay to transmission delay. When propagation delay is high—such as across WANs or satellite links—Stop-and-Wait leaves the channel idle for over 90% of the time.
  >
  > Sliding window protocols solve this through pipelining. By allowing up to 'W' frames to be outstanding, the link can achieve 100% saturation if W is greater than or equal to 1 plus 2a. However, when errors occur, protocols diverge: Go-Back-N chooses simplicity by discarding out-of-order packets, while Selective Repeat introduces receiver buffering to avoid retransmitting correctly received data."

---

#### [3:30 – 5:00] Slides 4 & 5: Principles of GBN vs Selective Repeat
- **What to Show on Screen:** Slide 4 (Go-Back-N Principles) followed by Slide 5 (Selective Repeat Principles).
- **Spoken Narration:**
  > "Let's examine how each protocol operates under the hood.
  > In **Go-Back-N (Slide 4)**, the receiver maintains a window size of exactly 1. It only accepts the expected in-order frame. If an out-of-order frame arrives—even if completely uncorrupted—the receiver discards it immediately and sends a duplicate cumulative ACK. The sender maintains a single timer for the oldest unacknowledged frame. If that timer expires, the sender must 'Go Back N' frames, retransmitting the entire in-flight window.
  >
  > Now, contrast this with **Selective Repeat (Slide 5)**. Here, the receiver window equals the sender window. The receiver accepts and buffers any frame that falls within its window, acknowledging each packet with an individual, selective ACK. At the sender, each transmitted frame has its own independent timer. When a timeout occurs, only the specific missing frame is retransmitted. This preserves channel bandwidth at the cost of receiver buffer memory."

---

#### [5:00 – 6:15] Slides 6 & 7: Architectural Comparison & Simulation Engine
- **What to Show on Screen:** Slide 6 (Protocol Matrix) and Slide 7 (Event-Driven Architecture).
- **Spoken Narration:**
  > "Slide 6 highlights the key theoretical distinctions. Notice the crucial sequence number constraint: GBN requires W less than or equal to 2 to the m minus 1, whereas Selective Repeat requires W less than or equal to 2 to the m minus 1, meaning the window size cannot exceed half the sequence number space to prevent duplicate window overlap ambiguity.
  >
  > On Slide 7, I show how I built the simulator. Rather than using fixed time-step loops, I implemented a pure discrete-event simulation model using Python's `heapq` priority queue. Events such as Frame Transmission, Arrival, ACK Arrival, and Timeouts are sorted chronologically. Each event carries an incremental tie-breaker ID to eliminate race conditions. This ensures 100% reproducibility and technical correctness."

---

#### [6:15 – 8:30] LIVE SIMULATOR DEMONSTRATION (Switch to Terminal & Dashboard)
- **What to Show on Screen:** 
  1. Switch screen capture to Terminal (`ARQ_Project` directory).
  2. Run `python arq_simulator.py`.
  3. Briefly switch to the browser displaying `app.py` (Streamlit Dashboard).
- **Spoken Narration:**
  > "Now, let me demonstrate the actual execution of the simulator live.
  > *(In Terminal, run `python arq_simulator.py`)*
  >
  > Notice on my terminal screen: the simulator runs all four experiments automatically.
  > Experiment 1: GBN with window 3. Frame 4 and 7 drop on attempt 1. We observe 6 retransmissions and a completion time of 36.8 time units.
  > Experiment 2: GBN with window 5. Retransmissions drop to 5, and completion time accelerates to 23.4 time units.
  > Experiments 3 and 4: Selective Repeat with window 3 and window 5. In both cases, retransmissions are strictly 2!
  > And most importantly, all four configurations verify: 10 out of 10 frames delivered successfully and in exact ascending order to the application layer.
  >
  > *(Switch to Streamlit browser displaying ARQ LIVE LAB)*
  > "Here is our interactive networking laboratory dashboard: 'ARQ LIVE LAB — Go-Back-N vs Selective Repeat'.
  > When I click 'Play', notice the live animated packets with frame numbers moving along the channel from Sender to Receiver, and ACKs traveling back!
  > Watch closely as Frame 4 moves across the channel: at the midpoint, it turns flashing red and drops, and our prominent warning banner immediately triggers: 'FRAME 4 LOST'!
  > In Go-Back-N, the receiver discards subsequent out-of-order frames, and on timeout, the sender retransmits all outstanding in-flight frames. Notice how the cyan Sender Window and green Receiver Window brackets visibly glide across our numbered frame ribbon from [0] to [9], while our 8 live statistics cards update in real time.
  > If I switch over to Selective Repeat, you can see out-of-order frames safely stored in purple receiver buffer slots, with individual ACKs returned, and only Frame 4 and Frame 7 selectively retransmitted. We can pause, step forward one event at a time, or change playback speed from 0.5x to 4x. This brings the theoretical protocol behavior to life!"

---

#### [8:30 – 10:30] Slides 8 – 11: Results Breakdown & The Research Discovery
- **What to Show on Screen:** Slide 10 (Window Size 3 Results) and Slide 11 (Window Size 5 Results).
- **Spoken Narration:**
  > "Returning to our slides, let us examine the experimental results and answer our primary research question.
  >
  > At **Window Size 3 (Slide 10)**:
  > Selective Repeat required only 2 retransmissions, whereas GBN required 6. When Frame 4 was lost in GBN, the sender had also transmitted Frames 5 and 6. Because the receiver had no buffer, Frames 5 and 6 were discarded. When timeout 4 fired, the sender had to retransmit Frames 4, 5, and 6. Later, Frame 7 was lost, forcing retransmission of Frames 7, 8, and 9. Total = 6 retransmissions across 2 timeouts.
  >
  > Now look at **Window Size 5 (Slide 11)**—this reveals a fascinating result!
  > In GBN with W=5, retransmissions did not increase; they actually decreased to 5! Why?
  > Because the window of 5 allowed Frames 4, 5, 6, 7, and 8 to all be sent in one single burst. Both Frame 4 and Frame 7 suffered first-attempt loss during this burst. When timeout on Frame 4 expired, the sender retransmitted the entire window: 4, 5, 6, 7, and 8. Because Frame 7 was retransmitted in this burst, it reached attempt 2 and was delivered successfully! Frame 7 was repaired in the *same* cycle without requiring a second timeout!
  >
  > Meanwhile, in Selective Repeat, whether W was 3 or 5, retransmissions stayed strictly at 2. Selective Repeat is completely immune to the window size penalty because the receiver buffers out-of-order packets."

---

#### [10:30 – 12:00] Slide 12: Comparison Graphs & Research Conclusion
- **What to Show on Screen:** Slide 12 (Graphs & Scientific Interpretation).
- **Spoken Narration:**
  > "On Slide 12, we see the generated comparison graphs.
  > On the left, the bar chart demonstrates the significant bandwidth savings of Selective Repeat: exactly 2 retransmissions versus 5 and 6 in GBN.
  > On the right, the sensitivity chart plots retransmissions against window size. It clearly illustrates:
  > 1. Selective Repeat achieves invariant, minimal retransmission overhead regardless of window size.
  > 2. Go-Back-N's overhead depends on whether loss events fall into separate window bursts or consolidate within a single in-flight window.
  > 3. Expanding the window size from 3 to 5 reduces overall completion time by over 30% in both protocols due to pipelining."

---

#### [12:00 – 13:30] Slide 13: Solved University Examination Problem
- **What to Show on Screen:** Slide 13 (Solved University Examination Numerical).
- **Spoken Narration:**
  > "To connect our experimental work directly with our ITUC201 syllabus, Slide 13 presents a fully solved university examination numerical.
  > Given a 100 km link at 10 Mbps with frame size 1000 bytes, we compute:
  > Transmission delay Tt is 0.8 milliseconds; propagation delay Tp is 0.5 milliseconds.
  > The link parameter 'a' is 0.625.
  > Stop-and-Wait efficiency is only 44.44%, yielding an effective throughput of just 4.44 Mbps.
  > To reach 100% channel utilization, the optimal window size W_opt is 1 plus 2a, which gives 2.25, rounded up to 3 frames.
  > Finally, for sequence number bits:
  > For Go-Back-N, 2 to the m minus 1 must be at least 3, requiring at least m = 2 bits.
  > For Selective Repeat, 2 times Ws must be at least 6, requiring at least m = 3 bits. This perfectly aligns with our protocol rules."

---

#### [13:30 – 14:30] Slide 14: Conclusion & Closing
- **What to Show on Screen:** Slide 14 (Conclusion, References & Execution Guide).
- **Spoken Narration:**
  > "In conclusion, this project successfully built, validated, and demonstrated an event-driven ARQ simulator. We answered our core research question by demonstrating that Selective Repeat provides superior channel efficiency through receiver buffering, while Go-Back-N trades bandwidth efficiency for receiver simplicity.
  >
  > All project files—including `arq_simulator.py`, the interactive dashboard `app.py`, the technical report, PowerPoint deck, results CSV, and event logs—are fully reproducible and organized in the submission package.
  >
  > Thank you for your time and evaluation. I am now open to any viva questions or demonstration requests."
