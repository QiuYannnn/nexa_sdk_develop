#!/usr/bin/env python3
"""
Display network information (cross-platform)
"""
import subprocess
import platform
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unable to determine"

def show_network_info():
    system = platform.system()
    print("=" * 50)
    print("NETWORK INFORMATION")
    print("=" * 50)

    print(f"\nHostname: {socket.gethostname()}")
    print(f"Local IP: {get_local_ip()}")

    print("\n--- Network Interfaces ---\n")

    try:
        if system == "Windows":
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True
            )
            print(result.stdout)

        elif system == "Darwin":  # macOS
            result = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True
            )
            print(result.stdout)

        elif system == "Linux":
            # Try ip command first, fall back to ifconfig
            result = subprocess.run(
                ["ip", "addr"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ["ifconfig", "-a"],
                    capture_output=True,
                    text=True
                )
            print(result.stdout)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_network_info()
