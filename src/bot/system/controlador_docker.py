import docker

class DockerController:
    """Controlador para manejar contenedores Docker desde Python."""

    def __init__(self):
        try:
            # Cliente automático (funciona con Docker Desktop, WSL y Linux)
            self.client = docker.from_env()
            self.client.ping()
            print("Docker conectado correctamente.")
        except Exception as e:
            print(f"❌ Error al conectar con Docker: {e}")
            self.client = None

    def is_ready(self):
        return self.client is not None

    # ============================
    #   LISTAR CONTENEDORES
    # ============================
    def list_containers(self, only_running=False):
        if not self.is_ready():
            return "❌ Docker no está disponible."

        containers = self.client.containers.list(all=not only_running)
        result = []

        for c in containers:
            result.append({
                "id": c.short_id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags
            })

        return result

    # ============================
    #   OBTENER LOGS
    # ============================
    def get_logs(self, container_id, tail=100):
        if not self.is_ready():
            return "❌ Docker no está disponible."

        try:
            cont = self.client.containers.get(container_id)
            logs = cont.logs(tail=tail).decode("utf-8", errors="ignore")
            return logs
        except Exception as e:
            return f"❌ Error obteniendo logs: {e}"

    # ============================
    #   INICIAR / DETENER
    # ============================
    def start_container(self, container_id):
        if not self.is_ready():
            return "❌ Docker no está disponible."

        try:
            cont = self.client.containers.get(container_id)
            cont.start()
            return f"▶️ Contenedor {cont.name} iniciado."
        except Exception as e:
            return f"❌ Error al iniciar: {e}"

    def stop_container(self, container_id):
        if not self.is_ready():
            return "❌ Docker no está disponible."

        try:
            cont = self.client.containers.get(container_id)
            cont.stop()
            return f"⛔ Contenedor {cont.name} detenido."
        except Exception as e:
            return f"❌ Error al detener: {e}"

    # ============================
    #   EJECUTAR COMANDO
    # ============================
    def exec_in_container(self, container_id, cmd: str):
        if not self.is_ready():
            return "❌ Docker no está disponible."

        try:
            cont = self.client.containers.get(container_id)
            result = cont.exec_run(cmd)
            return result.output.decode("utf-8")
        except Exception as e:
            return f"❌ Error ejecutando comando: {e}"