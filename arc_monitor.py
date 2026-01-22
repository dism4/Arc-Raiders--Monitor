import time
import requests
from datetime import datetime, timezone, timedelta
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich import box

# --- KONFIGURATION ---
API_URL = "https://metaforge.app/api/arc-raiders/events-schedule"
REFRESH_RATE = 30 
# Vi använder denna endast för visningen av klockan längst ner
SWEDISH_TIME_ZONE = timezone(timedelta(hours=1))

MAJOR_EVENT_NAMES = {
    "Night Raid", "Electromagnetic Storm", "Hidden Bunker", 
    "Locked Gate", "Harvester", "Matriarch", "Launch Tower Loot"
}

def fetch_active_events():
    active_rows = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        json_payload = response.json()
        
        events_list = json_payload.get('data', [])
        
        # VIKTIGT: Vi använder ren UTC här för att matcha API:ets Unix-tid perfekt
        now_ts = datetime.now(timezone.utc).timestamp() 

        for event in events_list:
            s_raw = event.get('startTime')
            e_raw = event.get('endTime')
            
            if s_raw is None or e_raw is None:
                continue

            # Konvertera ms till sekunder
            start_ts = s_raw / 1000
            end_ts = e_raw / 1000

            # Jämför nuvarande UTC-tid med händelsens tider
            if start_ts <= now_ts <= end_ts:
                mins_left = int((end_ts - now_ts) / 60)
                
                e_name = event.get('name', 'Unknown')
                m_name = event.get('map', 'Unknown Map')
                
                category = "major" if e_name in MAJOR_EVENT_NAMES else "minor"
                color = "bold red" if category == "major" else "green"

                active_rows.append(f"[{color}]{e_name} - {m_name}({category}) Ends in {mins_left}m[/{color}]")
                
    except Exception as e:
        return [f"[red]Systemfel: {type(e).__name__}[/red]"]

    return active_rows

def generate_dashboard():
    # Klockan visar din lokala svenska tid (UTC+1)
    local_clock = datetime.now(SWEDISH_TIME_ZONE).strftime('%H:%M:%S')
    
    table = Table(
        title="[bold cyan]ARC RAIDERS REAL-TIME MONITOR[/bold cyan]", 
        box=box.DOUBLE_EDGE,
        caption=f"Refresh: {REFRESH_RATE}s | Local Time: {local_clock}"
    )
    table.add_column("Current Active Missions", justify="left", width=65)
    
    events = fetch_active_events()
    if not events:
        table.add_row("[italic dim]No active events found for the current UTC time.[/]")
    else:
        # Sortera Major händelser först
        events.sort(key=lambda x: "major" not in x)
        for event_str in events:
            table.add_row(event_str)
            
    return table

def main():
    console = Console()
    console.clear()
    
    with Live(generate_dashboard(), console=console, refresh_per_second=1) as live:
        while True:
            live.update(generate_dashboard())
            time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bold yellow]Monitor avslutad.[/bold yellow]")