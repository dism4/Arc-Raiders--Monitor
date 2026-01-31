import requests
import time
from datetime import datetime, timezone, timedelta
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

# --- KONFIGURATION ---
API_URL = "https://metaforge.app/api/arc-raiders/events-schedule"
# Vi sätter svensk tidszon (UTC+1)
SWEDISH_TZ = timezone(timedelta(hours=1))

# --- FÄRGKARTA ---
EVENT_COLORS = {
    "Prospecting Probes": "grey37",
    "Electromagnetic Storm": "grey53",
    "Husk Graveyard": "grey70",
    "Lush Blooms": "grey85",
    "Hidden Bunker": "white",
    "Locked Gate": "grey100",
    "Night Raid": "orange1",
    "Harvester": "dark_orange",
    "Matriarch": "orange_red1",
    "Launch Tower Loot": "red3"
}

console = Console()

def get_color(name):
    """Returnerar rätt färg baserat på eventets namn."""
    return EVENT_COLORS.get(name, "grey62")

def generate_table():
    """Hämtar data och bygger den visuella tabellen."""
    # Skapar en tabell som fyller hela bredden (expand=True)
    table = Table(
        title="[bold cyan]A R C  M O N I T O R[/][dim] │ PYTHON EDITION[/]",
        box=box.SIMPLE_HEAD,
        expand=True,
        show_header=False,
        caption_justify="left"
    )
    
    # Kolumn 1: Event-namn | Kolumn 2: Tid/Status (högerställd)
    table.add_column("Event Info", ratio=3)
    table.add_column("Status/Time", justify="right", ratio=1)

    try:
        # Sätt en User-Agent för att vara schysst mot API:et
        headers = {'User-Agent': 'Python-Monitor-Client'}
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json().get('data', [])
        now_ts = datetime.now(timezone.utc).timestamp() * 1000
        
        # Sortera händelserna kronologiskt
        data.sort(key=lambda x: x['startTime'])
        
        # --- SEKTION: AKTIVA EVENTS ---
        table.add_row("[bold green]LIVE STATUS[/]", "")
        active_found = False
        
        for event in data:
            if event['startTime'] <= now_ts <= event['endTime']:
                color = get_color(event['name'])
                mins_left = int((event['endTime'] - now_ts) / 1000 / 60)
                
                # Lägg till rad med färg och padding via tabell-systemet
                table.add_row(
                    f"[{color}]● {event['name'].upper()} - {event['map']}[/]",
                    f"[{color}]ACTIVE │ {mins_left}m left[/]"
                )
                active_found = True
        
        if not active_found:
            table.add_row("[dim]    Inga aktiva händelser just nu.[/]", "")

        table.add_section() # En liten horisontell linje
        
        # --- SEKTION: KOMMANDE EVENTS (Full lista) ---
        table.add_row("[grey50]FULL UPCOMING SEQUENCE[/]", "")
        now_local = datetime.now(SWEDISH_TZ)
        today_day = now_local.day
        
        for event in data:
            if event['startTime'] > now_ts:
                color = get_color(event['name'])
                start_dt = datetime.fromtimestamp(event['startTime'] / 1000, tz=SWEDISH_TZ)
                
                # Om eventet är en annan dag, visa datumet
                if start_dt.day != today_day:
                    time_display = start_dt.strftime("%d/%m %H:%M")
                else:
                    time_display = start_dt.strftime("      %H:%M")
                
                table.add_row(
                    f"[{color}]{event['name']} - {event['map']}[/]",
                    f"[{color}]{time_display}[/]"
                )

        # Footer med klockslag för senaste scanningen
        scan_time = now_local.strftime("%H:%M:%S")
        table.caption = f"[dim]LAST SCAN: {scan_time} │ Scroll up to see full history[/]"
        
    except Exception as e:
        table.add_row(f"[red]Error fetching data: {e}[/]", "")

    return table

def main():
    # Live-läge: auto_refresh=False gör att den bara ritar om när vi säger till
    with Live(generate_table(), auto_refresh=False, screen=False) as live:
        while True:
            # Uppdatera tabellen och tvinga en omditning (refresh=True)
            live.update(generate_table(), refresh=True)
            
            # Vänta 30 sekunder innan nästa API-anrop
            time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold orange_red1]>> MONITOR DEACTIVATED.[/]")
