#!/usr/bin/env python3
"""
========================================================================================
Project: ARQ LAB · 25CS024 — Go-Back-N vs Selective Repeat
Course:  ITUC201 — Fundamentals of Computer Networks (B.Tech Semester 3)
Student: 25CS024
Topic:   Go-Back-N and Selective Repeat ARQ under Losses
========================================================================================

Description:
    An exact high-fidelity reproduction of the "ARQ Lab · 25CS024" event-driven protocol
    observatory dashboard (matching https://arq-recovery-demo.preview.emergentagent.com/).

    Features:
        - 01 / Configuration: Protocol, Window Size, Total Frames, Loss Frames, Timing Model
        - Playback Controls: Start run, Run to completion, Defaults, Pause, Resume, Step forward, Reset
        - Playback Speed: 0.25x to 4x live animation slider
        - Live Network View: Frames in motion, Sender/Receiver endpoints, Data & ACK channels,
          Sender Window strip, Receiver Buffer strip, and prominent Frame 4/7 loss alerts
        - Metrics Dashboard: Retransmissions, Completion steps, Simulated time, In-order delivery
        - 02 / Event Stream: Replayable timeline with Event-Type filter & Frame Search
        - 03 / Protocol Lens: Dynamic protocol insights & architecture observation cards
        - 04 / Controlled Evaluation: Four-run benchmark matrix, comparison table & dual bar chart
        - Export Tools: One-click CSV and JSON exports

How to Run:
    streamlit run app.py
    (or: python app.py)
========================================================================================
"""

import os
import sys
import json
import subprocess

# Ensure ARQ_Project is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Check if running directly via python CLI rather than streamlit CLI
def is_running_under_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

