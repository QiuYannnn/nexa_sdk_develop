#!/usr/bin/env python3
"""
Display comprehensive system information
"""
import platform
import os
import sys
from datetime import datetime

def format_bytes(size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def show_system_info():
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)

    # Basic system info
    print(f"\n{'='*20} SYSTEM {'='*20}")
    print(f"OS:              {platform.system()} {platform.release()}")
    print(f"OS Version:      {platform.version()}")
    print(f"Architecture:    {platform.machine()}")
    print(f"Processor:       {platform.processor()}")
    print(f"Python Version:  {sys.version.split()[0]}")
    print(f"Hostname:        {platform.node()}")

    # Current time
    print(f"\n{'='*20} TIME {'='*20}")
    print(f"Current Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Environment
    print(f"\n{'='*20} ENVIRONMENT {'='*20}")
    print(f"User:            {os.environ.get('USER', os.environ.get('USERNAME', 'Unknown'))}")
    print(f"Home Directory:  {os.path.expanduser('~')}")
    print(f"Working Dir:     {os.getcwd()}")

    # Try to get memory info (platform dependent)
    print(f"\n{'='*20} RESOURCES {'='*20}")

    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"Total Memory:    {format_bytes(mem.total)}")
        print(f"Available:       {format_bytes(mem.available)}")
        print(f"Used:            {format_bytes(mem.used)} ({mem.percent}%)")

        disk = psutil.disk_usage('/')
        print(f"\nDisk Total:      {format_bytes(disk.total)}")
        print(f"Disk Used:       {format_bytes(disk.used)} ({disk.percent}%)")
        print(f"Disk Free:       {format_bytes(disk.free)}")

        print(f"\nCPU Cores:       {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
        print(f"CPU Usage:       {psutil.cpu_percent(interval=1)}%")

    except ImportError:
        print("(Install psutil for detailed resource info: pip install psutil)")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    show_system_info()
