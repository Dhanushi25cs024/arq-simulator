#!/usr/bin/env python3
"""
========================================================================================
Test Suite: ARQ Protocol Logic & Experimental Verification
Course:     ITUC201 — Fundamentals of Computer Networks
Student ID: 25CS024
Topic:      Go-Back-N and Selective Repeat ARQ under Frame Losses
========================================================================================

This test script validates:
    1. Priority Queue & Event-Driven Engine determinism
    2. Go-Back-N (GBN) logic, cumulative ACKs, discard behavior, and window retransmissions
    3. Selective Repeat (SR) logic, selective ACKs, receiver buffering, and selective retransmissions
    4. Deterministic loss rules (Frames 4 & 7 dropped on Attempt 1 only; Attempt 2 succeeds)
    5. Exact metric verification for all four benchmark configurations:
        - GBN-3: Retransmissions = 6, Timeouts = 2
        - GBN-5: Retransmissions = 5, Timeouts = 1
        - SR-3:  Retransmissions = 2, Timeouts = 2
        - SR-5:  Retransmissions = 2, Timeouts = 2
    6. 100% In-Order Application Layer Delivery for all configurations
========================================================================================
"""

import sys
import unittest
from arq_simulator import ARQSimulator

class TestARQProtocols(unittest.TestCase):

    def test_gbn_window_3(self):
        """Test Go-Back-N with Window Size 3 under deterministic losses at 4 and 7."""
        sim = ARQSimulator(protocol="GBN", window_size=3, total_frames=10, loss_frames={4, 7})
        res = sim.run()
        
        self.assertEqual(res["protocol"], "GBN")
        self.assertEqual(res["window_size"], 3)
        self.assertEqual(res["original_tx"], 10)
        self.assertEqual(res["retransmissions"], 6, "GBN W=3 must produce exactly 6 retransmissions (3 for frame 4, 3 for frame 7)")
        self.assertEqual(res["total_tx"], 16)
        self.assertEqual(res["timeout_count"], 2, "GBN W=3 must have 2 distinct timeout events")
        self.assertTrue(res["delivered_in_order"], "All 10 frames must be delivered in strict ascending sequence")
        self.assertEqual(sim.delivered_frames, list(range(10)))

    def test_gbn_window_5(self):
        """Test Go-Back-N with Window Size 5 under deterministic losses at 4 and 7."""
        sim = ARQSimulator(protocol="GBN", window_size=5, total_frames=10, loss_frames={4, 7})
        res = sim.run()
        
        self.assertEqual(res["protocol"], "GBN")
        self.assertEqual(res["window_size"], 5)
        self.assertEqual(res["original_tx"], 10)
        self.assertEqual(res["retransmissions"], 5, "GBN W=5 must produce exactly 5 retransmissions (consolidated burst [4..8])")
        self.assertEqual(res["total_tx"], 15)
        self.assertEqual(res["timeout_count"], 1, "GBN W=5 must experience only 1 timeout (frame 7 repaired in same burst)")
        self.assertTrue(res["delivered_in_order"], "All 10 frames must be delivered in strict ascending sequence")
        self.assertEqual(sim.delivered_frames, list(range(10)))

    def test_sr_window_3(self):
        """Test Selective Repeat with Window Size 3 under deterministic losses at 4 and 7."""
        sim = ARQSimulator(protocol="SR", window_size=3, total_frames=10, loss_frames={4, 7})
        res = sim.run()
        
        self.assertEqual(res["protocol"], "SR")
        self.assertEqual(res["window_size"], 3)
        self.assertEqual(res["original_tx"], 10)
        self.assertEqual(res["retransmissions"], 2, "SR W=3 must produce exactly 2 retransmissions (solely frames 4 and 7)")
        self.assertEqual(res["total_tx"], 12)
        self.assertEqual(res["timeout_count"], 2)
        self.assertTrue(res["delivered_in_order"], "All 10 frames must be delivered in strict ascending sequence")
        self.assertEqual(sim.delivered_frames, list(range(10)))

    def test_sr_window_5(self):
        """Test Selective Repeat with Window Size 5 under deterministic losses at 4 and 7."""
        sim = ARQSimulator(protocol="SR", window_size=5, total_frames=10, loss_frames={4, 7})
        res = sim.run()
        
        self.assertEqual(res["protocol"], "SR")
        self.assertEqual(res["window_size"], 5)
        self.assertEqual(res["original_tx"], 10)
        self.assertEqual(res["retransmissions"], 2, "SR W=5 must produce exactly 2 retransmissions (invariant to window size)")
        self.assertEqual(res["total_tx"], 12)
        self.assertEqual(res["timeout_count"], 2)
        self.assertTrue(res["delivered_in_order"], "All 10 frames must be delivered in strict ascending sequence")
        self.assertEqual(sim.delivered_frames, list(range(10)))

    def test_deterministic_loss_attempts(self):
        """Verify that losses apply strictly to Attempt 1 and retransmissions succeed."""
        sim = ARQSimulator(protocol="SR", window_size=3, total_frames=10, loss_frames={4, 7})
        sim.run()
        
        # Verify attempt counts
        self.assertEqual(sim.tx_attempts[4], 2, "Frame 4 must have exactly 2 attempts (Attempt 1 lost, Attempt 2 delivered)")
        self.assertEqual(sim.tx_attempts[7], 2, "Frame 7 must have exactly 2 attempts (Attempt 1 lost, Attempt 2 delivered)")
        for i in (0, 1, 2, 3, 5, 6, 8, 9):
            self.assertEqual(sim.tx_attempts[i], 1, f"Frame {i} should only be transmitted once in SR")

    def test_sr_receiver_buffering(self):
        """Verify that SR receiver successfully buffers out-of-order packets."""
        sim = ARQSimulator(protocol="SR", window_size=3, total_frames=10, loss_frames={4, 7})
        sim.run()
        
        # Check logs for buffered events
        buffered_events = [e for e in sim.log_entries if e["event_type"] == "FRAME_RCV_BUFFERED"]
        self.assertTrue(len(buffered_events) > 0, "SR must trigger FRAME_RCV_BUFFERED events for out-of-order frames")
        
        # Frame 5 and Frame 6 must have been buffered while waiting for Frame 4
        buffered_frame_ids = [e["frame_id"] for e in buffered_events]
        self.assertIn(5, buffered_frame_ids)
        self.assertIn(6, buffered_frame_ids)

    def test_gbn_discard_behavior(self):
        """Verify that GBN receiver discards out-of-order packets and sends duplicate ACKs."""
        sim = ARQSimulator(protocol="GBN", window_size=3, total_frames=10, loss_frames={4, 7})
        sim.run()
        
        discarded_events = [e for e in sim.log_entries if e["event_type"] == "FRAME_DISCARDED"]
        self.assertTrue(len(discarded_events) > 0, "GBN must discard out-of-order frames")
        
        dup_ack_events = [e for e in sim.log_entries if e["event_type"] == "ACK_TX_DUPLICATE"]
        self.assertTrue(len(dup_ack_events) > 0, "GBN must send duplicate cumulative ACKs on out-of-order arrival")


if __name__ == "__main__":
    print("=" * 70)
    print("  RUNNING ARQ SIMULATOR PROTOCOL VERIFICATION TEST SUITE")
    print("=" * 70)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestARQProtocols)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n[PASSED] All ARQ protocol tests and verification assertions passed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILED] One or more tests failed.")
        sys.exit(1)
