import logging
from openai import AsyncOpenAI
import httpx

class OpenAIManager:
    global logger
    logger = logging.getLogger(__name__)

    def __init__(self, ip_config, port_config, api_key, model_config):
        self.config = {
            "ip": ip_config,
            "port": port_config,
            "api_key": api_key,
            "model": model_config
        }
        

    async def connect(self):
        """Conectar a OpenAI usando la configuración."""
        if not self.config.get("api_key"):
            raise ValueError("API key is required to connect to OpenAI.")
        
        self.client =  AsyncOpenAI(
            base_url=f"http://{self.config['ip']}:{self.config['port']}/v1",
            api_key=self.config["api_key"],
            timeout=60,
            max_retries=1,
            http_client=httpx.AsyncClient(
                proxies=None,
                trust_env=False)
        )
    
    async def chat(self, message):
        """Enviar un mensaje al modelo de OpenAI y obtener la respuesta."""
        if not hasattr(self, "client"):
            await self.connect()
        
        response = await self.client.chat.completions.create(
            model=self.config["model"],
            messages=[{"role": "user", "content": message}],
            extra_body={"keep_alive": -1}
        )
        return response.choices[0].message.content