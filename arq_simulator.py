#!/usr/bin/env python3
"""
========================================================================================
Project: NetVista 3D — Go-Back-N and Selective Repeat ARQ Simulator
Course:  ITUC201 — Fundamentals of Computer Networks (B.Tech Semester 3) 
Student: 25CS024
Topic:   Go-Back-N and Selective Repeat ARQ under Frame Losses
========================================================================================

Description:
    This module implements a discrete-event network simulator for two classic Sliding
    Window Automatic Repeat reQuest (ARQ) protocols:
        1. Go-Back-N (GBN) ARQ
        2. Selective Repeat (SR) ARQ

    The simulator uses a priority queue (Python's heapq) to process discrete network
    events in strict chronological order. It models:
        - Sender and receiver state machines
        - Transmission delay and propagation delay
        - Cumulative ACKs (GBN) and Individual/Selective ACKs (SR)
        - Oldest-unacknowledged frame timer (GBN) and per-frame timers (SR)
        - Receiver out-of-order buffering (SR) vs discarding (GBN)
        - Deterministic first-attempt frame loss injection (Frames 4 and 7)
        - Sender window movement and in-order application layer delivery

Execution:
    Run the command:
        python arq_simulator.py
========================================================================================
"""

import os
import sys
import csv
import heapq
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
import matplotlib
matplotlib.use('Agg')  # Headless backend for reliable server/CLI plotting
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ======================================================================================
# 1. SIMULATION EVENT DATA STRUCTURE
# ======================================================================================

@dataclass(order=True)
class SimulationEvent:
    """Represents a discrete event in the simulation priority queue."""
    time: float
    event_id: int
    event_type: str = field(compare=False)
    frame_id: Optional[int] = field(compare=False, default=None)
    data: dict = field(compare=False, default_factory=dict)


# ======================================================================================
# 2. CORE ARQ SIMULATOR CLASS
# ======================================================================================

