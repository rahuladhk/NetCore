#=======================
#       Core-Program
#=======================
import subprocess
import re

def start_hotspot(ssid, password):

    with open('StartH.ps1', 'r', encoding='utf-8') as file:
        powercommand = file.read()

    powercommand = re.sub(
        r'^\s*\$config\.Ssid\s*=.*$',
        f'$config.Ssid="{ssid}"',
        powercommand,
        flags=re.MULTILINE
    )

    powercommand = re.sub(
        r'^\s*\$config\.Passphrase\s*=.*$',
        f'$config.Passphrase="{password}"',
        powercommand,
        flags=re.MULTILINE
    )

    with open('StartH.ps1', 'w', encoding='utf-8') as file:
        file.write(powercommand)

    result = subprocess.run(
        'StartH.bat',
        capture_output=True,
        text=True,
        shell=True
    )

    print("========== START HOTSPOT OUTPUT ==========")
    print(result.stdout)
    print(result.stderr)
    print("==========================================")

    return result.stdout + result.stderr

def systeminfo():
    result = subprocess.run(
        ['systeminfo'],
        capture_output=True,
        text=True
    )

    return result.stdout

def ipconfig():
    result = subprocess.run(
        ['ipconfig', '/all'],
        capture_output=True,
        text=True
    )

    return result.stdout

def stop_hotspot():
    result = subprocess.run(
        ['StopH.bat'],
        capture_output=True,
        text=True,
        shell=True
    )

    return result.stdout + result.stderr

def driver_details():
    result = subprocess.run(
        ['netsh', 'wlan', 'show', 'driver'],
        capture_output=True,
        text=True
    )

    return result.stdout

def saved_networks():
    net=subprocess.run(['netsh', 'wlan', 'show', 'profiles'], capture_output=True).stdout.decode()
    names=re.findall('All User Profile     : (.*)\r', net)
    result=''
    for ssid in names:
        profiles=subprocess.run(['netsh', 'wlan', 'show', 'profiles', ssid, 'key=clear'], capture_output=True).stdout.decode()
        key=re.findall('Key Content            : (.*)\r', profiles)
        if len(key)>0:
            result+='SSID          : '+ssid+ '\n'
            result+='Password      : '+key[0]+'\n\n'
        else:
            result+="SSID          : "+ssid+'\n'
            result+="Password      : "+"None"+'\n\n'
            
    return result






#========================
#       Server
#========================

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app)


# ==========================================
# START HOTSPOT
# ==========================================

@app.route('/Start-Hotspot', methods=['POST'])
def start_hotspot_route():

    print()
    print("================================", flush=True)
    print("     START-HOTSPOT REQUEST", flush=True)
    print("================================", flush=True)

    try:

        # ------------------------------------------
        # GET JSON DATA
        # ------------------------------------------

        data = request.get_json()

        print("Received data:", data, flush=True)

        if not data:
            print("ERROR: No data received.", flush=True)

            return jsonify({
                "success": False,
                "error": "No data received."
            }), 400


        # ------------------------------------------
        # GET SSID AND PASSWORD
        # ------------------------------------------

        ssid = data.get("ssid")
        password = data.get("password")


        print("SSID:", ssid, flush=True)
        print("Password received:", "YES" if password else "NO", flush=True)


        # ------------------------------------------
        # CHECK SSID
        # ------------------------------------------

        if not ssid:

            print("ERROR: SSID is empty.", flush=True)

            return jsonify({
                "success": False,
                "error": "SSID is required."
            }), 400


        # ------------------------------------------
        # CHECK PASSWORD
        # ------------------------------------------

        if not password:

            print("ERROR: Password is empty.", flush=True)

            return jsonify({
                "success": False,
                "error": "Password is required."
            }), 400


        # ------------------------------------------
        # CHECK PASSWORD LENGTH
        # ------------------------------------------

        if len(password) < 8:

            print("ERROR: Password is too short.", flush=True)

            return jsonify({
                "success": False,
                "error": "Password must be at least 8 characters."
            }), 400


        # ==========================================
        # START HOTSPOT
        # ==========================================

        print()
        print("--------------------------------", flush=True)
        print("CALLING Core.start()", flush=True)
        print("--------------------------------", flush=True)


        result = start_hotspot(ssid, password)


        # ==========================================
        # PRINT RESULT
        # ==========================================

        print()
        print("--------------------------------", flush=True)
        print("CORE.PY RESULT", flush=True)
        print("--------------------------------", flush=True)

        print(result, flush=True)

        print("--------------------------------", flush=True)
        print("HOTSPOT START FINISHED", flush=True)
        print("================================", flush=True)
        print()


        # ==========================================
        # SEND RESULT TO setup.html
        # ==========================================

        return jsonify({
            "success": True,
            "data": result
        })


    except Exception as error:

        print()
        print("================================", flush=True)
        print("       START HOTSPOT ERROR", flush=True)
        print("================================", flush=True)
        print("ERROR:", error, flush=True)
        print("================================", flush=True)
        print()


        return jsonify({
            "success": False,
            "error": str(error)
        }), 500



# ==========================================
# STOP HOTSPOT
# ==========================================

@app.route('/Stop-Hotspot')
def get_stop_hotspot():

    try:

        print("Stopping hotspot...", flush=True)

        result = stop_hotspot()

        print("Stop result:", flush=True)
        print(result, flush=True)

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        print("STOP HOTSPOT ERROR:", error, flush=True)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500



# ==========================================
# DRIVER DETAILS
# ==========================================

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



# ==========================================
# SYSTEM INFO
# ==========================================

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



# ==========================================
# IPCONFIG
# ==========================================

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



# ==========================================
# SAVED NETWORKS
# ==========================================

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



# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':

    print()
    print("================================", flush=True)
    print("          NETCORE SERVER", flush=True)
    print("================================", flush=True)
    print("Server running at:", flush=True)
    print("http://127.0.0.1:5000", flush=True)
    print("================================", flush=True)
    print()


    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False
    )
