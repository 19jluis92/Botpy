import subprocess
import platform
import psutil
import socket
import time

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
    
    # ====================================================
    #      REINICIO DE ADAPTADORES DE RED (WLAN / LAN)
    # ====================================================

    def restart_wifi(self):
        """
        Reinicia la interfaz WiFi (wlan0).
        Compatible con Raspberry Pi / Debian.
        """
        try:
            subprocess.run(["sudo", "ifdown", "wlan0"], check=True)
            subprocess.run(["sudo", "ifup", "wlan0"], check=True)
            return "🔄 WiFi reiniciado correctamente (wlan0)."
        except:
            # fallback para NetworkManager
            try:
                subprocess.run(["sudo", "nmcli", "radio", "wifi", "off"], check=True)
                subprocess.run(["sudo", "nmcli", "radio", "wifi", "on"], check=True)
                return "🔄 WiFi reiniciado usando NetworkManager."
            except Exception as e:
                return f"❌ Error reiniciando WiFi:\n{e}"

    def restart_ethernet(self):
        """
        Reinicia la interfaz Ethernet (eth0).
        Compatible con Raspberry Pi / Debian.
        """
        try:
            subprocess.run(["sudo", "ifdown", "eth0"], check=True)
            subprocess.run(["sudo", "ifup", "eth0"], check=True)
            return "🔄 Ethernet reiniciado correctamente (eth0)."
        except:
            # fallback para NetworkManager
            try:
                subprocess.run(["sudo", "nmcli", "connection", "down", "eth0"], check=True)
                subprocess.run(["sudo", "nmcli", "connection", "up", "eth0"], check=True)
                return "🔄 Ethernet reiniciado usando NetworkManager."
            except Exception as e:
                return f"❌ Error reiniciando Ethernet:\n{e}"

    # =============================
    #   RESET DE ADAPTADORES DE RED
    # =============================
    def reset_interface(self, iface: str, seconds: int = 60):
        """
        Reinicia una interfaz de red por X segundos.
        """
        try:
            # Apagar interfaz
            subprocess.run(["sudo", "ip", "link", "set", iface, "down"], check=True)

            # Esperar el tiempo definido
            time.sleep(seconds)

            # Encender interfaz
            subprocess.run(["sudo", "ip", "link", "set", iface, "up"], check=True)

            return f"🔌 Interfaz {iface} reiniciada correctamente."
        except subprocess.CalledProcessError as e:
            return f"❌ Error al reiniciar la interfaz {iface}: {e}"

    def reset_wifi(self):
        return self.reset_interface("wlan0", seconds=60)

    def reset_lan(self):
        return self.reset_interface("eth0", seconds=60)