class ARQSimulator:
    """
    Event-driven simulator for Go-Back-N and Selective Repeat ARQ protocols.
    
    Simulation Assumptions & Timing Units:
        - All completion steps and intervals are defined in simulated time units (TU).
        - Frame transmission delay (TX_TIME) = 1.0 TU (time to push frame onto wire).
        - Channel propagation delay (PROP_DELAY) = 1.5 TU (one-way transit time).
        - ACK transmission delay (ACK_TX_TIME) = 0.2 TU.
        - ACK propagation delay (ACK_PROP_DELAY) = 1.5 TU.
        - Round Trip Time (RTT) ~ 1.0 + 1.5 + 0.2 + 1.5 = 4.2 TU.
        - Retransmission Timeout (TIMEOUT) = 6.0 TU (sufficiently greater than RTT).
    """

    def __init__(
        self,
        protocol: str = "GBN",
        window_size: int = 3,
        total_frames: int = 10,
        loss_frames: Optional[Set[int]] = None,
        tx_time: float = 1.0,
        prop_delay: float = 1.5,
        ack_tx_time: float = 0.2,
        ack_prop_delay: float = 1.5,
        timeout: float = 6.0
    ):
        protocol = protocol.upper()
        if protocol not in ("GBN", "SR"):
            raise ValueError(f"Unsupported protocol: {protocol}. Choose 'GBN' or 'SR'.")
        
        self.protocol = protocol
        self.window_size = window_size
        self.total_frames = total_frames
        self.loss_frames = set(loss_frames) if loss_frames is not None else {4, 7}
        
        # Timing parameters (in simulated time units)
        self.TX_TIME = tx_time
        self.PROP_DELAY = prop_delay
        self.ACK_TX_TIME = ack_tx_time
        self.ACK_PROP_DELAY = ack_prop_delay
        self.TIMEOUT = timeout
        
        # Priority Queue and Event Counter
        self.event_queue: List[SimulationEvent] = []
        self.event_counter = 0
        self.current_time = 0.0
        
        # Sender State
        self.send_base = 0
        self.next_seq_num = 0
        self.sender_next_tx_time = 0.0
        self.tx_attempts: Dict[int, int] = {i: 0 for i in range(total_frames)}
        
        # Receiver State
        self.rcv_base = 0
        self.delivered_frames: List[int] = []
        self.receiver_buffer: Dict[int, bool] = {}  # For SR out-of-order buffering
        
        # Timers
        # GBN: Single timer for the oldest unacknowledged frame (send_base)
        self.gbn_timer_active = False
        self.gbn_timer_expiry = 0.0
        self.gbn_timer_seq = 0  # Monotonically increasing sequence to invalidate stale timer events
        
        # SR: Per-frame timers
        self.sr_timer_active: Dict[int, bool] = {i: False for i in range(total_frames)}
        self.sr_timer_expiry: Dict[int, float] = {i: 0.0 for i in range(total_frames)}
        self.sr_timer_seq: Dict[int, int] = {i: 0 for i in range(total_frames)}
        self.sr_sender_acked: Dict[int, bool] = {i: False for i in range(total_frames)}
        
        # Metrics and Logging
        self.original_tx_count = 0
        self.retrans_count = 0
        self.ack_count = 0
        self.timeout_count = 0
        self.events_processed = 0
        self.log_entries: List[Dict] = []
        self.snapshots: List[Dict] = []
        
        # Detailed transmission history for visual ladder diagram
        # Each record: dict(type, frame_id, start_time, end_time, status, attempt)
        self.tx_records: List[Dict] = []
        self.ack_records: List[Dict] = []
        self.timeout_records: List[Dict] = []

    def _schedule_event(self, time: float, event_type: str, frame_id: Optional[int] = None, data: dict = None):
        """Pushes an event into the priority queue."""
        self.event_counter += 1
        heapq.heappush(
            self.event_queue,
            SimulationEvent(time, self.event_counter, event_type, frame_id, data or {})
        )

    def _log(self, time: float, event_type: str, frame_id: Optional[int], ack_id: Optional[int], description: str):
        """Appends a structured event entry to the simulation log and records an animation snapshot."""
        self.log_entries.append({
            "timestamp": round(time, 2),
            "protocol": self.protocol,
            "window_size": self.window_size,
            "event_type": event_type,
            "frame_id": frame_id if frame_id is not None else "",
            "ack_id": ack_id if ack_id is not None else "",
            "description": description
        })
        self._record_snapshot(time, event_type, frame_id, ack_id, description)

    def _record_snapshot(self, time: float, event_type: str, frame_id: Optional[int], ack_id: Optional[int], description: str):
        """Captures a complete state snapshot for the live animation dashboard."""
        frame_states = {}
        for i in range(self.total_frames):
            if i in self.delivered_frames:
                frame_states[i] = "DELIVERED"
            elif i in self.receiver_buffer:
                frame_states[i] = "BUFFERED"
            elif i == frame_id and event_type in ("FRAME_TX_LOST", "FRAME_RETRANS_LOST"):
                frame_states[i] = "LOST"
            elif self.tx_attempts.get(i, 0) > 1:
                frame_states[i] = "RETRANSMITTED"
            elif self.tx_attempts.get(i, 0) == 1:
                frame_states[i] = "IN_FLIGHT"
            else:
                frame_states[i] = "WAITING"

        active_packet = None
        if "FRAME_TX" in event_type or "FRAME_RETRANS" in event_type:
            status = "LOST" if "LOST" in event_type else ("RETRANS" if "RETRANS" in event_type else "NORMAL")
            active_packet = {
                "type": "DATA",
                "direction": "FORWARD",
                "id": frame_id,
                "label": f"Frame {frame_id}",
                "status": status
            }
        elif "ACK_TX" in event_type:
            status = "DUPLICATE" if "DUP" in event_type or "PREV" in event_type else "NORMAL"
            active_packet = {
                "type": "ACK",
                "direction": "BACKWARD",
                "id": ack_id,
                "label": f"ACK {ack_id}",
                "status": status
            }
        elif "TIMEOUT" in event_type:
            active_packet = {
                "type": "TIMEOUT",
                "direction": "NONE",
                "id": frame_id,
                "label": f"TIMEOUT F{frame_id}",
                "status": "TIMEOUT"
            }

        loss_alert = None
        if event_type in ("FRAME_TX_LOST", "FRAME_RETRANS_LOST"):
            if frame_id == 4:
                loss_alert = "FRAME 4 LOST"
            elif frame_id == 7:
                loss_alert = "FRAME 7 LOST"
            else:
                loss_alert = f"FRAME {frame_id} LOST"

        self.snapshots.append({
            "step": len(self.snapshots),
            "time": round(time, 2),
            "event_type": event_type,
            "frame_id": frame_id if frame_id is not None else "",
            "ack_id": ack_id if ack_id is not None else "",
            "description": description,
            "protocol": self.protocol,
            "window_size": self.window_size,
            "total_frames": self.total_frames,
            "send_base": self.send_base,
            "next_seq_num": self.next_seq_num,
            "rcv_base": self.rcv_base,
            "rcv_window_size": 1 if self.protocol == "GBN" else self.window_size,
            "delivered_frames": list(self.delivered_frames),
            "buffered_frames": sorted(list(self.receiver_buffer.keys())),
            "frame_states": frame_states,
            "loss_alert": loss_alert,
            "active_packet": active_packet,
            "stats": {
                "original_tx": self.original_tx_count,
                "retransmissions": self.retrans_count,
                "total_tx": self.original_tx_count + self.retrans_count,
                "ack_count": self.ack_count,
                "timeout_count": self.timeout_count,
                "frames_received": len(self.delivered_frames) + len(self.receiver_buffer),
                "frames_delivered": len(self.delivered_frames),
                "completion_time": round(time, 2)
            }
        })

    def _try_send_new_frames(self):
        """Sends new frames as long as the sender sliding window has available capacity."""
        while self.next_seq_num < self.total_frames and (self.next_seq_num - self.send_base) < self.window_size:
            f_id = self.next_seq_num
            tx_start = max(self.current_time, self.sender_next_tx_time)
            self.sender_next_tx_time = tx_start + self.TX_TIME
            self.original_tx_count += 1
            self.tx_attempts[f_id] += 1
            attempt = self.tx_attempts[f_id]
            
            # Timer management
            if self.protocol == "GBN":
                if not self.gbn_timer_active:
                    self.gbn_timer_active = True
                    self.gbn_timer_seq += 1
                    self.gbn_timer_expiry = tx_start + self.TIMEOUT
                    self._schedule_event(self.gbn_timer_expiry, "TIMEOUT_GBN", None, {"timer_seq": self.gbn_timer_seq})
            elif self.protocol == "SR":
                self.sr_timer_active[f_id] = True
                self.sr_timer_seq[f_id] += 1
                self.sr_timer_expiry[f_id] = tx_start + self.TIMEOUT
                self._schedule_event(self.sr_timer_expiry[f_id], "TIMEOUT_SR", f_id, {"timer_seq": self.sr_timer_seq[f_id]})
            
            # Deterministic loss check: Lost on first transmission attempt only
            is_lost = (f_id in self.loss_frames and attempt == 1)
            tx_end = tx_start + self.TX_TIME + self.PROP_DELAY
            
            if is_lost:
                self._log(tx_start, "FRAME_TX_LOST", f_id, None,
                          f"Sender transmitted Frame {f_id} (Attempt {attempt}, Original) -> DROPPED by channel (deterministic loss)")
                self.tx_records.append({
                    "frame_id": f_id,
                    "start_time": tx_start,
                    "end_time": tx_start + self.TX_TIME + (self.PROP_DELAY * 0.5), # Dropped halfway
                    "status": "LOST",
                    "attempt": attempt,
                    "is_retrans": False
                })
            else:
                self._log(tx_start, "FRAME_TX", f_id, None,
                          f"Sender transmitted Frame {f_id} (Attempt {attempt}, Original)")
                self.tx_records.append({
                    "frame_id": f_id,
                    "start_time": tx_start,
                    "end_time": tx_end,
                    "status": "DELIVERED",
                    "attempt": attempt,
                    "is_retrans": False
                })
                self._schedule_event(tx_end, "FRAME_ARRIVAL", f_id, {"attempt": attempt})
                
            self.next_seq_num += 1

    def run(self) -> Dict:
        """
        Executes the discrete-event simulation until all frames are delivered and acknowledged.
        Returns a dictionary of performance metrics and execution results.
        """
        # Initial transmission burst up to window capacity
        self._try_send_new_frames()
        
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            self.events_processed += 1
            
            # Early termination check: all frames delivered and sender window fully acknowledged
            if len(self.delivered_frames) == self.total_frames and self.send_base == self.total_frames:
                break
                
            # -------------------------------------------------------------------------
            # EVENT: FRAME ARRIVAL AT RECEIVER
            # -------------------------------------------------------------------------
            if event.event_type == "FRAME_ARRIVAL":
                f_id = event.frame_id
                attempt = event.data["attempt"]
                
                if self.protocol == "GBN":
                    if f_id == self.rcv_base:
                        # In-order frame received
                        self.delivered_frames.append(f_id)
                        self.rcv_base += 1
                        self._log(self.current_time, "FRAME_RCV_IN_ORDER", f_id, None,
                                  f"Receiver accepted in-order Frame {f_id}. Delivered to application. Next expected: {self.rcv_base}")
                        # Send cumulative ACK
                        self.ack_count += 1
                        ack_start = self.current_time
                        ack_end = ack_start + self.ACK_TX_TIME + self.ACK_PROP_DELAY
                        self._schedule_event(ack_end, "ACK_ARRIVAL", None, {"ack_id": f_id})
                        self._log(ack_start, "ACK_TX_CUMULATIVE", None, f_id,
                                  f"Receiver sent cumulative ACK {f_id}")
                        self.ack_records.append({
                            "ack_id": f_id,
                            "start_time": ack_start,
                            "end_time": ack_end,
                            "is_dup": False
                        })
                    else:
                        # Out-of-order frame: GBN receiver discards and re-sends duplicate ACK
                        self._log(self.current_time, "FRAME_DISCARDED", f_id, None,
                                  f"Receiver received out-of-order Frame {f_id}. Discarded! Still expecting Frame {self.rcv_base}")
                        if self.rcv_base > 0:
                            # Re-send ACK for highest in-order frame
                            last_ack = self.rcv_base - 1
                            self.ack_count += 1
                            ack_start = self.current_time
                            ack_end = ack_start + self.ACK_TX_TIME + self.ACK_PROP_DELAY
                            self._schedule_event(ack_end, "ACK_ARRIVAL", None, {"ack_id": last_ack})
                            self._log(ack_start, "ACK_TX_DUPLICATE", None, last_ack,
                                      f"Receiver re-sent duplicate cumulative ACK {last_ack}")
                            self.ack_records.append({
                                "ack_id": last_ack,
                                "start_time": ack_start,
                                "end_time": ack_end,
                                "is_dup": True
                            })
                            
                elif self.protocol == "SR":
                    # Selective Repeat Receiver Window: [rcv_base, rcv_base + window_size - 1]
                    if self.rcv_base <= f_id < self.rcv_base + self.window_size:
                        self.receiver_buffer[f_id] = True
                        self._log(self.current_time, "FRAME_RCV_BUFFERED", f_id, None,
                                  f"Receiver accepted Frame {f_id} within window [{self.rcv_base}..{self.rcv_base + self.window_size - 1}]. Buffered.")
                        
                        # Send individual selective ACK
                        self.ack_count += 1
                        ack_start = self.current_time
                        ack_end = ack_start + self.ACK_TX_TIME + self.ACK_PROP_DELAY
                        self._schedule_event(ack_end, "ACK_ARRIVAL", None, {"ack_id": f_id})
                        self._log(ack_start, "ACK_TX_INDIVIDUAL", None, f_id,
                                  f"Receiver sent individual ACK {f_id}")
                        self.ack_records.append({
                            "ack_id": f_id,
                            "start_time": ack_start,
                            "end_time": ack_end,
                            "is_dup": False
                        })
                        
                        # Check if rcv_base can slide forward
                        while self.rcv_base in self.receiver_buffer:
                            deliv_f = self.rcv_base
                            self.delivered_frames.append(deliv_f)
                            self._log(self.current_time, "APP_DELIVERY", deliv_f, None,
                                      f"Receiver delivered in-order Frame {deliv_f} from buffer to application.")
                            self.rcv_base += 1
                            
                    elif self.rcv_base - self.window_size <= f_id < self.rcv_base:
                        # Already delivered frame (duplicate arrival due to delayed/lost earlier ACK)
                        self.ack_count += 1
                        ack_start = self.current_time
                        ack_end = ack_start + self.ACK_TX_TIME + self.ACK_PROP_DELAY
                        self._schedule_event(ack_end, "ACK_ARRIVAL", None, {"ack_id": f_id})
                        self._log(ack_start, "ACK_TX_PREVIOUS", None, f_id,
                                  f"Receiver re-acknowledged previously delivered Frame {f_id}")
                        self.ack_records.append({
                            "ack_id": f_id,
                            "start_time": ack_start,
                            "end_time": ack_end,
                            "is_dup": True
                        })
                    else:
                        self._log(self.current_time, "FRAME_OUT_OF_WINDOW", f_id, None,
                                  f"Receiver ignored Frame {f_id} outside window [{self.rcv_base}..{self.rcv_base + self.window_size - 1}]")

            # -------------------------------------------------------------------------
            # EVENT: ACK ARRIVAL AT SENDER
            # -------------------------------------------------------------------------
            elif event.event_type == "ACK_ARRIVAL":
                ack_id = event.data["ack_id"]
                
                if self.protocol == "GBN":
                    if ack_id >= self.send_base:
                        # Cumulative ACK confirms all frames <= ack_id
                        old_base = self.send_base
                        self.send_base = ack_id + 1
                        self._log(self.current_time, "ACK_RCV_CUMULATIVE", None, ack_id,
                                  f"Sender received cumulative ACK {ack_id}. Window base advanced from {old_base} to {self.send_base}")
                        
                        if self.send_base == self.next_seq_num:
                            # All outstanding transmitted frames have been acknowledged
                            self.gbn_timer_active = False
                        else:
                            # Outstanding frames remain; restart timer for oldest unacknowledged frame
                            self.gbn_timer_active = True
                            self.gbn_timer_seq += 1
                            self.gbn_timer_expiry = self.current_time + self.TIMEOUT
                            self._schedule_event(self.gbn_timer_expiry, "TIMEOUT_GBN", None, {"timer_seq": self.gbn_timer_seq})
                        
                        self._try_send_new_frames()
                    else:
                        self._log(self.current_time, "ACK_RCV_DUPLICATE", None, ack_id,
                                  f"Sender received duplicate cumulative ACK {ack_id}. Ignored.")
                        
                elif self.protocol == "SR":
                    if ack_id >= self.send_base and not self.sr_sender_acked[ack_id]:
                        self.sr_sender_acked[ack_id] = True
                        self.sr_timer_active[ack_id] = False  # Cancel timer for acknowledged frame
                        self._log(self.current_time, "ACK_RCV_INDIVIDUAL", None, ack_id,
                                  f"Sender received individual ACK {ack_id}. Frame {ack_id} marked acknowledged.")
                        
                        # Advance send_base past all contiguous acknowledged frames
                        old_base = self.send_base
                        while self.send_base < self.total_frames and self.sr_sender_acked[self.send_base]:
                            self.send_base += 1
                            
                        if self.send_base > old_base:
                            self._log(self.current_time, "WINDOW_SLIDE", None, None,
                                      f"Sender window base advanced from {old_base} to {self.send_base}")
                        
                        self._try_send_new_frames()
                    else:
                        self._log(self.current_time, "ACK_RCV_DUPLICATE", None, ack_id,
                                  f"Sender received already acknowledged ACK {ack_id}. Ignored.")

            # -------------------------------------------------------------------------
            # EVENT: TIMEOUT (GBN)
            # -------------------------------------------------------------------------
            elif event.event_type == "TIMEOUT_GBN":
                # Validate timer sequence to prevent processing obsolete timer events
                if self.gbn_timer_active and event.data.get("timer_seq") == self.gbn_timer_seq and self.send_base < self.total_frames:
                    self.timeout_count += 1
                    self.timeout_records.append({
                        "time": self.current_time,
                        "frame_id": self.send_base,
                        "protocol": "GBN"
                    })
                    self._log(self.current_time, "TIMEOUT_EXPIRED", self.send_base, None,
                              f"TIMEOUT! Oldest unacknowledged Frame {self.send_base} expired. Retransmitting entire window [{self.send_base}..{self.next_seq_num - 1}]")
                    
                    # Restart timer for the window base
                    self.gbn_timer_seq += 1
                    self.gbn_timer_expiry = self.current_time + self.TIMEOUT
                    self._schedule_event(self.gbn_timer_expiry, "TIMEOUT_GBN", None, {"timer_seq": self.gbn_timer_seq})
                    
                    # Go-Back-N: Retransmit ALL outstanding frames in window
                    for f_id in range(self.send_base, self.next_seq_num):
                        self.retrans_count += 1
                        self.tx_attempts[f_id] += 1
                        attempt = self.tx_attempts[f_id]
                        tx_start = max(self.current_time, self.sender_next_tx_time)
                        self.sender_next_tx_time = tx_start + self.TX_TIME
                        tx_end = tx_start + self.TX_TIME + self.PROP_DELAY
                        
                        # Retransmission deterministic loss check (Attempt > 1 succeeds)
                        is_lost = (f_id in self.loss_frames and attempt == 1)
                        if is_lost:
                            self._log(tx_start, "FRAME_RETRANS_LOST", f_id, None,
                                      f"Sender retransmitted Frame {f_id} (Attempt {attempt}) -> DROPPED (loss)")
                            self.tx_records.append({
                                "frame_id": f_id,
                                "start_time": tx_start,
                                "end_time": tx_start + self.TX_TIME + (self.PROP_DELAY * 0.5),
                                "status": "LOST",
                                "attempt": attempt,
                                "is_retrans": True
                            })
                        else:
                            self._log(tx_start, "FRAME_RETRANS", f_id, None,
                                      f"Sender retransmitted Frame {f_id} (Attempt {attempt}, Retransmission)")
                            self.tx_records.append({
                                "frame_id": f_id,
                                "start_time": tx_start,
                                "end_time": tx_end,
                                "status": "DELIVERED",
                                "attempt": attempt,
                                "is_retrans": True
                            })
                            self._schedule_event(tx_end, "FRAME_ARRIVAL", f_id, {"attempt": attempt})

            # -------------------------------------------------------------------------
            # EVENT: TIMEOUT (SR)
            # -------------------------------------------------------------------------
            elif event.event_type == "TIMEOUT_SR":
                f_id = event.frame_id
                if self.sr_timer_active[f_id] and event.data.get("timer_seq") == self.sr_timer_seq[f_id] and not self.sr_sender_acked[f_id]:
                    self.timeout_count += 1
                    self.retrans_count += 1
                    self.tx_attempts[f_id] += 1
                    attempt = self.tx_attempts[f_id]
                    
                    self.timeout_records.append({
                        "time": self.current_time,
                        "frame_id": f_id,
                        "protocol": "SR"
                    })
                    self._log(self.current_time, "TIMEOUT_EXPIRED", f_id, None,
                              f"TIMEOUT! Frame {f_id} expired. Retransmitting ONLY Frame {f_id} (Attempt {attempt})")
                    
                    # Restart individual timer for this specific frame
                    self.sr_timer_seq[f_id] += 1
                    self.sr_timer_expiry[f_id] = self.current_time + self.TIMEOUT
                    self._schedule_event(self.sr_timer_expiry[f_id], "TIMEOUT_SR", f_id, {"timer_seq": self.sr_timer_seq[f_id]})
                    
                    tx_start = max(self.current_time, self.sender_next_tx_time)
                    self.sender_next_tx_time = tx_start + self.TX_TIME
                    tx_end = tx_start + self.TX_TIME + self.PROP_DELAY
                    
                    is_lost = (f_id in self.loss_frames and attempt == 1)
                    if is_lost:
                        self._log(tx_start, "FRAME_RETRANS_LOST", f_id, None,
                                  f"Sender retransmitted Frame {f_id} (Attempt {attempt}) -> DROPPED (loss)")
                        self.tx_records.append({
                            "frame_id": f_id,
                            "start_time": tx_start,
                            "end_time": tx_start + self.TX_TIME + (self.PROP_DELAY * 0.5),
                            "status": "LOST",
                            "attempt": attempt,
                            "is_retrans": True
                        })
                    else:
                        self._log(tx_start, "FRAME_RETRANS", f_id, None,
                                  f"Sender retransmitted Frame {f_id} (Attempt {attempt}, Selective Retransmission)")
                        self.tx_records.append({
                            "frame_id": f_id,
                            "start_time": tx_start,
                            "end_time": tx_end,
                            "status": "DELIVERED",
                            "attempt": attempt,
                            "is_retrans": True
                        })
                        self._schedule_event(tx_end, "FRAME_ARRIVAL", f_id, {"attempt": attempt})

        # Correctness Verification
        expected_sequence = list(range(self.total_frames))
        is_ordered_and_complete = (self.delivered_frames == expected_sequence)
        
        return {
            "experiment_id": f"{self.protocol}_W{self.window_size}",
            "protocol": self.protocol,
            "window_size": self.window_size,
            "total_frames": self.total_frames,
            "loss_frames": sorted(list(self.loss_frames)),
            "original_tx": self.original_tx_count,
            "retransmissions": self.retrans_count,
            "total_tx": self.original_tx_count + self.retrans_count,
            "ack_count": self.ack_count,
            "timeout_count": self.timeout_count,
            "events_processed": self.events_processed,
            "completion_time": round(self.current_time, 2),
            "delivered_in_order": is_ordered_and_complete,
            "delivered_count": len(self.delivered_frames)
        }


