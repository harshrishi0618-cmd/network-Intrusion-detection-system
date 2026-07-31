"""
AI-NIDS — AI-Powered Network Intrusion Detection System
========================================================
Entry point.  Run as Administrator so Scapy can capture raw packets.

Usage
-----
  Monitor network traffic (default):
      python main.py

  Monitor on a specific interface:
      python main.py --iface "Ethernet"

  Start the Streamlit dashboard instead:
      python main.py --dashboard

  Show help:
      python main.py --help
"""

import argparse
import subprocess
import sys
import os
import threading

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def run_monitor(iface: str | None = None):
    from scapy.all import sniff
    from live_capture.live_monitor import process_packet, export_flows

    print("[AI-NIDS] Starting live network monitor...")
    print("[AI-NIDS] Press Ctrl+C to stop.\n")

    exporter = threading.Thread(target=export_flows, daemon=True)
    exporter.start()

    kwargs = {"prn": process_packet, "store": False, "filter": "ip"}
    if iface:
        kwargs["iface"] = iface

    try:
        sniff(**kwargs)
    except PermissionError:
        print("[ERROR] Permission denied — please run as Administrator.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[AI-NIDS] Stopped.")


def run_dashboard():
    dashboard_path = os.path.join(PROJECT_ROOT, "dashboard", "app.py")
    print("[AI-NIDS] Launching Streamlit dashboard...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])


def main():
    parser = argparse.ArgumentParser(
        description="AI-NIDS — AI-Powered Network Intrusion Detection System"
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Launch the Streamlit dashboard instead of the monitor",
    )
    parser.add_argument(
        "--iface",
        metavar="INTERFACE",
        default=None,
        help="Network interface to sniff on (e.g. 'Ethernet', 'Wi-Fi'). "
             "Omit to use the default interface.",
    )
    args = parser.parse_args()

    if args.dashboard:
        run_dashboard()
    else:
        run_monitor(iface=args.iface)


if __name__ == "__main__":
    main()
