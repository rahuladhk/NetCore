# ============================================================
# NETCORE LAUNCHER
# ============================================================

import subprocess
import re
import sys
import os


# ============================================================
# BASE DIRECTORY
# ============================================================

# When running normally:
#     BASE_DIR = folder containing NetCore_Launcher.py
#
# When running as EXE:
#     BASE_DIR = folder containing NetCore_Launcher.exe

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)


# ============================================================
# FLASK
# ============================================================

from flask import Flask, jsonify, request
from flask_cors import CORS


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# START HOTSPOT
# ============================================================

def start_hotspot(ssid, password):

    try:

        ps1_file = os.path.join(BASE_DIR, "StartH.ps1")
        bat_file = os.path.join(BASE_DIR, "StartH.bat")

        # ----------------------------------------------------
        # Check files
        # ----------------------------------------------------

        if not os.path.exists(ps1_file):
            return "ERROR: StartH.ps1 not found."

        if not os.path.exists(bat_file):
            return "ERROR: StartH.bat not found."

        # ----------------------------------------------------
        # Read PowerShell file
        # ----------------------------------------------------

        with open(
            ps1_file,
            'r',
            encoding='utf-8'
        ) as file:

            powercommand = file.read()

        # ----------------------------------------------------
        # Replace SSID
        # ----------------------------------------------------

        powercommand = re.sub(
            r'^\s*\$config\.Ssid\s*=.*$',
            f'$config.Ssid="{ssid}"',
            powercommand,
            flags=re.MULTILINE
        )

        # ----------------------------------------------------
        # Replace Password
        # ----------------------------------------------------

        powercommand = re.sub(
            r'^\s*\$config\.Passphrase\s*=.*$',
            f'$config.Passphrase="{password}"',
            powercommand,
            flags=re.MULTILINE
        )

        # ----------------------------------------------------
        # Save PowerShell file
        # ----------------------------------------------------

        with open(
            ps1_file,
            'w',
            encoding='utf-8'
        ) as file:

            file.write(powercommand)

        # ----------------------------------------------------
        # Run BAT
        # ----------------------------------------------------

        result = subprocess.run(
            bat_file,
            capture_output=True,
            text=True,
            shell=True,
            cwd=BASE_DIR
        )

        # ----------------------------------------------------
        # Console output
        # ----------------------------------------------------

        print()
        print("========== START HOTSPOT OUTPUT ==========")
        print(result.stdout)
        print(result.stderr)
        print("==========================================")
        print()

        return result.stdout + result.stderr

    except Exception as error:

        print("START HOTSPOT ERROR:", error)

        return str(error)


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def systeminfo():

    result = subprocess.run(
        ['systeminfo'],
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr


# ============================================================
# IP CONFIGURATION
# ============================================================

def ipconfig():

    result = subprocess.run(
        ['ipconfig', '/all'],
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr


# ============================================================
# STOP HOTSPOT
# ============================================================

def stop_hotspot():

    bat_file = os.path.join(
        BASE_DIR,
        "StopH.bat"
    )

    if not os.path.exists(bat_file):
        return "ERROR: StopH.bat not found."

    result = subprocess.run(
        bat_file,
        capture_output=True,
        text=True,
        shell=True,
        cwd=BASE_DIR
    )

    return result.stdout + result.stderr


# ============================================================
# DRIVER DETAILS
# ============================================================

def driver_details():

    result = subprocess.run(
        [
            'netsh',
            'wlan',
            'show',
            'driver'
        ],
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr


# ============================================================
# SAVED NETWORKS
# ============================================================

def saved_networks():

    result = ''

    # --------------------------------------------------------
    # Get Wi-Fi profiles
    # --------------------------------------------------------

    net = subprocess.run(
        [
            'netsh',
            'wlan',
            'show',
            'profiles'
        ],
        capture_output=True
    ).stdout.decode(
        errors='ignore'
    )

    # --------------------------------------------------------
    # Extract profile names
    # --------------------------------------------------------

    names = re.findall(
        r'All User Profile\s*:\s*(.*)',
        net
    )

    # --------------------------------------------------------
    # Get passwords
    # --------------------------------------------------------

    for ssid in names:

        ssid = ssid.strip()

        profiles = subprocess.run(
            [
                'netsh',
                'wlan',
                'show',
                'profiles',
                ssid,
                'key=clear'
            ],
            capture_output=True
        ).stdout.decode(
            errors='ignore'
        )

        key = re.findall(
            r'Key Content\s*:\s*(.*)',
            profiles
        )

        result += f"SSID          : {ssid}\n"

        if len(key) > 0:

            result += (
                f"Password      : "
                f"{key[0].strip()}\n\n"
            )

        else:

            result += (
                "Password      : None\n\n"
            )

    return result


# ============================================================
# START HOTSPOT ROUTE
# ============================================================

@app.route(
    '/Start-Hotspot',
    methods=['POST']
)
def start_hotspot_route():

    print()
    print("================================")
    print("     START-HOTSPOT REQUEST")
    print("================================")

    try:

        # ----------------------------------------------------
        # Get JSON
        # ----------------------------------------------------

        data = request.get_json()

        print(
            "Received data:",
            data,
            flush=True
        )

        if not data:

            print(
                "ERROR: No data received.",
                flush=True
            )

            return jsonify({
                "success": False,
                "error": "No data received."
            }), 400

        # ----------------------------------------------------
        # Get SSID
        # ----------------------------------------------------

        ssid = data.get("ssid")

        # ----------------------------------------------------
        # Get password
        # ----------------------------------------------------

        password = data.get("password")

        print(
            "SSID:",
            ssid,
            flush=True
        )

        print(
            "Password received:",
            "YES" if password else "NO",
            flush=True
        )

        # ----------------------------------------------------
        # Validate SSID
        # ----------------------------------------------------

        if not ssid:

            return jsonify({
                "success": False,
                "error": "SSID is required."
            }), 400

        # ----------------------------------------------------
        # Validate password
        # ----------------------------------------------------

        if not password:

            return jsonify({
                "success": False,
                "error": "Password is required."
            }), 400

        # ----------------------------------------------------
        # Password length
        # ----------------------------------------------------

        if len(password) < 8:

            return jsonify({
                "success": False,
                "error":
                    "Password must be at least 8 characters."
            }), 400

        # ----------------------------------------------------
        # Start hotspot
        # ----------------------------------------------------

        print()
        print("--------------------------------")
        print("CALLING start_hotspot()")
        print("--------------------------------")

        result = start_hotspot(
            ssid,
            password
        )

        print()
        print("--------------------------------")
        print("HOTSPOT RESULT")
        print("--------------------------------")

        print(
            result,
            flush=True
        )

        print("--------------------------------")
        print("HOTSPOT START FINISHED")
        print("================================")
        print()

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        print()
        print("================================")
        print("       START HOTSPOT ERROR")
        print("================================")

        print(
            "ERROR:",
            error,
            flush=True
        )

        print("================================")
        print()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# STOP HOTSPOT ROUTE
# ============================================================

@app.route('/Stop-Hotspot')
def get_stop_hotspot():

    try:

        print(
            "Stopping hotspot...",
            flush=True
        )

        result = stop_hotspot()

        print(
            "Stop result:",
            flush=True
        )

        print(
            result,
            flush=True
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        print(
            "STOP HOTSPOT ERROR:",
            error,
            flush=True
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# DRIVER DETAILS ROUTE
# ============================================================

@app.route('/driver-details')
def get_driver_details():

    try:

        result = driver_details()

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# SYSTEM INFORMATION ROUTE
# ============================================================

@app.route('/System-info')
def get_systeminfo():

    try:

        result = systeminfo()

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# IPCONFIG ROUTE
# ============================================================

@app.route('/ipconfig')
def get_ipconfig():

    try:

        result = ipconfig()

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# SAVED NETWORKS ROUTE
# ============================================================

@app.route('/saved-networks')
def get_saved_networks():

    try:

        result = saved_networks()

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == '__main__':

    print()
    print("================================")
    print("          NETCORE SERVER")
    print("================================")

    print(
        "NetCore folder:",
        BASE_DIR,
        flush=True
    )

    print(
        "Server running at:",
        flush=True
    )

    print(
        "http://127.0.0.1:5000",
        flush=True
    )

    print("================================")
    print()

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False
    )