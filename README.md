# ARC Raiders Real-Time Event Monitor 📡

##All made with Google Gemini 3 Pro as a test.

A lightweight Python-based terminal dashboard that tracks active events in **ARC Raiders** using the MetaForge API. It provides a real-time, flicker-free overview of ongoing missions, their locations, and time remaining.

## Features
- **Real-Time Updates:** Automatically refreshes every 30 seconds.
- **Intelligent Categorization:** Automatically flags events like `Night Raid`, `Matriarch`, and `Harvester` as **(major)** in bold red.
- **Clean UI:** Built with the `Rich` library for a modern, table-based terminal interface.
- **Timezone Aware:** Uses UTC-timestamps to ensure accurate "time remaining" calculations regardless of local settings.
- **Stable & Robust:** Includes error handling for API timeouts or connectivity issues.

## Installation

### Prerequisites

- Python 3.10 or higher
- `pip` (Python package manager)

### Setup
```bash

cd arc-raiders-monitor
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# project dependencies
pip install requests rich

# Run
python arc_monitor.py
