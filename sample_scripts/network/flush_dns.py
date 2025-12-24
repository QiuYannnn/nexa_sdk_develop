#!/usr/bin/env python3
"""
Flush DNS cache (cross-platform)
Requires admin/root privileges on some systems
"""
import subprocess
import platform
import sys

def flush_dns():
    system = platform.system()
    print(f"Operating System: {system}")
    print("Flushing DNS cache...")

    try:
        if system == "Windows":
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")

        elif system == "Darwin":  # macOS
            result = subprocess.run(
                ["sudo", "dscacheutil", "-flushcache"],
                capture_output=True,
                text=True
            )
            subprocess.run(
                ["sudo", "killall", "-HUP", "mDNSResponder"],
                capture_output=True,
                text=True
            )
            print("DNS cache flushed successfully")

        elif system == "Linux":
            # Try systemd-resolve first
            result = subprocess.run(
                ["sudo", "systemd-resolve", "--flush-caches"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Try resolvectl
                result = subprocess.run(
                    ["sudo", "resolvectl", "flush-caches"],
                    capture_output=True,
                    text=True
                )
            if result.returncode == 0:
                print("DNS cache flushed successfully")
            else:
                print("Could not flush DNS cache. Try running as root.")

        else:
            print(f"Unsupported operating system: {system}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    flush_dns()
