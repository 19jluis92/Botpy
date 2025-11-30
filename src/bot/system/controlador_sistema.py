import subprocess
import platform
import psutil
import socket

class SistemaController:

    # =============================
    #   INFO GENERAL DEL SISTEMA
    # =============================
    def get_system_info(self):
        info = {
            "OS": platform.system(),
            "Version": platform.version(),
            "Release": platform.release(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
        }
        return info

    # =============================
    #         CPU / RAM
    # =============================
    def get_usage(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent
        }

    # =============================
    #     TEMPERATURA (Raspberry)
    # =============================
    def get_temperature(self):
        try:
            output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
            temp = output.replace("temp=", "").replace("'C", "").strip()
            return float(temp)
        except:
            return None

    # =============================
    #           IPs
    # =============================
    def get_ip_local(self):
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    def get_ip_public(self):
        try:
            output = subprocess.check_output(["curl", "-s", "https://ifconfig.me"])
            return output.decode().strip()
        except:
            return None

    # =============================
    #      APAGAR / REINICIAR
    # =============================
    def shutdown(self):
        subprocess.Popen(["sudo", "shutdown", "now"])
        return "Apagando el sistema…"

    def reboot(self):
        subprocess.Popen(["sudo", "reboot"])
        return "Reiniciando el sistema…"