if __name__ == "__main__" and not is_running_under_streamlit():
    print("[*] Launching ARQ Lab dashboard via Streamlit on http://localhost:8501 ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)])
    sys.exit(0)

import streamlit as st
import streamlit.components.v1 as components
from arq_simulator import ARQSimulator

# Configure Streamlit page shell
st.set_page_config(
    page_title="ARQ Lab · 25CS024",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit chrome for a full-bleed application feel
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu, footer { visibility: hidden !important; }
    .stApp {
        background-color: #030712 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)


def get_precomputed_experiments():
    """Runs the 4 official benchmark experiments with ARQSimulator and prepares JSON data."""
    configs = [
        {"protocol": "GBN", "window_size": 3, "label": "GBN N=3"},
        {"protocol": "GBN", "window_size": 5, "label": "GBN N=5"},
        {"protocol": "SR", "window_size": 3, "label": "SR N=3"},
        {"protocol": "SR", "window_size": 5, "label": "SR N=5"},
    ]
    results = []
    for cfg in configs:
        sim = ARQSimulator(
            protocol=cfg["protocol"],
            window_size=cfg["window_size"],
            total_frames=10,
            loss_frames={4, 7},
            tx_time=1.0,
            prop_delay=2.0,
            ack_tx_time=0.5,
            ack_prop_delay=1.0,
            timeout=8.0
        )
        res = sim.run()
        results.append({
            "label": cfg["label"],
            "protocol": cfg["protocol"],
            "window_size": cfg["window_size"],
            "retransmissions": res["retransmissions"],
            "completion_event_steps": res["events_processed"],
            "completion_simulated_time": res["completion_time"],
            "timeouts": res["timeout_count"],
            "buffered_out_of_order": len(res.get("receiver_buffer", {})) if cfg["protocol"] == "SR" else 0,
            "snapshots": sim.snapshots,
            "events": [
                {
                    "sequence": idx + 1,
                    "timestamp": entry["timestamp"],
                    "event_type": entry["event_type"],
                    "frame": entry["frame_id"] if entry["frame_id"] != "" else None,
                    "protocol": entry["protocol"],
                    "window_size": entry["window_size"],
                    "description": entry["description"],
                    "result": "OK" if "LOST" not in entry["event_type"] else "LOST",
                    "attempt": 1
                }
                for idx, entry in enumerate(sim.log_entries)
            ]
        })
    return results

benchmark_experiments = get_precomputed_experiments()
benchmark_json = json.dumps(benchmark_experiments)

# Embed complete standalone application matching reference web app
APP_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARQ Lab · 25CS024</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        *, ::after, ::before {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        :root {{
            --bg-base: #030712;
            --bg-card: rgba(17, 24, 39, 0.74);
            --bg-inset: rgba(15, 23, 42, 0.85);
            --border: rgba(148, 163, 184, 0.14);
            --border-hover: rgba(129, 140, 248, 0.36);
            --primary: #4f46e5;
            --primary-hover: #6366f1;
            --cyan: #38bdf8;
            --emerald: #10b981;
            --amber: #f59e0b;
            --rose: #ef4444;
            --purple: #a855f7;
            --indigo: #818cf8;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --font-sans: 'Geist', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
        }}
        body {{
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-sans);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
            padding-bottom: 40px;
        }}
        .mono {{
            font-family: var(--font-mono);
        }}
        .eyebrow {{
            font-size: 10px;
            font-family: var(--font-mono);
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-dim);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .app-shell {{
            width: 100%;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* TOPBAR */
        .topbar {{
            height: 64px;
            padding: 0 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            background: rgba(3, 7, 18, 0.85);
            backdrop-filter: blur(8px);
            position: sticky;
            top: 0;
            z-index: 50;
        }}
        .brand-block {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brand-mark {{
            width: 36px;
            height: 36px;
            border-radius: 9px;
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--cyan);
            display: grid;
            place-items: center;
        }}
        .brand-title {{
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #ffffff;
        }}
        .brand-title span {{
            color: var(--text-dim);
            font-weight: 400;
        }}
        .brand-subtitle {{
            font-size: 10px;
            color: var(--text-dim);
            font-weight: 400;
        }}
        .topbar-status {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 5px 12px;
            border-radius: 9999px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            font-size: 11px;
            color: var(--text-muted);
        }}
        .status-light {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--emerald);
            box-shadow: 0 0 8px var(--emerald);
        }}
        .status-light.running {{
            background: var(--cyan);
            box-shadow: 0 0 10px var(--cyan);
            animation: pulse 1.2s infinite;
        }}
        .status-light.completed {{
            background: var(--emerald);
            box-shadow: 0 0 8px var(--emerald);
        }}
        .status-divider {{
            color: var(--border);
            margin: 0 2px;
        }}

        /* DASHBOARD CONTAINER */
        .dashboard-container {{
            max-width: 1440px;
            width: 100%;
            margin: 0 auto;
            padding: 32px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}

        /* HERO ROW */
        .hero-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
        }}
        .hero-eyebrow {{
            color: var(--cyan);
            margin-bottom: 8px;
        }}
        .hero-pulse {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--cyan);
            box-shadow: 0 0 8px var(--cyan);
            display: inline-block;
        }}
        .hero-row h1 {{
            font-size: 32px;
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: -0.02em;
            color: #ffffff;
            margin-bottom: 8px;
        }}
        .hero-row h1 em {{
            font-style: italic;
            font-weight: 400;
            color: var(--indigo);
        }}
        .hero-row p {{
            font-size: 13px;
            color: var(--text-muted);
            max-width: 650px;
            line-height: 1.6;
        }}
        .hero-aside {{
            width: 320px;
            flex-shrink: 0;
            padding: 16px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .hero-aside strong {{
            font-size: 12px;
            font-weight: 500;
            color: #e2e8f0;
            line-height: 1.4;
        }}
        .hero-aside-meta {{
            display: flex;
            gap: 8px;
            margin-top: 4px;
            flex-wrap: wrap;
        }}
        .hero-aside-meta span {{
            font-size: 10px;
            font-family: var(--font-mono);
            color: var(--indigo);
            padding: 2px 8px;
            border-radius: 4px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(129, 140, 248, 0.2);
        }}

        /* PANELS */
        .panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            position: relative;
        }}
        .panel-heading {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}
        .panel h2 {{
            font-size: 17px;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: #f1f5f9;
            margin-top: 4px;
        }}
        .panel-description {{
            font-size: 11px;
            color: var(--text-dim);
            margin-top: 4px;
        }}
        .muted-icon {{
            color: var(--text-dim);
        }}

        /* CONTROL GRID (UPPER SECTION) */
        .control-grid {{
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 20px;
        }}
        .config-panel {{
            display: flex;
            flex-direction: column;
        }}
        .form-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px 10px;
            margin-top: 14px;
        }}
        .field-label, .compact-field {{
            display: grid;
            gap: 6px;
            font-size: 11px;
            color: var(--text-muted);
        }}
        .field-label span, .compact-field span {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .field-label small {{
            font-size: 9px;
            color: var(--text-dim);
        }}
        .field-wide {{
            grid-column: span 2;
        }}
        select, input[type="number"], input[type="text"] {{
            width: 100%;
            height: 35px;
            padding: 0 10px;
            border-radius: 7px;
            color: #dbeafe;
            background: var(--bg-inset);
            border: 1px solid var(--border);
            outline: none;
            font-size: 12px;
            font-family: inherit;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        select:focus, input:focus {{
            border-color: rgba(129, 140, 248, 0.75);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
        }}
        .timing-divider {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border);
            margin-top: 18px;
            padding-top: 14px;
        }}
        .timing-note {{
            font-size: 9px;
            color: var(--text-dim);
        }}
        .timing-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }}
        .compact-field input {{
            height: 30px;
            font-size: 11px;
        }}
        .form-error {{
            display: flex;
            gap: 8px;
            align-items: center;
            color: #fca5a5;
            font-size: 11px;
            padding: 9px 11px;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.25);
            border-radius: 7px;
            margin-top: 14px;
        }}
        .control-actions {{
            display: flex;
            gap: 8px;
            margin-top: 18px;
            flex-wrap: wrap;
        }}
        .button {{
            border: 1px solid transparent;
            border-radius: 7px;
            min-height: 34px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 0 12px;
            color: #e2e8f0;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s, border-color 0.2s, transform 0.15s;
        }}
        .button:hover:not(:disabled) {{
            transform: translateY(-1px);
        }}
        .button.primary {{
            background: var(--primary);
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.28);
        }}
        .button.primary:hover:not(:disabled) {{
            background: var(--primary-hover);
        }}
        .button.outline {{
            border-color: rgba(129, 140, 248, 0.35);
            background: rgba(99, 102, 241, 0.08);
            color: #c7d2fe;
        }}
        .button.outline:hover:not(:disabled) {{
            background: rgba(99, 102, 241, 0.18);
        }}
        .button.ghost {{
            color: var(--text-muted);
            background: transparent;
        }}
        .button.ghost:hover:not(:disabled) {{
            color: #ffffff;
            background: rgba(255, 255, 255, 0.05);
        }}
        .button:disabled, .text-button:disabled, .icon-button:disabled {{
            opacity: 0.4;
            cursor: not-allowed;
            transform: none !important;
        }}
        .secondary-controls {{
            display: flex;
            gap: 12px;
            padding: 14px 0 2px;
            border-top: 1px solid var(--border);
            margin-top: 14px;
            flex-wrap: wrap;
        }}
        .text-button {{
            border: 0;
            background: transparent;
            color: var(--text-muted);
            font-size: 11px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
            transition: color 0.15s;
        }}
        .text-button:hover:not(:disabled) {{
            color: #ffffff;
        }}
        .text-button.danger:hover:not(:disabled) {{
            color: #fca5a5;
        }}
        .speed-control {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 8px 12px;
            border-top: 1px solid var(--border);
            margin-top: 14px;
            padding-top: 14px;
            color: var(--text-muted);
            font-size: 11px;
        }}
        .speed-control span {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .speed-control strong {{
            color: #a5b4fc;
            font-family: var(--font-mono);
        }}
        .speed-control input[type="range"] {{
            grid-column: span 2;
            width: 100%;
            accent-color: var(--primary-hover);
            height: 4px;
            cursor: pointer;
        }}

        /* RIGHT STACK */
        .right-stack {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        /* NETWORK PANEL */
        .network-panel {{
            background: radial-gradient(circle at 50% 45%, rgba(30, 41, 59, 0.45), transparent 55%), rgba(17, 24, 39, 0.74);
            overflow: hidden;
        }}
        .legend {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }}
        .legend span {{
            color: var(--text-dim);
            font-size: 10px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .legend-dot {{
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }}
        .legend-dot.normal {{ background: var(--cyan); }}
        .legend-dot.success {{ background: var(--emerald); }}
        .legend-dot.loss {{ background: var(--rose); }}
        .legend-dot.retransmit {{ background: var(--amber); }}

        .network-lanes {{
            display: grid;
            grid-template-columns: 140px 1fr 140px;
            align-items: center;
            gap: 14px;
            margin: 28px 0 22px;
        }}
        .endpoint {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .endpoint-icon {{
            width: 38px;
            height: 38px;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            color: var(--cyan);
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 9px;
        }}
        .endpoint-icon.receiver {{
            color: var(--emerald);
            background: rgba(16, 185, 129, 0.08);
            border-color: rgba(16, 185, 129, 0.28);
        }}
        .endpoint strong {{
            display: block;
            color: #f1f5f9;
            font-size: 12px;
        }}
        .endpoint span {{
            display: block;
            color: var(--text-dim);
            font-size: 9px;
            margin-top: 2px;
            font-family: var(--font-mono);
        }}
        .lane-column {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            position: relative;
        }}
        .lane-label {{
            display: flex;
            justify-content: space-between;
            color: var(--text-dim);
            font-size: 8px;
            letter-spacing: 0.12em;
            font-family: var(--font-mono);
        }}
        .lane-line {{
            height: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
        }}
        .lane-line::before {{
            content: "";
            position: absolute;
            inset: 50% 8px auto;
            height: 1px;
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.2), rgba(99, 102, 241, 0.55), rgba(16, 185, 129, 0.2));
        }}
        .lane-arrow {{
            width: 7px;
            height: 7px;
            border-top: 1px solid var(--indigo);
            border-right: 1px solid var(--indigo);
            transform: rotate(45deg);
            z-index: 1;
        }}
        .lane-arrow.left {{
            transform: rotate(-135deg);
        }}
        .lane-signal {{
            z-index: 2;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--cyan);
            box-shadow: 0 0 12px var(--cyan);
            animation: travel 2.2s ease-in-out infinite;
        }}
        .lane-signal.cyan {{
            background: #06b6d4;
            box-shadow: 0 0 12px #06b6d4;
            animation-direction: reverse;
        }}
        .loss-alert-box {{
            position: absolute;
            top: -24px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.6);
            color: #fecaca;
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 4px;
            animation: pulse 1s infinite;
            display: none;
            z-index: 10;
        }}

        /* WINDOW STRIPS */
        .window-strip {{
            border-top: 1px solid var(--border);
            padding-top: 12px;
        }}
        .receiver-strip {{
            margin-top: 12px;
        }}
        .strip-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .strip-title .mono {{
            color: var(--text-muted);
            font-size: 10px;
        }}
        .frame-track {{
            display: flex;
            gap: 6px;
            overflow-x: auto;
            padding-bottom: 4px;
        }}
        .frame-node {{
            min-width: 40px;
            height: 36px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1px;
            color: var(--text-dim);
            border: 1px solid rgba(100, 116, 139, 0.25);
            border-radius: 6px;
            font-family: var(--font-mono);
            font-size: 10px;
            background: rgba(15, 23, 42, 0.55);
            transition: all 0.2s ease;
        }}
        .frame-node small {{
            font-size: 7px;
            color: inherit;
        }}
        .frame-node.active {{
            color: #bae6fd;
            border-color: rgba(56, 189, 248, 0.5);
            background: rgba(56, 189, 248, 0.12);
        }}
        .frame-node.success, .frame-node.received {{
            color: #a7f3d0;
            border-color: rgba(16, 185, 129, 0.5);
            background: rgba(16, 185, 129, 0.12);
        }}
        .frame-node.buffered {{
            color: #c7d2fe;
            border-color: rgba(129, 140, 248, 0.5);
            background: rgba(99, 102, 241, 0.15);
        }}
        .frame-node.loss {{
            color: #fecaca;
            border-color: rgba(239, 68, 68, 0.6);
            background: rgba(239, 68, 68, 0.18);
        }}
        .frame-node.retransmit {{
            color: #fde68a;
            border-color: rgba(245, 158, 11, 0.6);
            background: rgba(245, 158, 11, 0.15);
            animation: glow 1.6s ease-in-out infinite;
        }}

        /* LAST EVENT CALLOUT */
        .last-event {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 16px;
            padding: 10px 14px;
            border-left: 2px solid var(--primary-hover);
            background: rgba(99, 102, 241, 0.08);
            border-radius: 0 8px 8px 0;
        }}
        .last-event strong {{
            display: block;
            color: #cbd5e1;
            font-size: 11px;
            font-weight: 500;
            margin-top: 2px;
        }}
        .last-event .mono {{
            margin-left: auto;
            color: var(--indigo);
            font-size: 11px;
            white-space: nowrap;
        }}
        .pulse-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--indigo);
            flex-shrink: 0;
        }}

        /* METRICS GRID */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}
        .metric-card {{
            padding: 16px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 11px;
            transition: border-color 0.2s, transform 0.2s;
        }}
        .metric-card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }}
        .metric-card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: #f8fafc;
            font-family: var(--font-mono);
            letter-spacing: -0.03em;
        }}
        .metric-detail {{
            color: var(--text-dim);
            font-size: 10px;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* LOWER GRID */
        .lower-grid {{
            display: grid;
            grid-template-columns: 1.4fr 0.6fr;
            gap: 20px;
        }}
        .timeline-panel, .insight-panel, .experiments-panel {{
            padding: 20px;
        }}
        .timeline-tools {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .timeline-tools select {{
            width: 125px;
            height: 29px;
            font-size: 10px;
        }}
        .frame-search {{
            display: flex;
            align-items: center;
            gap: 6px;
            height: 29px;
            padding: 0 8px;
            border: 1px solid var(--border);
            border-radius: 7px;
            background: var(--bg-inset);
            color: var(--text-dim);
        }}
        .frame-search input {{
            border: 0;
            outline: 0;
            width: 60px;
            padding: 0;
            color: #dbeafe;
            background: transparent;
            font-size: 10px;
            height: auto;
        }}
        .timeline-list {{
            max-height: 340px;
            min-height: 150px;
            margin-top: 14px;
            overflow-y: auto;
            border-top: 1px solid var(--border);
        }}
        .event-row {{
            display: grid;
            grid-template-columns: 32px 46px 105px 1fr auto;
            align-items: center;
            gap: 8px;
            min-height: 36px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.08);
            font-size: 10px;
            padding: 2px 4px;
        }}
        .event-row:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .event-index, .event-time {{
            color: var(--text-dim);
            font-size: 9px;
        }}
        .event-type {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 9px;
            white-space: nowrap;
            font-weight: 500;
        }}
        .event-type i {{
            width: 5px;
            height: 5px;
            border-radius: 50%;
            display: inline-block;
        }}
        .event-description {{
            color: var(--text-muted);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .event-frame {{
            color: var(--indigo);
            font-size: 9px;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 4px;
            background: rgba(99, 102, 241, 0.1);
        }}

        /* PROTOCOL LENS (INSIGHTS) */
        .insight-main {{
            padding: 14px 0 16px;
            border-bottom: 1px solid var(--border);
        }}
        .protocol-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #c7d2fe;
            font-family: var(--font-mono);
            font-size: 10px;
            text-transform: uppercase;
            padding: 5px 9px;
            border: 1px solid rgba(129, 140, 248, 0.25);
            background: rgba(99, 102, 241, 0.1);
            border-radius: 6px;
        }}
        .chip-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--indigo);
        }}
        .insight-main p {{
            color: var(--text-muted);
            font-size: 12px;
            line-height: 1.6;
            margin-top: 10px;
        }}
        .observation-list {{
            padding-top: 16px;
            display: grid;
            gap: 14px;
        }}
        .observation-item {{
            display: flex;
            gap: 10px;
            align-items: flex-start;
            color: var(--indigo);
        }}
        .observation-item span {{
            display: grid;
            gap: 2px;
        }}
        .observation-item strong {{
            color: #cbd5e1;
            font-size: 11px;
            font-weight: 500;
        }}
        .observation-item small {{
            color: var(--text-dim);
            font-size: 10px;
            line-height: 1.4;
        }}

        /* CONTROLLED EVALUATION (BENCHMARK PANEL) */
        .experiments-panel {{
            margin-top: 4px;
        }}
        .experiment-actions {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .icon-button {{
            width: 34px;
            height: 34px;
            border: 1px solid var(--border);
            border-radius: 7px;
            display: grid;
            place-items: center;
            color: var(--text-muted);
            background: rgba(15, 23, 42, 0.6);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .icon-button:hover:not(:disabled) {{
            color: #ffffff;
            border-color: rgba(129, 140, 248, 0.45);
            background: rgba(99, 102, 241, 0.15);
        }}
        .experiment-content {{
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 20px;
            margin-top: 18px;
            align-items: start;
        }}
        .experiment-table-wrap {{
            overflow-x: auto;
        }}
        .experiment-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        .experiment-table th {{
            color: var(--text-dim);
            font-family: var(--font-mono);
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            text-align: left;
            padding: 0 12px 10px;
            white-space: nowrap;
        }}
        .experiment-table td {{
            border-top: 1px solid var(--border);
            padding: 12px;
            color: var(--text-muted);
            white-space: nowrap;
        }}
        .table-protocol {{
            font-family: var(--font-mono);
            font-size: 9px;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .table-protocol.gbn {{
            color: #a5b4fc;
            background: rgba(99, 102, 241, 0.12);
        }}
        .table-protocol.sr {{
            color: #67e8f9;
            background: rgba(6, 182, 212, 0.1);
        }}
        .amber {{
            color: var(--amber) !important;
            font-weight: 600;
        }}
        .cyan {{
            color: #67e8f9 !important;
        }}

        /* DUAL BAR CHART */
        .chart-box {{
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid var(--border);
            border-radius: 9px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .chart-legend {{
            display: flex;
            justify-content: flex-end;
            gap: 14px;
            font-size: 10px;
            color: var(--text-muted);
        }}
        .chart-bars-wrap {{
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            height: 160px;
            padding-top: 10px;
            border-bottom: 1px solid var(--border);
        }}
        .chart-col {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            width: 22%;
        }}
        .bar-pair {{
            display: flex;
            align-items: flex-end;
            gap: 4px;
            height: 120px;
            width: 100%;
            justify-content: center;
        }}
        .bar-seg {{
            width: 14px;
            border-radius: 3px 3px 0 0;
            transition: height 0.4s ease;
            position: relative;
        }}
        .bar-seg.amber {{
            background: var(--amber);
        }}
        .bar-seg.indigo {{
            background: var(--primary-hover);
        }}
        .bar-label {{
            font-size: 10px;
            font-family: var(--font-mono);
            color: var(--text-muted);
            white-space: nowrap;
        }}

        .method-note {{
            display: flex;
            gap: 12px;
            align-items: baseline;
            color: var(--text-dim);
            font-size: 10px;
            line-height: 1.5;
            padding-top: 16px;
            border-top: 1px solid var(--border);
            margin-top: 16px;
        }}
        .method-note .eyebrow {{
            flex-shrink: 0;
        }}

        /* APP FOOTER */
        .app-footer {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 0 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-dim);
            font-size: 10px;
        }}
        .app-footer span {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        /* KEYFRAME ANIMATIONS */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(0.8); }}
        }}
        @keyframes travel {{
            0% {{ transform: translateX(-40px); opacity: 0.2; }}
            50% {{ opacity: 1; }}
            100% {{ transform: translateX(40px); opacity: 0.2; }}
        }}
        @keyframes glow {{
            0%, 100% {{ box-shadow: 0 0 0 rgba(245, 158, 11, 0); }}
            50% {{ box-shadow: 0 0 12px rgba(245, 158, 11, 0.4); }}
        }}

        /* RESPONSIVE */
        @media (max-width: 1024px) {{
            .control-grid, .lower-grid, .experiment-content {{
                grid-template-columns: 1fr;
            }}
            .hero-row {{
                flex-direction: column;
            }}
            .hero-aside {{
                width: 100%;
            }}
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 640px) {{
            .topbar {{
                padding: 0 16px;
            }}
            .dashboard-container {{
                padding: 16px;
            }}
            .network-lanes {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            .event-row {{
                grid-template-columns: 30px 40px 90px 1fr;
            }}
            .event-frame {{
                display: none;
            }}
            .app-footer {{
                flex-direction: column;
                gap: 8px;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="app-shell">
        <!-- TOPBAR -->
        <header class="topbar" data-testid="app-header">
            <div class="brand-block">
                <div class="brand-mark">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M12 12V8"/>
                    </svg>
                </div>
                <div>
                    <div class="brand-title" data-testid="app-title">ARQ LAB <span>／</span> 25CS024</div>
                    <div class="brand-subtitle" data-testid="app-subtitle">Event-driven protocol observatory</div>
                </div>
            </div>
            <div class="topbar-status" data-testid="simulation-status-badge">
                <span id="topbar-status-light" class="status-light"></span>
                <span id="topbar-status-text">READY</span>
                <span class="status-divider">|</span>
                <span class="mono" id="topbar-protocol-badge">GBN · W=3</span>
            </div>
        </header>

        <!-- MAIN DASHBOARD -->
        <main class="dashboard-container">
            <!-- HERO ROW -->
            <section class="hero-row" data-testid="hero-section">
                <div>
                    <div class="eyebrow hero-eyebrow" data-testid="hero-eyebrow">
                        <span class="hero-pulse"></span> DISCRETE EVENT SIMULATOR
                    </div>
                    <h1 data-testid="hero-title">
                        How does loss change<br>
                        <em>recovery behaviour?</em>
                    </h1>
                    <p data-testid="hero-description">
                        Replay Go-Back-N and Selective Repeat frame by frame. Every packet, timeout, ACK, and window slide below is generated by the Python event engine.
                    </p>
                </div>
                <div class="hero-aside" data-testid="hero-question-card">
                    <div class="eyebrow">Research question</div>
                    <strong>How do retransmission counts change with window size and loss pattern?</strong>
                    <div class="hero-aside-meta">
                        <span>2 protocols</span>
                        <span>2 windows</span>
                        <span>deterministic loss</span>
                    </div>
                </div>
            </section>

            <!-- CONTROLS & NETWORK VISUALIZATION -->
            <section class="control-grid" data-testid="control-section">
                <!-- 01 / CONFIGURATION PANEL -->
                <div class="panel config-panel" data-testid="configuration-panel">
                    <div class="panel-heading">
                        <div>
                            <div class="eyebrow" data-testid="config-eyebrow">01 / Configuration</div>
                            <h2 data-testid="config-title">Build a run</h2>
                        </div>
                        <svg class="muted-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M20 7h-9M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>
                        </svg>
                    </div>

                    <div class="form-grid">
                        <label class="field-label" data-testid="protocol-field">
                            <span>Protocol</span>
                            <select id="cfg-protocol" data-testid="protocol-select">
                                <option value="GBN" selected>Go-Back-N</option>
                                <option value="SR">Selective Repeat</option>
                            </select>
                        </label>
                        <label class="field-label" data-testid="window-field">
                            <span>Window size</span>
                            <select id="cfg-window" data-testid="window-size-select">
                                <option value="3" selected>N = 3</option>
                                <option value="5">N = 5</option>
                            </select>
                        </label>
                        <label class="field-label" data-testid="total-frames-field">
                            <span>Total frames</span>
                            <input id="cfg-total-frames" type="number" min="2" max="100" value="10" data-testid="total-frames-input">
                        </label>
                        <label class="field-label field-wide" data-testid="losses-field">
                            <span>First-attempt losses <small>comma separated</small></span>
                            <input id="cfg-losses" type="text" value="4, 7" placeholder="4, 7" data-testid="initial-losses-input">
                        </label>
                    </div>

                    <div class="timing-divider">
                        <span class="eyebrow">Timing model · simulated units</span>
                        <span class="timing-note" data-testid="timing-note">No real-time sleeps in engine</span>
                    </div>

                    <div class="timing-grid">
                        <label class="compact-field">
                            <span>Frame tx</span>
                            <input id="cfg-tx-time" type="number" min="0.1" step="0.1" value="1.0" data-testid="frame-tx-delay-input">
                        </label>
                        <label class="compact-field">
                            <span>Frame prop</span>
                            <input id="cfg-prop-delay" type="number" min="0.1" step="0.1" value="2.0" data-testid="frame-propagation-delay-input">
                        </label>
                        <label class="compact-field">
                            <span>ACK round</span>
                            <input id="cfg-ack-delay" type="number" min="0.1" step="0.1" value="1.0" data-testid="ack-propagation-delay-input">
                        </label>
                        <label class="compact-field">
                            <span>Timeout</span>
                            <input id="cfg-timeout" type="number" min="0.1" step="0.1" value="8.0" data-testid="timeout-input">
                        </label>
                    </div>

                    <div id="form-error-msg" class="form-error" style="display: none;" role="alert" data-testid="configuration-error">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                        <span id="form-error-text">Timeout must be longer than round-trip latency.</span>
                    </div>

                    <div class="control-actions" data-testid="primary-simulation-controls">
                        <button id="btn-start" class="button primary" data-testid="start-simulation-btn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg>
                            Start run
                        </button>
                        <button id="btn-run-all" class="button outline" data-testid="run-completion-btn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                            Run to completion
                        </button>
                        <button id="btn-defaults" class="button ghost" data-testid="restore-defaults-button">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                            Defaults
                        </button>
                    </div>

                    <div class="secondary-controls" data-testid="secondary-simulation-controls">
                        <button id="btn-pause" class="text-button" disabled data-testid="pause-simulation-btn">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                            Pause
                        </button>
                        <button id="btn-resume" class="text-button" disabled data-testid="resume-simulation-btn">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg>
                            Resume
                        </button>
                        <button id="btn-step" class="text-button" data-testid="step-simulation-btn">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2"/></svg>
                            Step forward
                        </button>
                        <button id="btn-reset" class="text-button danger" data-testid="reset-simulation-btn">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>
                            Reset
                        </button>
                    </div>

                    <label class="speed-control" data-testid="speed-control">
                        <span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 14 4-4M3.34 19a10 10 0 1 1 17.32 0"/></svg>
                            Playback speed
                        </span>
                        <strong id="speed-label">1.00×</strong>
                        <input id="speed-slider" type="range" min="0.25" max="4" step="0.25" value="1.0" data-testid="speed-slider">
                    </label>
                </div>

                <!-- RIGHT STACK: NETWORK & METRICS -->
                <div class="right-stack">
                    <!-- LIVE NETWORK VIEW -->
                    <section class="panel network-panel" data-testid="network-visualization-panel">
                        <div class="panel-heading">
                            <div>
                                <div class="eyebrow" data-testid="network-panel-eyebrow">Live network view</div>
                                <h2 data-testid="network-panel-title">Frames in motion</h2>
                            </div>
                            <div class="legend" data-testid="network-legend">
                                <span><i class="legend-dot normal"></i> Outbound</span>
                                <span><i class="legend-dot success"></i> Delivered</span>
                                <span><i class="legend-dot loss"></i> Loss</span>
                                <span><i class="legend-dot retransmit"></i> Retry</span>
                            </div>
                        </div>

                        <div class="network-lanes" data-testid="network-lanes">
                            <!-- SENDER ENDPOINT -->
                            <div class="endpoint sender-endpoint" data-testid="sender-endpoint">
                                <div class="endpoint-icon">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/></svg>
                                </div>
                                <div>
                                    <strong data-testid="sender-label">Sender</strong>
                                    <span id="sender-window-label" data-testid="sender-window-label">Base 1 · W=3</span>
                                </div>
                            </div>

                            <!-- LANES -->
                            <div class="lane-column">
                                <div id="loss-alert-indicator" class="loss-alert-box">FRAME 4 LOST</div>
                                <div class="lane-label" data-testid="sender-to-receiver-label">
                                    <span>DATA CHANNEL</span>
                                    <span class="mono" id="lane-protocol-tag">GBN</span>
                                </div>
                                <div class="lane-line">
                                    <span class="lane-arrow left"></span>
                                    <span id="data-channel-signal" class="lane-signal"></span>
                                    <span class="lane-arrow right"></span>
                                </div>
                                <div class="lane-label ack-label" data-testid="ack-channel-label">
                                    <span>ACK CHANNEL</span>
                                    <span class="mono">reverse path</span>
                                </div>
                                <div class="lane-line ack-line">
                                    <span class="lane-arrow left"></span>
                                    <span id="ack-channel-signal" class="lane-signal cyan"></span>
                                    <span class="lane-arrow right"></span>
                                </div>
                            </div>

                            <!-- RECEIVER ENDPOINT -->
                            <div class="endpoint receiver-endpoint" data-testid="receiver-endpoint">
                                <div class="endpoint-icon receiver">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M12 12V8"/></svg>
                                </div>
                                <div>
                                    <strong data-testid="receiver-label">Receiver</strong>
                                    <span id="receiver-window-label" data-testid="receiver-window-label">Expecting 1</span>
                                </div>
                            </div>
                        </div>

                        <!-- SENDER SLIDING WINDOW STRIP -->
                        <div class="window-strip" data-testid="sender-window-strip">
                            <div class="strip-title">
                                <span class="eyebrow">Sender window</span>
                                <span class="mono" id="sender-window-range">1—3</span>
                            </div>
                            <div id="sender-frame-track" class="frame-track" data-testid="sender-frame-track"></div>
                        </div>

                        <!-- RECEIVER BUFFER STRIP -->
                        <div class="window-strip receiver-strip" data-testid="receiver-window-strip">
                            <div class="strip-title">
                                <span class="eyebrow">Receiver buffer</span>
                                <span class="mono" id="receiver-buffer-count">0 buffered</span>
                            </div>
                            <div id="receiver-frame-track" class="frame-track" data-testid="receiver-frame-track"></div>
                        </div>

                        <!-- LATEST ENGINE EVENT CALLOUT -->
                        <div class="last-event" data-testid="active-event-callout">
                            <span id="event-pulse-dot" class="pulse-dot"></span>
                            <div>
                                <span class="eyebrow">Latest engine event</span>
                                <strong id="latest-event-desc" data-testid="latest-event-description">Ready. Press "Start run" to execute.</strong>
                            </div>
                            <span class="mono" id="latest-event-time" data-testid="latest-event-time">t=0.0u</span>
                        </div>
                    </section>

                    <!-- METRICS DASHBOARD (4 STAT CARDS) -->
                    <div class="metrics-grid" data-testid="metrics-dashboard">
                        <div class="metric-card" data-testid="metric-retransmissions">
                            <div class="metric-card-top">
                                <span class="eyebrow">Retransmissions</span>
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="var(--amber)"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                            </div>
                            <div class="metric-value" id="metric-retransmissions-val" style="color: var(--amber);">0</div>
                            <div class="metric-detail" id="metric-retransmissions-detail">0 total attempts</div>
                        </div>

                        <div class="metric-card" data-testid="metric-completion-steps">
                            <div class="metric-card-top">
                                <span class="eyebrow">Completion steps</span>
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--indigo)" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                            </div>
                            <div class="metric-value" id="metric-steps-val" style="color: var(--indigo);">—</div>
                            <div class="metric-detail">processed engine events</div>
                        </div>

                        <div class="metric-card" data-testid="metric-completion-time">
                            <div class="metric-card-top">
                                <span class="eyebrow">Simulated time</span>
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--purple)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16.5 12"/></svg>
                            </div>
                            <div class="metric-value" id="metric-time-val" style="color: var(--purple);">—</div>
                            <div class="metric-detail" id="metric-time-detail">0 timeout events</div>
                        </div>

                        <div class="metric-card" data-testid="metric-delivery">
                            <div class="metric-card-top">
                                <span class="eyebrow">In-order delivery</span>
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--emerald)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                            </div>
                            <div class="metric-value" id="metric-delivery-val" style="color: var(--emerald);">0/10</div>
                            <div class="metric-detail" id="metric-delivery-detail">2 initial losses</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- LOWER GRID: TIMELINE & PROTOCOL LENS -->
            <section class="lower-grid" data-testid="analysis-section">
                <!-- 02 / EVENT STREAM TIMELINE -->
                <div class="panel timeline-panel" data-testid="event-timeline-container">
                    <div class="panel-heading">
                        <div>
                            <div class="eyebrow" data-testid="timeline-eyebrow">02 / Event stream</div>
                            <h2 data-testid="timeline-title">Replayable timeline <span id="timeline-count-badge" style="font-size: 11px; color: var(--text-dim); margin-left: 6px;">0</span></h2>
                        </div>
                        <div class="timeline-tools">
                            <select id="timeline-filter" data-testid="event-type-filter">
                                <option value="ALL">All events</option>
                                <option value="FRAME_TX">Transmit</option>
                                <option value="FRAME_ARRIVAL">Arrival</option>
                                <option value="FRAME_DELIVERED">Delivered</option>
                                <option value="FRAME_LOST">Loss</option>
                                <option value="RETRANSMIT">Retransmit</option>
                                <option value="ACK_SEND">ACK sent</option>
                                <option value="ACK_ARRIVAL">ACK received</option>
                                <option value="TIMEOUT">Timeout</option>
                                <option value="FRAME_BUFFERED">Buffered</option>
                            </select>
                            <label class="frame-search">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                                <input id="frame-search-input" type="text" placeholder="Frame #" data-testid="timeline-frame-filter">
                            </label>
                        </div>
                    </div>
                    <div id="timeline-list" class="timeline-list" data-testid="timeline-list">
                        <div style="padding: 40px; text-align: center; color: var(--text-dim); font-size: 11px;">
                            Engine events will appear here once the run is started.
                        </div>
                    </div>
                </div>

                <!-- 03 / PROTOCOL LENS -->
                <div class="panel insight-panel" data-testid="insight-panel">
                    <div class="panel-heading">
                        <div>
                            <div class="eyebrow" data-testid="insight-eyebrow">03 / Protocol lens</div>
                            <h2 data-testid="insight-title">What to watch</h2>
                        </div>
                        <svg class="muted-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>
                    </div>

                    <div class="insight-main">
                        <div id="protocol-badge-chip" class="protocol-chip" data-testid="protocol-chip">
                            <span class="chip-dot"></span>
                            <span id="protocol-chip-label">Go-Back-N</span>
                        </div>
                        <p id="protocol-explanation-text" data-testid="protocol-explanation">
                            A timeout at the oldest missing frame can resend every outstanding frame in the window. Watch the retransmission count grow when a loss blocks cumulative progress.
                        </p>
                    </div>

                    <div class="observation-list" data-testid="observation-list">
                        <div class="observation-item">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="14" r="8"/><line x1="12" y1="14" x2="15" y2="11"/><line x1="10" y1="2" x2="14" y2="2"/></svg>
                            <span>
                                <strong>Timeout model</strong>
                                <small>Old timers are invalidated with generation numbers.</small>
                            </span>
                        </div>
                        <div class="observation-item">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.5-8.58 3.91a2 2 0 0 1-1.66 0L2 12.5"/></svg>
                            <span>
                                <strong>Absolute numbering</strong>
                                <small>Frames 1 through N avoid wraparound for clarity.</small>
                            </span>
                        </div>
                        <div class="observation-item">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/></svg>
                            <span>
                                <strong>Reproducible loss</strong>
                                <small>Only the first attempt of selected frames is dropped.</small>
                            </span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 04 / CONTROLLED EVALUATION (BENCHMARK MATRIX) -->
            <section class="panel experiments-panel" data-testid="experiments-panel">
                <div class="panel-heading">
                    <div>
                        <div class="eyebrow" data-testid="experiments-eyebrow">04 / Controlled evaluation</div>
                        <h2 data-testid="experiments-title">Four-run comparison</h2>
                        <p class="panel-description" data-testid="experiments-description">
                            Same loss pattern, same timing model. Only protocol and sender window change.
                        </p>
                    </div>
                    <div class="experiment-actions">
                        <button id="btn-benchmark-run" class="button primary" data-testid="run-all-experiments-btn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/></svg>
                            Run all experiments
                        </button>
                        <button id="btn-export-json" class="icon-button" title="Export JSON" data-testid="export-json-btn">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
                        </button>
                        <button id="btn-export-csv" class="icon-button" title="Export CSV" data-testid="export-csv-btn">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                        </button>
                    </div>
                </div>

                <div class="experiment-content">
                    <!-- TABLE -->
                    <div class="experiment-table-wrap">
                        <table class="experiment-table" data-testid="experiment-results-table">
                            <thead>
                                <tr>
                                    <th>Run</th>
                                    <th>Retransmissions</th>
                                    <th>Completion steps</th>
                                    <th>Sim time</th>
                                    <th>Timeouts</th>
                                    <th>Buffered</th>
                                </tr>
                            </thead>
                            <tbody id="benchmark-table-body"></tbody>
                        </table>
                    </div>

                    <!-- DUAL BAR CHART -->
                    <div class="chart-box" data-testid="experiment-chart">
                        <div class="chart-legend">
                            <span><i class="legend-dot retransmit"></i> Retransmissions</span>
                            <span><i class="legend-dot" style="background: var(--primary-hover);"></i> Completion steps</span>
                        </div>
                        <div id="chart-bars" class="chart-bars-wrap"></div>
                    </div>
                </div>

                <div class="method-note" data-testid="methodology-note">
                    <span class="eyebrow">Method note</span>
                    <span>Completion steps count processed queue events through the event that establishes completion. Completion time is the simulated timestamp of that event; they are not interchangeable.</span>
                </div>
            </section>
        </main>

        <!-- FOOTER -->
        <footer class="app-footer" data-testid="app-footer">
            <span>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                Live engine telemetry
            </span>
            <span>Python priority queue · deterministic sequence ordering · absolute frame numbers</span>
            <span class="mono" id="footer-queue-count">standby</span>
        </footer>
    </div>

    <!-- CLIENT SCRIPT: ENGINE & USER INTERACTION -->
    <script>
        // Precomputed benchmark data from Python ARQSimulator
        const BENCHMARK_DATA = {benchmark_json};

        // State Machine
        let currentConfig = {{
            protocol: "GBN",
            window_size: 3,
            total_frames: 10,
            initial_losses: [4, 7],
            timing: {{
                tx: 1.0,
                prop: 2.0,
                ack_delay: 1.0,
                timeout: 8.0
            }}
        }};

        let activeSimulation = null;
        let currentStepIndex = 0;
        let playbackTimer = null;
        let playbackSpeed = 1.0;
        let isRunning = false;

        // Color mapping for events
        const eventColors = {{
            "FRAME_TX": "#38bdf8",
            "FRAME_TX_LOST": "#ef4444",
            "FRAME_RETRANS": "#f59e0b",
            "FRAME_RETRANS_LOST": "#ef4444",
            "FRAME_ARRIVAL": "#10b981",
            "FRAME_RCV_IN_ORDER": "#10b981",
            "APP_DELIVERY": "#10b981",
            "FRAME_DISCARDED": "#ef4444",
            "FRAME_RCV_BUFFERED": "#818cf8",
            "ACK_TX_CUMULATIVE": "#06b6d4",
            "ACK_TX_INDIVIDUAL": "#06b6d4",
            "ACK_TX_DUPLICATE": "#06b6d4",
            "ACK_ARRIVAL": "#06b6d4",
            "TIMEOUT_GBN": "#a855f7",
            "TIMEOUT_SR": "#a855f7",
            "SIMULATION_COMPLETE": "#34d399"
        }};

        const eventLabels = {{
            "FRAME_TX": "Transmit",
            "FRAME_TX_LOST": "Loss",
            "FRAME_RETRANS": "Retransmit",
            "FRAME_RETRANS_LOST": "Loss (Retry)",
            "FRAME_ARRIVAL": "Arrival",
            "FRAME_RCV_IN_ORDER": "Delivered",
            "APP_DELIVERY": "Delivered",
            "FRAME_DISCARDED": "Discarded",
            "FRAME_RCV_BUFFERED": "Buffered",
            "ACK_TX_CUMULATIVE": "ACK sent",
            "ACK_TX_INDIVIDUAL": "ACK sent",
            "ACK_TX_DUPLICATE": "Dup ACK",
            "ACK_ARRIVAL": "ACK received",
            "TIMEOUT_GBN": "Timeout",
            "TIMEOUT_SR": "Timeout",
            "SIMULATION_COMPLETE": "Complete"
        }};

        // Mini Discrete-Event Priority Queue Engine in JS for on-the-fly custom runs
        class JSEventQueue {{
            constructor() {{ this.queue = []; }}
            push(item) {{
                this.queue.push(item);
                this.queue.sort((a, b) => a.time - b.time || a.id - b.id);
            }}
            pop() {{ return this.queue.shift(); }}
            isEmpty() {{ return this.queue.length === 0; }}
        }}

        function simulateARQ(cfg) {{
            const proto = cfg.protocol;
            const W = cfg.window_size;
            const total = cfg.total_frames;
            const lossSet = new Set(cfg.initial_losses);
            const txTime = cfg.timing.tx;
            const prop = cfg.timing.prop;
            const ackProp = cfg.timing.ack_delay;
            const timeoutVal = cfg.timing.timeout;

            const pq = new JSEventQueue();
            let eventId = 0;
            let currentTime = 0;
            let eventsProcessed = 0;

            let sendBase = 0;
            let nextSeqNum = 0;
            let senderNextTx = 0;
            const txAttempts = {{}};
            for (let i = 0; i < total; i++) txAttempts[i] = 0;

            let rcvBase = 0;
            const delivered = [];
            const rcvBuffer = {{}};

            let gbnTimerActive = false;
            let gbnTimerSeq = 0;

            const srTimerActive = {{}};
            const srTimerSeq = {{}};
            const srSenderAcked = {{}};
            for (let i = 0; i < total; i++) {{
                srTimerActive[i] = false;
                srTimerSeq[i] = 0;
                srSenderAcked[i] = false;
            }}

            let origCount = 0;
            let retransCount = 0;
            let ackCount = 0;
            let timeoutCount = 0;

            const snapshots = [];
            const events = [];

            function logSnapshot(type, fId, aId, desc) {{
                const fStates = [];
                for (let i = 0; i < total; i++) {{
                    let st = "idle";
                    if (delivered.includes(i)) st = "delivered";
                    else if (rcvBuffer[i]) st = "buffered";
                    else if (i === fId && (type.includes("LOST"))) st = "loss";
                    else if (txAttempts[i] > 1) st = "retransmitting";
                    else if (i >= sendBase && i < sendBase + W && txAttempts[i] > 0) st = "active";
                    else if (i >= sendBase && i < sendBase + W) st = "active";

                    fStates.push({{
                        frame: i + 1,
                        status: st,
                        attempts: txAttempts[i]
                    }});
                }}

                let activeLoss = null;
                if (type.includes("LOST")) {{
                    activeLoss = fId + 1;
                }}

                const snap = {{
                    step: snapshots.length,
                    timestamp: Math.round(currentTime * 10) / 10,
                    event_type: type,
                    frame: fId !== null ? fId + 1 : null,
                    ack: aId !== null ? aId + 1 : null,
                    description: desc,
                    sender_base: sendBase + 1,
                    window_size: W,
                    receiver_expected: rcvBase + 1,
                    receiver_buffer: Object.keys(rcvBuffer).map(k => Number(k) + 1),
                    frame_states: fStates,
                    loss_alert: activeLoss,
                    metrics: {{
                        retransmissions: retransCount,
                        total_attempts: origCount + retransCount,
                        completion_steps: eventsProcessed,
                        completion_time: Math.round(currentTime * 10) / 10,
                        timeouts: timeoutCount,
                        delivered_in_order: delivered.length,
                        total_frames: total,
                        frame_losses: lossSet.size
                    }}
                }};
                snapshots.push(snap);
                events.push({{
                    sequence: events.length + 1,
                    timestamp: snap.timestamp,
                    event_type: type,
                    frame: snap.frame,
                    description: desc
                }});
            }}

            function trySendNew() {{
                while (nextSeqNum < total && (nextSeqNum - sendBase) < W) {{
                    const f = nextSeqNum;
                    const start = Math.max(currentTime, senderNextTx);
                    senderNextTx = start + txTime;
                    origCount++;
                    txAttempts[f]++;
                    const att = txAttempts[f];

                    if (proto === "GBN") {{
                        if (!gbnTimerActive) {{
                            gbnTimerActive = true;
                            gbnTimerSeq++;
                            pq.push({{ time: start + timeoutVal, id: ++eventId, type: "TIMEOUT_GBN", fId: null, data: {{ seq: gbnTimerSeq }} }});
                        }}
                    }} else {{
                        srTimerActive[f] = true;
                        srTimerSeq[f]++;
                        pq.push({{ time: start + timeoutVal, id: ++eventId, type: "TIMEOUT_SR", fId: f, data: {{ seq: srTimerSeq[f] }} }});
                    }}

                    // Loss condition: 1st attempt only for loss frames
                    const isLoss = (lossSet.has(f + 1) && att === 1);
                    const arriveTime = start + txTime + prop;

                    if (isLoss) {{
                        logSnapshot("FRAME_TX_LOST", f, null, `Sender transmitted Frame ${{f + 1}} (attempt ${{att}}) -> LOST in channel`);
                    }} else {{
                        logSnapshot("FRAME_TX", f, null, `Sender transmitted Frame ${{f + 1}} (attempt ${{att}})`);
                        pq.push({{ time: arriveTime, id: ++eventId, type: "FRAME_ARRIVAL", fId: f, data: {{ att }} }});
                    }}
                    nextSeqNum++;
                }}
            }}

            trySendNew();

            while (!pq.isEmpty()) {{
                const ev = pq.pop();
                currentTime = ev.time;
                eventsProcessed++;

                if (delivered.length === total && sendBase === total) break;

                if (ev.type === "FRAME_ARRIVAL") {{
                    const f = ev.fId;
                    if (proto === "GBN") {{
                        if (f === rcvBase) {{
                            delivered.push(f);
                            rcvBase++;
                            logSnapshot("FRAME_RCV_IN_ORDER", f, null, `Receiver accepted in-order Frame ${{f + 1}}. Next expected: ${{rcvBase + 1}}`);
                            ackCount++;
                            const aEnd = currentTime + 0.2 + ackProp;
                            pq.push({{ time: aEnd, id: ++eventId, type: "ACK_ARRIVAL", fId: null, data: {{ ack: f }} }});
                            logSnapshot("ACK_TX_CUMULATIVE", null, f, `Receiver sent cumulative ACK ${{f + 1}}`);
                        }} else {{
                            logSnapshot("FRAME_DISCARDED", f, null, `Receiver discarded out-of-order Frame ${{f + 1}}. Expecting ${{rcvBase + 1}}`);
                            if (rcvBase > 0) {{
                                ackCount++;
                                const aEnd = currentTime + 0.2 + ackProp;
                                pq.push({{ time: aEnd, id: ++eventId, type: "ACK_ARRIVAL", fId: null, data: {{ ack: rcvBase - 1 }} }});
                                logSnapshot("ACK_TX_DUPLICATE", null, rcvBase - 1, `Receiver resent duplicate ACK ${{rcvBase}}`);
                            }}
                        }}
                    }} else {{
                        // SR
                        if (f >= rcvBase && f < rcvBase + W) {{
                            rcvBuffer[f] = true;
                            logSnapshot("FRAME_RCV_BUFFERED", f, null, `Receiver buffered out-of-order Frame ${{f + 1}}`);
                            ackCount++;
                            const aEnd = currentTime + 0.2 + ackProp;
                            pq.push({{ time: aEnd, id: ++eventId, type: "ACK_ARRIVAL", fId: null, data: {{ ack: f }} }});
                            logSnapshot("ACK_TX_INDIVIDUAL", null, f, `Receiver sent selective ACK ${{f + 1}}`);

                            while (rcvBuffer[rcvBase]) {{
                                delivered.push(rcvBase);
                                logSnapshot("APP_DELIVERY", rcvBase, null, `Receiver delivered in-order Frame ${{rcvBase + 1}} to application`);
                                rcvBase++;
                            }}
                        }} else if (f < rcvBase) {{
                            ackCount++;
                            const aEnd = currentTime + 0.2 + ackProp;
                            pq.push({{ time: aEnd, id: ++eventId, type: "ACK_ARRIVAL", fId: null, data: {{ ack: f }} }});
                            logSnapshot("ACK_TX_INDIVIDUAL", null, f, `Receiver sent ACK ${{f + 1}} for already-delivered frame`);
                        }}
                    }}
                }} else if (ev.type === "ACK_ARRIVAL") {{
                    const ackVal = ev.data.ack;
                    if (proto === "GBN") {{
                        if (ackVal >= sendBase) {{
                            sendBase = ackVal + 1;
                            logSnapshot("ACK_ARRIVAL", null, ackVal, `Sender received ACK ${{ackVal + 1}}. Window base slides to ${{sendBase + 1}}`);
                            if (sendBase === nextSeqNum) {{
                                gbnTimerActive = false;
                            }} else {{
                                gbnTimerActive = true;
                                gbnTimerSeq++;
                                pq.push({{ time: currentTime + timeoutVal, id: ++eventId, type: "TIMEOUT_GBN", fId: null, data: {{ seq: gbnTimerSeq }} }});
                            }}
                            trySendNew();
                        }}
                    }} else {{
                        // SR
                        if (ackVal < total) {{
                            srSenderAcked[ackVal] = true;
                            srTimerActive[ackVal] = false;
                            logSnapshot("ACK_ARRIVAL", null, ackVal, `Sender received individual ACK ${{ackVal + 1}}`);
                            while (srSenderAcked[sendBase] && sendBase < total) {{
                                sendBase++;
                            }}
                            trySendNew();
                        }}
                    }}
                }} else if (ev.type === "TIMEOUT_GBN") {{
                    if (gbnTimerActive && ev.data.seq === gbnTimerSeq && sendBase < total) {{
                        timeoutCount++;
                        logSnapshot("TIMEOUT_GBN", sendBase, null, `TIMEOUT at Sender for Frame ${{sendBase + 1}}! Retransmitting window [${{sendBase + 1}}..${{nextSeqNum}}]`);
                        gbnTimerSeq++;
                        pq.push({{ time: currentTime + timeoutVal, id: ++eventId, type: "TIMEOUT_GBN", fId: null, data: {{ seq: gbnTimerSeq }} }});

                        senderNextTx = Math.max(currentTime, senderNextTx);
                        for (let f = sendBase; f < nextSeqNum; f++) {{
                            const start = senderNextTx;
                            senderNextTx = start + txTime;
                            retransCount++;
                            txAttempts[f]++;
                            const att = txAttempts[f];

                            // Retransmission succeeds
                            logSnapshot("FRAME_RETRANS", f, null, `Sender retransmitted Frame ${{f + 1}} (attempt ${{att}})`);
                            pq.push({{ time: start + txTime + prop, id: ++eventId, type: "FRAME_ARRIVAL", fId: f, data: {{ att }} }});
                        }}
                    }}
                }} else if (ev.type === "TIMEOUT_SR") {{
                    const f = ev.fId;
                    if (srTimerActive[f] && ev.data.seq === srTimerSeq[f] && !srSenderAcked[f]) {{
                        timeoutCount++;
                        logSnapshot("TIMEOUT_SR", f, null, `TIMEOUT for Frame ${{f + 1}}! Selective retransmission started`);
                        srTimerSeq[f]++;
                        pq.push({{ time: currentTime + timeoutVal, id: ++eventId, type: "TIMEOUT_SR", fId: f, data: {{ seq: srTimerSeq[f] }} }});

                        const start = Math.max(currentTime, senderNextTx);
                        senderNextTx = start + txTime;
                        retransCount++;
                        txAttempts[f]++;
                        const att = txAttempts[f];

                        logSnapshot("FRAME_RETRANS", f, null, `Sender retransmitted Frame ${{f + 1}} (attempt ${{att}})`);
                        pq.push({{ time: start + txTime + prop, id: ++eventId, type: "FRAME_ARRIVAL", fId: f, data: {{ att }} }});
                    }}
                }}
            }}

            logSnapshot("SIMULATION_COMPLETE", null, null, "All frames successfully transferred and acknowledged in order.");
            return {{
                snapshots,
                events,
                metrics: snapshots[snapshots.length - 1].metrics
            }};
        }}

        // UI Binding & State Controllers
        function updateConfigFromInputs() {{
            const proto = document.getElementById("cfg-protocol").value;
            const w = Number(document.getElementById("cfg-window").value);
            const total = Number(document.getElementById("cfg-total-frames").value);
            const rawLosses = document.getElementById("cfg-losses").value;
            const losses = rawLosses.split(",")
                .map(s => Number(s.trim()))
                .filter(n => Number.isFinite(n) && n >= 1 && n <= total);

            const tx = Number(document.getElementById("cfg-tx-time").value);
            const prop = Number(document.getElementById("cfg-prop-delay").value);
            const ackD = Number(document.getElementById("cfg-ack-delay").value);
            const timeout = Number(document.getElementById("cfg-timeout").value);

            // Validation
            const errBox = document.getElementById("form-error-msg");
            const errText = document.getElementById("form-error-text");
            if (timeout <= (tx + prop + 0.2 + ackD)) {{
                errText.textContent = "Timeout must be longer than one full Round-Trip Time (RTT).";
                errBox.style.display = "flex";
                return null;
            }}
            if (losses.length === 0 && rawLosses.trim() !== "") {{
                errText.textContent = "Please provide valid frame numbers for losses.";
                errBox.style.display = "flex";
                return null;
            }}
            errBox.style.display = "none";

            currentConfig = {{
                protocol: proto,
                window_size: w,
                total_frames: total,
                initial_losses: losses,
                timing: {{ tx, prop, ack_delay: ackD, timeout }}
            }};

            document.getElementById("topbar-protocol-badge").textContent = `${{proto}} · W=${{w}}`;
            document.getElementById("lane-protocol-tag").textContent = proto;
            document.getElementById("protocol-chip-label").textContent = proto === "GBN" ? "Go-Back-N" : "Selective Repeat";
            document.getElementById("protocol-explanation-text").textContent = proto === "GBN"
                ? "A timeout at the oldest missing frame can resend every outstanding frame in the window. Watch the retransmission count grow when a loss blocks cumulative progress."
                : "Each frame has its own timer and ACK. Later frames can be buffered and delivered after the missing frame returns, so recovery is selective.";

            return currentConfig;
        }}

        function renderFrameTracks(snap) {{
            const total = currentConfig.total_frames;
            const sTrack = document.getElementById("sender-frame-track");
            const rTrack = document.getElementById("receiver-frame-track");

            sTrack.innerHTML = "";
            rTrack.innerHTML = "";

            const sBase = snap ? snap.sender_base : 1;
            const W = snap ? snap.window_size : currentConfig.window_size;
            const rExp = snap ? snap.receiver_expected : 1;
            const rBuf = snap ? (snap.receiver_buffer || []) : [];

            document.getElementById("sender-window-label").textContent = `Base ${{sBase}} · W=${{W}}`;
            document.getElementById("sender-window-range").textContent = `${{sBase}}—${{Math.min(total, sBase + W - 1)}}`;
            document.getElementById("receiver-window-label").textContent = `Expecting ${{rExp}}`;
            document.getElementById("receiver-buffer-count").textContent = `${{rBuf.length}} buffered`;

            for (let i = 1; i <= total; i++) {{
                // Sender frame node
                const sNode = document.createElement("div");
                sNode.className = "frame-node";
                let sState = "idle";
                let attempts = 0;

                if (snap && snap.frame_states) {{
                    const fs = snap.frame_states.find(item => item.frame === i);
                    if (fs) {{
                        sState = fs.status;
                        attempts = fs.attempts;
                    }}
                }} else {{
                    if (i >= sBase && i < sBase + W) sState = "active";
                }}

                sNode.classList.add(sState);
                sNode.innerHTML = `<span>F${{i}}</span>` + (attempts > 1 ? `<small>${{attempts}}×</small>` : "");
                sTrack.appendChild(sNode);

                // Receiver frame node
                const rNode = document.createElement("div");
                rNode.className = "frame-node";
                let rState = "idle";
                if (snap) {{
                    if (i < rExp) rState = "success";
                    else if (rBuf.includes(i)) rState = "buffered";
                    else if (i === rExp) rState = "active";
                }}
                rNode.classList.add(rState);
                rNode.innerHTML = `<span>F${{i}}</span>`;
                rTrack.appendChild(rNode);
            }}

            // Frame 4 / 7 loss alert banner
            const lossBox = document.getElementById("loss-alert-indicator");
            if (snap && snap.loss_alert) {{
                lossBox.textContent = `FRAME ${{snap.loss_alert}} LOST`;
                lossBox.style.display = "block";
            }} else {{
                lossBox.style.display = "none";
            }}
        }}

        function renderMetrics(metrics) {{
            if (!metrics) return;
            document.getElementById("metric-retransmissions-val").textContent = metrics.retransmissions ?? 0;
            document.getElementById("metric-retransmissions-detail").textContent = `${{metrics.total_attempts ?? 0}} total attempts`;
            document.getElementById("metric-steps-val").textContent = metrics.completion_steps ?? "—";
            document.getElementById("metric-time-val").textContent = metrics.completion_time ? `${{metrics.completion_time.toFixed(1)}}u` : "—";
            document.getElementById("metric-time-detail").textContent = `${{metrics.timeouts ?? 0}} timeout events`;
            document.getElementById("metric-delivery-val").textContent = `${{metrics.delivered_in_order ?? 0}}/${{metrics.total_frames ?? 10}}`;
            document.getElementById("metric-delivery-detail").textContent = `${{metrics.frame_losses ?? 2}} initial losses`;
        }}

        function renderTimeline(events) {{
            const listEl = document.getElementById("timeline-list");
            const filter = document.getElementById("timeline-filter").value;
            const search = document.getElementById("frame-search-input").value.trim();

            const filtered = (events || []).filter(e => {{
                const matchType = (filter === "ALL" || e.event_type.includes(filter));
                const matchFrame = (!search || (e.frame && String(e.frame).includes(search)));
                return matchType && matchFrame;
            }});

            document.getElementById("timeline-count-badge").textContent = filtered.length;

            if (filtered.length === 0) {{
                listEl.innerHTML = `<div style="padding: 30px; text-align: center; color: var(--text-dim); font-size: 11px;">No matching events found.</div>`;
                return;
            }}

            listEl.innerHTML = filtered.slice().reverse().map(e => {{
                const dotColor = eventColors[e.event_type] || "#94a3b8";
                const label = eventLabels[e.event_type] || e.event_type;
                const framePill = e.frame ? `<span class="event-frame mono">F${{e.frame}}</span>` : "";
                return `
                    <div class="event-row">
                        <span class="event-index mono">${{String(e.sequence).padStart(3, "0")}}</span>
                        <span class="event-time mono">${{e.timestamp.toFixed(1)}}</span>
                        <span class="event-type" style="color: ${{dotColor}};">
                            <i style="background: ${{dotColor}};"></i> ${{label}}
                        </span>
                        <span class="event-description">${{e.description}}</span>
                        ${{framePill}}
                    </div>
                `;
            }}).join("");
        }}

        function applySnapshot(index) {{
            if (!activeSimulation || !activeSimulation.snapshots[index]) return;
            const snap = activeSimulation.snapshots[index];
            currentStepIndex = index;

            renderFrameTracks(snap);
            renderMetrics(snap.metrics);

            // Latest event callout
            const dot = document.getElementById("event-pulse-dot");
            dot.style.background = eventColors[snap.event_type] || "#818cf8";
            document.getElementById("latest-event-desc").textContent = snap.description;
            document.getElementById("latest-event-time").textContent = `t=${{snap.timestamp.toFixed(1)}}u`;

            // Status light
            const light = document.getElementById("topbar-status-light");
            const statusText = document.getElementById("topbar-status-text");
            if (index === activeSimulation.snapshots.length - 1) {{
                light.className = "status-light completed";
                statusText.textContent = "COMPLETED";
                document.getElementById("footer-queue-count").textContent = "0 queued · completed";
            }} else if (isRunning) {{
                light.className = "status-light running";
                statusText.textContent = "RUNNING";
                document.getElementById("footer-queue-count").textContent = `${{activeSimulation.snapshots.length - index}} queued`;
            }} else {{
                light.className = "status-light";
                statusText.textContent = "PAUSED";
            }}

            renderTimeline(activeSimulation.events.slice(0, index + 1));
        }}

        function startPlayback() {{
            const cfg = updateConfigFromInputs();
            if (!cfg) return;

            // Run simulation engine
            activeSimulation = simulateARQ(cfg);
            currentStepIndex = 0;
            isRunning = true;

            document.getElementById("btn-start").disabled = true;
            document.getElementById("btn-pause").disabled = false;
            document.getElementById("btn-resume").disabled = true;

            if (playbackTimer) clearInterval(playbackTimer);

            const intervalMs = Math.max(120, 650 / playbackSpeed);
            playbackTimer = setInterval(() => {{
                if (currentStepIndex < activeSimulation.snapshots.length - 1) {{
                    applySnapshot(currentStepIndex + 1);
                }} else {{
                    pausePlayback();
                }}
            }}, intervalMs);

            applySnapshot(0);
        }}

        function pausePlayback() {{
            isRunning = false;
            if (playbackTimer) clearInterval(playbackTimer);
            playbackTimer = null;

            document.getElementById("btn-start").disabled = false;
            document.getElementById("btn-pause").disabled = true;
            document.getElementById("btn-resume").disabled = false;

            const light = document.getElementById("topbar-status-light");
            const statusText = document.getElementById("topbar-status-text");
            if (activeSimulation && currentStepIndex === activeSimulation.snapshots.length - 1) {{
                light.className = "status-light completed";
                statusText.textContent = "COMPLETED";
            }} else {{
                light.className = "status-light";
                statusText.textContent = "PAUSED";
            }}
        }}

        function resumePlayback() {{
            if (!activeSimulation) return startPlayback();
            isRunning = true;
            document.getElementById("btn-pause").disabled = false;
            document.getElementById("btn-resume").disabled = true;

            if (playbackTimer) clearInterval(playbackTimer);
            const intervalMs = Math.max(120, 650 / playbackSpeed);
            playbackTimer = setInterval(() => {{
                if (currentStepIndex < activeSimulation.snapshots.length - 1) {{
                    applySnapshot(currentStepIndex + 1);
                }} else {{
                    pausePlayback();
                }}
            }}, intervalMs);
        }}

        function stepForward() {{
            if (!activeSimulation) {{
                const cfg = updateConfigFromInputs();
                if (!cfg) return;
                activeSimulation = simulateARQ(cfg);
                currentStepIndex = 0;
                applySnapshot(0);
                return;
            }}
            pausePlayback();
            if (currentStepIndex < activeSimulation.snapshots.length - 1) {{
                applySnapshot(currentStepIndex + 1);
            }}
        }}

        function resetPlayback() {{
            pausePlayback();
            activeSimulation = null;
            currentStepIndex = 0;
            renderFrameTracks(null);
            document.getElementById("topbar-status-light").className = "status-light";
            document.getElementById("topbar-status-text").textContent = "READY";
            document.getElementById("latest-event-desc").textContent = 'Ready. Press "Start run" to execute.';
            document.getElementById("latest-event-time").textContent = "t=0.0u";
            document.getElementById("loss-alert-indicator").style.display = "none";
            document.getElementById("footer-queue-count").textContent = "standby";
            renderTimeline([]);
            renderMetrics({{
                retransmissions: 0,
                total_attempts: 0,
                completion_steps: "—",
                completion_time: 0,
                timeouts: 0,
                delivered_in_order: 0,
                total_frames: currentConfig.total_frames,
                frame_losses: currentConfig.initial_losses.length
            }});
        }}

        function runToCompletion() {{
            const cfg = updateConfigFromInputs();
            if (!cfg) return;
            pausePlayback();
            activeSimulation = simulateARQ(cfg);
            applySnapshot(activeSimulation.snapshots.length - 1);
        }}

        // Benchmark Matrix & Chart
        function renderBenchmarkTable(dataList) {{
            const tbody = document.getElementById("benchmark-table-body");
            tbody.innerHTML = dataList.map(item => `
                <tr>
                    <td>
                        <span class="table-protocol ${{item.protocol === 'SR' ? 'sr' : 'gbn'}}">${{item.protocol}}</span>
                        <strong style="margin-left: 6px;">N=${{item.window_size}}</strong>
                    </td>
                    <td class="mono amber">${{item.retransmissions}}</td>
                    <td class="mono">${{item.completion_event_steps}}</td>
                    <td class="mono">${{item.completion_simulated_time.toFixed(1)}}u</td>
                    <td class="mono">${{item.timeouts}}</td>
                    <td class="mono cyan">${{item.buffered_out_of_order}}</td>
                </tr>
            `).join("");

            // Render Chart Bars
            const chartBars = document.getElementById("chart-bars");
            const maxVal = Math.max(...dataList.map(d => Math.max(d.retransmissions, d.completion_event_steps)), 30);

            chartBars.innerHTML = dataList.map(item => {{
                const retH = Math.max(8, Math.round((item.retransmissions / maxVal) * 110));
                const stepH = Math.max(8, Math.round((item.completion_event_steps / maxVal) * 110));
                return `
                    <div class="chart-col">
                        <div class="bar-pair">
                            <div class="bar-seg amber" style="height: ${{retH}}px;" title="Retransmissions: ${{item.retransmissions}}"></div>
                            <div class="bar-seg indigo" style="height: ${{stepH}}px;" title="Completion steps: ${{item.completion_event_steps}}"></div>
                        </div>
                        <span class="bar-label">${{item.protocol}} N${{item.window_size}}</span>
                    </div>
                `;
            }}).join("");
        }}

        function downloadFile(filename, content, mimeType) {{
            const blob = new Blob([content], {{ type: mimeType }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }}

        // Event Listeners
        document.getElementById("btn-start").addEventListener("click", startPlayback);
        document.getElementById("btn-run-all").addEventListener("click", runToCompletion);
        document.getElementById("btn-pause").addEventListener("click", pausePlayback);
        document.getElementById("btn-resume").addEventListener("click", resumePlayback);
        document.getElementById("btn-step").addEventListener("click", stepForward);
        document.getElementById("btn-reset").addEventListener("click", resetPlayback);

        document.getElementById("btn-defaults").addEventListener("click", () => {{
            document.getElementById("cfg-protocol").value = "GBN";
            document.getElementById("cfg-window").value = "3";
            document.getElementById("cfg-total-frames").value = "10";
            document.getElementById("cfg-losses").value = "4, 7";
            document.getElementById("cfg-tx-time").value = "1.0";
            document.getElementById("cfg-prop-delay").value = "2.0";
            document.getElementById("cfg-ack-delay").value = "1.0";
            document.getElementById("cfg-timeout").value = "8.0";
            document.getElementById("speed-slider").value = "1.0";
            document.getElementById("speed-label").textContent = "1.00×";
            playbackSpeed = 1.0;
            resetPlayback();
            updateConfigFromInputs();
        }});

        document.getElementById("speed-slider").addEventListener("input", (e) => {{
            playbackSpeed = Number(e.target.value);
            document.getElementById("speed-label").textContent = `${{playbackSpeed.toFixed(2)}}×`;
            if (isRunning) {{
                resumePlayback();
            }}
        }});

        document.getElementById("cfg-protocol").addEventListener("change", updateConfigFromInputs);
        document.getElementById("cfg-window").addEventListener("change", updateConfigFromInputs);
        document.getElementById("timeline-filter").addEventListener("change", () => {{
            if (activeSimulation) renderTimeline(activeSimulation.events.slice(0, currentStepIndex + 1));
        }});
        document.getElementById("frame-search-input").addEventListener("input", () => {{
            if (activeSimulation) renderTimeline(activeSimulation.events.slice(0, currentStepIndex + 1));
        }});

        document.getElementById("btn-benchmark-run").addEventListener("click", () => {{
            renderBenchmarkTable(BENCHMARK_DATA);
        }});

        document.getElementById("btn-export-json").addEventListener("click", () => {{
            const dataToExport = activeSimulation ? activeSimulation : BENCHMARK_DATA;
            downloadFile("arq-lab-telemetry.json", JSON.stringify(dataToExport, null, 2), "application/json");
        }});

        document.getElementById("btn-export-csv").addEventListener("click", () => {{
            const evs = (activeSimulation ? activeSimulation.events : BENCHMARK_DATA[0].events);
            const header = "sequence,timestamp,event_type,frame,description\\n";
            const rows = evs.map(e => `${{e.sequence}},${{e.timestamp}},${{e.event_type}},${{e.frame || ""}},"${{e.description.replace(/"/g, '""')}}"`).join("\\n");
            downloadFile("arq-event-log.csv", header + rows, "text/csv");
        }});

        // Initial Boot
        updateConfigFromInputs();
        renderFrameTracks(null);
        renderBenchmarkTable(BENCHMARK_DATA);
    </script>
</body>
</html>
"""

components.html(APP_HTML, height=1550, scrolling=True)