# ======================================================================================
# 3. TIMELINE VISUALISATION GENERATOR (SPACE-TIME LADDER DIAGRAM)
# ======================================================================================

def generate_timeline_diagram(sim: ARQSimulator, output_path: str):
    """
    Renders an academic-grade space-time ladder diagram of sender-receiver interactions.
    Visualises original transmissions, lost frames, ACKs, timeouts, and retransmissions.
    """
    max_time = sim.current_time + 2.0
    fig, ax = plt.subplots(figsize=(11, 14), dpi=150)
    
    # Draw Sender and Receiver timelines
    sender_x = 0.2
    receiver_x = 0.8
    
    ax.plot([sender_x, sender_x], [0, max_time], color='#1f77b4', linewidth=3, label='Sender')
    ax.plot([receiver_x, receiver_x], [0, max_time], color='#2ca02c', linewidth=3, label='Receiver')
    
    # Invert Y-axis so time increases downwards (standard protocol ladder format)
    ax.set_ylim(max_time, -1.0)
    ax.set_xlim(0.0, 1.0)
    
    # Annotate Nodes at top
    ax.text(sender_x, -1.5, "SENDER\n(Host A)", fontsize=13, weight='bold', color='#1f77b4', ha='center', va='bottom')
    ax.text(receiver_x, -1.5, "RECEIVER\n(Host B)", fontsize=13, weight='bold', color='#2ca02c', ha='center', va='bottom')
    
    # Draw time grid lines
    for t in range(0, int(max_time) + 2, 2):
        ax.axhline(y=t, color='#e0e0e0', linestyle='--', linewidth=0.7, zorder=0)
        ax.text(0.05, t, f"t={t}", fontsize=8, color='#666666', va='center')
        
    # Plot Data Frame Transmissions
    for rec in sim.tx_records:
        f_id = rec["frame_id"]
        t_start = rec["start_time"]
        t_end = rec["end_time"]
        status = rec["status"]
        attempt = rec["attempt"]
        is_retrans = rec["is_retrans"]
        
        if status == "LOST":
            # Truncated arrow with a bold Red X indicating loss
            mid_x = (sender_x + receiver_x) / 2.0
            ax.annotate(
                '',
                xy=(mid_x, t_end),
                xytext=(sender_x, t_start),
                arrowprops=dict(arrowstyle="->", color='#d62728', lw=1.8, linestyle=':')
            )
            ax.plot(mid_x, t_end, 'x', color='#d62728', markersize=11, markeredgewidth=2.5)
            ax.text(
                mid_x + 0.02, t_end,
                f"Frame {f_id} [LOST]",
                color='#d62728', fontsize=8, weight='bold', va='center'
            )
        else:
            # Delivered Frame
            color = '#9467bd' if is_retrans else '#1f77b4'
            ax.annotate(
                '',
                xy=(receiver_x, t_end),
                xytext=(sender_x, t_start),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.6)
            )
            lbl = f"Retrans F{f_id}" if is_retrans else f"Frame {f_id}"
            ax.text(
                sender_x - 0.02, t_start,
                f"Tx F{f_id}",
                color=color, fontsize=8, ha='right', va='center'
            )
            ax.text(
                (sender_x + receiver_x) * 0.45, (t_start + t_end) * 0.5,
                lbl,
                color=color, fontsize=7.5, rotation=-14, ha='center', va='bottom'
            )

    # Plot ACKs
    for rec in sim.ack_records:
        ack_id = rec["ack_id"]
        t_start = rec["start_time"]
        t_end = rec["end_time"]
        is_dup = rec["is_dup"]
        
        color = '#ff7f0e' if is_dup else '#2ca02c'
        ax.annotate(
            '',
            xy=(sender_x, t_end),
            xytext=(receiver_x, t_start),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.4, linestyle='--' if is_dup else '-')
        )
        label = f"DupACK {ack_id}" if is_dup else f"ACK {ack_id}"
        ax.text(
            receiver_x + 0.02, t_start,
            label,
            color=color, fontsize=8, ha='left', va='center'
        )

    # Plot Timeouts
    for rec in sim.timeout_records:
        t_out = rec["time"]
        f_id = rec["frame_id"]
        ax.plot(sender_x, t_out, 'o', color='#d62728', markersize=8)
        ax.text(
            sender_x - 0.03, t_out,
            f"TIMEOUT (F{f_id})",
            color='#d62728', fontsize=8, weight='bold', ha='right', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffcccc', edgecolor='#d62728', alpha=0.8)
        )

    # Title and Legend
    proto_title = "Go-Back-N (GBN)" if sim.protocol == "GBN" else "Selective Repeat (SR)"
    plt.title(
        f"Space-Time Ladder Diagram: {proto_title} | Window Size W = {sim.window_size}\n"
        f"Deterministic Losses at Frames 4 & 7 | Completion Time: {sim.current_time:.1f} TU",
        fontsize=12, weight='bold', pad=25
    )
    
    ax.axis('off')
    
    # Custom Legend
    legend_elements = [
        plt.Line2D([0], [0], color='#1f77b4', lw=2, label='Original Data Frame'),
        plt.Line2D([0], [0], color='#9467bd', lw=2, label='Retransmitted Frame'),
        plt.Line2D([0], [0], color='#d62728', lw=2, linestyle=':', label='Lost Frame (Drop)'),
        plt.Line2D([0], [0], color='#2ca02c', lw=2, label='Normal ACK'),
        plt.Line2D([0], [0], color='#ff7f0e', lw=2, linestyle='--', label='Duplicate ACK'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#d62728', markersize=8, label='Timeout Event')
    ]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.01), ncol=3, frameon=True, fontsize=8.5)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


