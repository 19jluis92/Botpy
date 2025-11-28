import os
import requests

class NgrokController:

    def __init__(self):
        self.api_key = os.getenv("NGROK_API_KEY")
        self.base_url = "https://api.ngrok.com"

        if not self.api_key:
            raise RuntimeError("⚠️ NGROK_API_KEY no está definido en el entorno.")

        # Headers requeridos por ngrok API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Ngrok-Version": "2"
        }

    # Obtener todos los túneles activos
    def list_tunnels(self):
        url = f"{self.base_url}/tunnels"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    # Obtener solo los public_url
    def get_public_urls(self):
        tunnels = self.list_tunnels().get("tunnels", [])
        return [t.get("public_url") for t in tunnels]

    # Información completa de un túnel por ID
    def get_tunnel_info(self, tunnel_id):
        url = f"{self.base_url}/tunnels/{tunnel_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    # Matar un túnel (si aplica)
    def delete_tunnel(self, tunnel_id):
        url = f"{self.base_url}/tunnels/{tunnel_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()
        return True