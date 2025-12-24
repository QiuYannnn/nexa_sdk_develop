#!/usr/bin/env python3
"""
Launcher for Script Hub and Conversion Hub GUI Applications
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_customtkinter():
    """Check if customtkinter is installed"""
    try:
        import customtkinter
        return True
    except ImportError:
        return False

def show_menu():
    """Show application menu"""
    print("=" * 50)
    print("  GUI Applications Launcher")
    print("=" * 50)
    print()
    print("  1. Script Hub")
    print("     Central launcher for PowerShell, Batch,")
    print("     and Python scripts")
    print()
    print("  2. Conversion & Data Cleaning Hub")
    print("     Document conversion and data cleaning tools")
    print()
    print("  3. Exit")
    print()
    print("=" * 50)

def main():
    if not check_customtkinter():
        print("CustomTkinter is not installed.")
        print("Install with: pip install customtkinter")
        print("\nFor full functionality, install all dependencies:")
        print("  pip install -r requirements_gui_apps.txt")
        sys.exit(1)

    while True:
        show_menu()
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            print("\nLaunching Script Hub...")
            from script_hub import main as script_hub_main
            script_hub_main()
            break
        elif choice == "2":
            print("\nLaunching Conversion Hub...")
            from conversion_hub import main as conversion_hub_main
            conversion_hub_main()
            break
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("\nInvalid option. Please enter 1, 2, or 3.\n")

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['script', 'scripts', 'hub', '1']:
            if check_customtkinter():
                from script_hub import main as script_hub_main
                script_hub_main()
            else:
                print("CustomTkinter required. Install: pip install customtkinter")
        elif arg in ['convert', 'conversion', 'clean', '2']:
            if check_customtkinter():
                from conversion_hub import main as conversion_hub_main
                conversion_hub_main()
            else:
                print("CustomTkinter required. Install: pip install customtkinter")
        else:
            print(f"Unknown option: {arg}")
            print("Usage: python launch_gui_apps.py [script|convert]")
    else:
        main()
