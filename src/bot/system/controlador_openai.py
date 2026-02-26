from email.mime import message
import logging
from openai import AsyncOpenAI
import httpx
from bot.utils.sqlite_manager import save_message, load_history

class OpenAIManager:
    global logger
    logger = logging.getLogger(__name__)
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = {
        "role": "system",
        "content": (
            "Tu nombre es Lala. "
            "Nunca digas otro nombre. "
            "Si te preguntan quién eres respondes: Soy Lala. "
            "Respuestas cortas."
        )
    }

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
    
    async def chat(self, user_id, message):

        if not hasattr(self, "client"):
            await self.connect()

        history = load_history(user_id, limit=6)

        messages = [SYSTEM_PROMPT] + history + [
            {"role": "user", "content": message}
        ]

        response = await self.client.chat.completions.create(
            model=self.config["model"],
            messages=messages,
            max_tokens=120,
            extra_body={
                "keep_alive": -1,
                "options": {
                    "num_ctx": 1024,
                    "num_predict": 80,
                    "temperature": 0.6,
                    "top_p": 0.9
                }
            }
        )

        answer = response.choices[0].message.content

        # guardar memoria
        save_message(user_id, "user", message)
        save_message(user_id, "assistant", answer)

        return answer