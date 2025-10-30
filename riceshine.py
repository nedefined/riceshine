#!/usr/bin/env python
import psutil
import socket
import time
import argparse
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.align import Align
from rich.text import Text
import toml
import os

console = Console()

def get_config_dir():
    config_dir = Path.home() / ".config" / "riceshine"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_config():
    config_dir = get_config_dir()
    config_path = config_dir / "config.toml"
    
    default_config = {
        "colors": {
            "ascii_art": "bold magenta",
            "title": "bold blue",
            "memory": "bold cyan",
            "disk": "bold cyan",
            "temp": "bold cyan",
            "ip": "bold green",
            "tcp": "bold green",
            "value": "white"
        },
        "display": {
            "date_format": "%a %d %b %Y | %H:%M:%S",
            "show_uptime": True,
            "show_load": True,
            "show_memory": True,
            "show_disk": True,
            "show_temp": True,
            "show_ip": True,
            "show_tcp": True,
            "expand_ascii": False
        },
        "paths": {
            "ascii_art": str(config_dir / "ascii.txt")
        }
    }
    
    if config_path.exists():
        with open(config_path, "r") as f:
            return toml.load(f)
    else:
        with open(config_path, "w") as f:
            toml.dump(default_config, f)
        return default_config

def get_default_ascii():
    return r"""
⣠⣤⣤⡤⠤⢤⣤⣀⡀⠀⠐⠒⡄⠀⡠⠒⠀⠀⢀⣀⣤⠤⠤⣤⣤⣤⡄
⠈⠻⣿⡤⠤⡏⠀⠉⠙⠲⣄⠀⢰⢠⠃⢀⡤⠞⠋⠉⠈⢹⠤⢼⣿⠏⠀
⠀⠀⠘⣿⡅⠓⢒⡤⠤⠀⡈⠱⣄⣼⡴⠋⡀⠀⠤⢤⡒⠓⢬⣿⠃⠀⠀
⠀⠀⠀⠹⣿⣯⣐⢷⣀⣀⢤⡥⢾⣿⠷⢥⠤⣀⣀⣞⣢⣽⡿⠃⠀⠀⠀
⠀⠀⠀⠀⠈⢙⣿⠝⠀⢁⠔⡨⡺⡿⡕⢔⠀⡈⠐⠹⣟⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢼⣟⢦⢶⢅⠜⢰⠃⠀⢹⡌⢢⣸⠦⠴⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⣿⣇⡬⡌⢀⡟⠀⠀⠀⢷⠀⣧⢧⣵⣿⠂⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢻⠛⠋⠉⠀⠀⠀⠀⠈⠉⠙⢻⡏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠄⠀⠀⠀⠀⠀⠀
"""

def expand_ascii_art(art_string: str) -> str:
    return " ".join(art_string)

def load_ascii_art(ascii_path, expand_ascii=True):
    if ascii_path.exists():
        art_content = ascii_path.read_text()
    else:
        art_content = get_default_ascii()
        ascii_path.write_text(art_content)
    if expand_ascii:
        return expand_ascii_art(art_content)
    else:
        return art_content

def notmain():
    parser = argparse.ArgumentParser(description='The first (not sure) fetch with centred display of system information written in Python + rich library')
    parser.add_argument('--settings', action='store_true', help='open settings file')
    args = parser.parse_args()

    config_dir = get_config_dir()
    config_path = config_dir / "config.toml"
    
    if args.settings:
        console.print(f"opening settings file: {config_path}")
        try:
            import subprocess
            subprocess.run([os.environ.get('EDITOR', 'nano'), config_path])
        except Exception as e:
            console.print(f"error opening editor: {e}")
        return

    config = load_config()
    colors = config["colors"]
    display = config["display"]
    paths = config["paths"]

    ascii_path = Path(paths["ascii_art"]).expanduser()
    ascii_art = load_ascii_art(ascii_path, display.get("expand_ascii", True))

    now = datetime.now().strftime(display["date_format"])

    uptime_s = time.time() - psutil.boot_time()
    d, r = divmod(uptime_s, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    uptime_str = f"up {int(d)} days, {int(h)} hours, {int(m)} minutes"

    load = psutil.getloadavg()
    load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"

    mem = psutil.virtual_memory()
    mem_str = f"{mem.used // (1024**2)}Mi/{mem.total / (1024**3):.1f}Gi"

    disk = psutil.disk_usage('/')
    disk_str = f"{disk.used // (1024**3)}G/{disk.total // (1024**3)}G"

    cpu_temp_str = "N/A"
    if display["show_temp"]:
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_temp_str = f"+{temps['coretemp'][0].current:.1f}°C"
            elif temps:
                key = list(temps.keys())[0]
                cpu_temp_str = f"+{temps[key][0].current:.1f}°C"
        except Exception:
            pass

    ip_str = "N/A"
    if display["show_ip"]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip_str = s.getsockname()[0]
        except Exception:
            pass

    tcp_conns = len(psutil.net_connections(kind='tcp')) if display["show_tcp"] else 0

    output = Text(justify="center")
    output.append(ascii_art, style=colors["ascii_art"])
    output.append("\n\n")
    
    output.append(f"Date: ", style=colors["title"])
    output.append(f"{now}\n", style=colors["value"])
    
    if display["show_uptime"]:
        output.append(f"Uptime: ", style=colors["title"])
        output.append(f"{uptime_str}\n", style=colors["value"])
    
    if display["show_load"]:
        output.append(f"Load Avg: ", style=colors["title"])
        output.append(f"{load_str}\n", style=colors["value"])
    
    if display["show_memory"]:
        output.append(f"MEM: ", style=colors["memory"])
        output.append(f"{mem_str}   ", style=colors["value"])
    
    if display["show_disk"]:
        output.append(f"DISK: ", style=colors["disk"])
        output.append(f"{disk_str}   ", style=colors["value"])
    
    if display["show_temp"]:
        output.append(f"CPU Temp: ", style=colors["temp"])
        output.append(f"{cpu_temp_str}\n", style=colors["value"])
    
    if display["show_ip"]:
        output.append(f"Local IP: ", style=colors["ip"])
        output.append(f"{ip_str}   ", style=colors["value"])
    
    if display["show_tcp"]:
        output.append(f"TCP-connection: ", style=colors["tcp"])
        output.append(f"{tcp_conns}", style=colors["value"])

    console.print(Align.center(output))

if __name__ == "__main__":
    notmain()