# ======================================================================================
# 4. STATISTICAL COMPARISON CHARTS GENERATOR
# ======================================================================================

def generate_comparison_charts(results: List[Dict], output_dir: str):
    """Generates publication-quality comparative charts from simulation results."""
    os.makedirs(output_dir, exist_ok=True)
    labels = [f"{r['protocol']}\nW={r['window_size']}" for r in results]
    colors = ['#3498db', '#2980b9', '#2ecc71', '#27ae60']
    
    # ----------------------------------------------------------------------------------
    # Chart 1: Retransmissions Comparison
    # ----------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    retrans_vals = [r['retransmissions'] for r in results]
    bars = ax.bar(labels, retrans_vals, color=colors, width=0.55, edgecolor='#333333', linewidth=1.2)
    ax.set_ylabel("Retransmission Count (Data Frames)", fontsize=11, weight='bold')
    ax.set_title("Retransmission Count across ARQ Configurations\n(Losses at Frames 4 & 7)", fontsize=12, weight='bold', pad=12)
    ax.set_ylim(0, max(retrans_vals) + 2)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparison_retransmissions.png"))
    plt.close()

    # ----------------------------------------------------------------------------------
    # Chart 2: Completion Time Comparison
    # ----------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    time_vals = [r['completion_time'] for r in results]
    bars = ax.bar(labels, time_vals, color=colors, width=0.55, edgecolor='#333333', linewidth=1.2)
    ax.set_ylabel("Simulated Completion Time (Time Units)", fontsize=11, weight='bold')
    ax.set_title("Total Completion Time across ARQ Configurations\n(Simulation Time Units)", fontsize=12, weight='bold', pad=12)
    ax.set_ylim(0, max(time_vals) + 5)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f} TU',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparison_completion_time.png"))
    plt.close()

    # ----------------------------------------------------------------------------------
    # Chart 3: Total Transmissions Comparison (Original + Retransmitted)
    # ----------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    orig_vals = [r['original_tx'] for r in results]
    retrans_vals = [r['retransmissions'] for r in results]
    
    p1 = ax.bar(labels, orig_vals, width=0.55, label='Original Transmissions (10)', color='#34495e', edgecolor='#2c3e50')
    p2 = ax.bar(labels, retrans_vals, width=0.55, bottom=orig_vals, label='Retransmissions', color='#e74c3c', edgecolor='#c0392b')
    
    ax.set_ylabel("Total Data Frames Sent onto Channel", fontsize=11, weight='bold')
    ax.set_title("Total Data-Frame Transmissions Breakdown\n(Original vs Retransmitted)", fontsize=12, weight='bold', pad=12)
    ax.set_ylim(0, max([o + r for o, r in zip(orig_vals, retrans_vals)]) + 4)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.legend(loc='upper right', frameon=True)
    
    for idx, (o, r) in enumerate(zip(orig_vals, retrans_vals)):
        total = o + r
        ax.annotate(f'Total: {total}\n({r} retrans)',
                    xy=(idx, total),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparison_total_transmissions.png"))
    plt.close()

    # ----------------------------------------------------------------------------------
    # Chart 4: Window Size Sensitivity (Research Question Focus)
    # ----------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    gbn_retrans = [r['retransmissions'] for r in results if r['protocol'] == 'GBN']
    sr_retrans = [r['retransmissions'] for r in results if r['protocol'] == 'SR']
    window_sizes = [3, 5]
    
    ax.plot(window_sizes, gbn_retrans, marker='s', markersize=9, color='#e74c3c', linewidth=2.5, label='Go-Back-N (GBN)')
    ax.plot(window_sizes, sr_retrans, marker='o', markersize=9, color='#27ae60', linewidth=2.5, label='Selective Repeat (SR)')
    
    ax.set_xlabel("Window Size (W)", fontsize=11, weight='bold')
    ax.set_ylabel("Retransmission Count", fontsize=11, weight='bold')
    ax.set_title("Research Finding: Retransmissions vs Window Size\n(Under Losses at Frames 4 & 7)", fontsize=12, weight='bold', pad=12)
    ax.set_xticks([3, 5])
    ax.set_ylim(0, max(gbn_retrans + sr_retrans) + 3)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='center right', frameon=True, fontsize=10)
    
    for x, y in zip(window_sizes, gbn_retrans):
        ax.annotate(f'GBN: {y}', xy=(x, y), xytext=(-15, 10), textcoords="offset points", weight='bold', color='#c0392b')
    for x, y in zip(window_sizes, sr_retrans):
        ax.annotate(f'SR: {y}', xy=(x, y), xytext=(-15, -18), textcoords="offset points", weight='bold', color='#1e824c')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "window_size_sensitivity.png"))
    plt.close()


# ======================================================================================
# 5. EXPERIMENT RUNNER & CLI INTERFACE
# ======================================================================================

def run_all_experiments():
    """
    Executes the four mandatory experiments:
        1. Go-Back-N, Window = 3
        2. Go-Back-N, Window = 5
        3. Selective Repeat, Window = 3
        4. Selective Repeat, Window = 5
    """
    print("=" * 86)
    print("  NETVISTA 3D — ARQ PROTOCOL SIMULATOR (GBN vs SR)")
    print("  Student ID: 25CS024 | Subject: ITUC201 Fundamentals of Computer Networks")
    print("  Deterministic Loss Injected at Data Frames: [4, 7]")
    print("=" * 86)
    
    # Base paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "event_logs")
    graphs_dir = os.path.join(script_dir, "graphs")
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(graphs_dir, exist_ok=True)
    
    configs = [
        ("GBN", 3),
        ("GBN", 5),
        ("SR", 3),
        ("SR", 5)
    ]
    
    results = []
    
    for proto, w in configs:
        print(f"\n[RUNNING EXPERIMENT] Protocol: {proto:<3} | Window Size: {w} | Frame Losses: [4, 7]")
        sim = ARQSimulator(protocol=proto, window_size=w, total_frames=10, loss_frames={4, 7})
        res = sim.run()
        results.append(res)
        
        # Save Event Log CSV
        log_filename = f"event_log_{proto}_W{w}.csv"
        log_filepath = os.path.join(logs_dir, log_filename)
        with open(log_filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "protocol", "window_size", "event_type", "frame_id", "ack_id", "description"])
            writer.writeheader()
            writer.writerows(sim.log_entries)
        print(f"  -> Event Log saved to: {os.path.relpath(log_filepath, script_dir)} ({len(sim.log_entries)} events)")
        
        # Generate Timeline Graphic
        timeline_filename = f"timeline_{proto}_W{w}.png"
        timeline_filepath = os.path.join(graphs_dir, timeline_filename)
        generate_timeline_diagram(sim, timeline_filepath)
        print(f"  -> Timeline Ladder Diagram saved to: {os.path.relpath(timeline_filepath, script_dir)}")
        
        # Print mini-summary
        status_str = "SUCCESS (All in-order)" if res["delivered_in_order"] else "FAILED"
        print(f"  -> Result: Retransmissions = {res['retransmissions']} | Completion Time = {res['completion_time']} TU | Status = {status_str}")

    # Save summary results.csv
    results_csv_path = os.path.join(script_dir, "results.csv")
    with open(results_csv_path, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = [
            "experiment_id", "protocol", "window_size", "total_frames",
            "original_tx", "retransmissions", "total_tx", "ack_count",
            "timeout_count", "events_processed", "completion_time",
            "delivered_in_order", "delivered_count"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = {k: r[k] for k in fieldnames}
            writer.writerow(row)
    print(f"\n[SUMMARY] Master results table saved to: {os.path.relpath(results_csv_path, script_dir)}")
    
    # Generate Comparison Charts
    generate_comparison_charts(results, graphs_dir)
    print(f"[PLOTS] Comparison charts generated successfully in: {os.path.relpath(graphs_dir, script_dir)}")

    # Print Final Comparison Table to Console
    print("\n" + "=" * 96)
    print("                      FINAL EXPERIMENTAL RESULTS & BENCHMARK TABLE")
    print("=" * 96)
    header = f"{'Protocol':<8} | {'Window':<6} | {'Orig Tx':<7} | {'Retrans':<7} | {'Total Tx':<8} | {'ACKs':<5} | {'Timeouts':<8} | {'Time (TU)':<9} | {'Delivered':<9}"
    print(header)
    print("-" * 96)
    for r in results:
        deliv_str = "10/10 [OK]" if r["delivered_in_order"] else "FAILED"
        print(f"{r['protocol']:<8} | {r['window_size']:<6} | {r['original_tx']:<7} | {r['retransmissions']:<7} | {r['total_tx']:<8} | {r['ack_count']:<5} | {r['timeout_count']:<8} | {r['completion_time']:<9.1f} | {deliv_str:<9}")
    print("=" * 96)
    
    print("\n[KEY RESEARCH FINDING SUMMARY]")
    print("  1. Selective Repeat (SR) achieved exactly 2 retransmissions in both W=3 and W=5,")
    print("     retransmitting solely the damaged frames (Frames 4 and 7) thanks to receiver buffering.")
    print("  2. Go-Back-N (GBN) retransmitted unacknowledged frames following timeout:")
    print("     - At W=3: Frame 4 timeout caused 3 retransmissions (4,5,6), Frame 7 timeout caused 3 (7,8,9) -> Total = 6.")
    print("     - At W=5: Both Frames 4 & 7 fell into the same in-flight window. A single timeout on Frame 4")
    print("       triggered retransmission of [4,5,6,7,8], simultaneously repairing Frame 7 without a second timeout -> Total = 5.")
    print("  3. Window size 5 reduced overall completion time across both protocols due to pipelining.")
    print("=" * 96)


if __name__ == "__main__":
    run_all_experiments()
