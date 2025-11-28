# Lala-Bot

Bot de Telegram modular que controla **Roku TV**, **Ngrok**, **Docker**, y un módulo externo de **Melate**, todo organizado por handlers independientes y controladores desacoplados.

---

## 📁 Estructura del Proyecto

```
src/
 └── bot/
      ├── handlers/
      │     ├── roku_handlers.py
      │     ├── ngrok_handlers.py
      │     ├── docker_handlers.py
      │     └── melate_handlers.py
      │
      ├── system/
      │     ├── controlador_roku.py
      │     ├── controlador_ngrok.py
      │     ├── controlador_docker.py
      │     └── controlador_melate.py
      │
      ├── utils/
      │     ├── user_auth.py
      │     └── __init__.py
      │
      ├── config/
      │     ├── allowed_users.json
      │     └── __init__.py
      │
      ├── main.py
      └── __init__.py
```

---

## ⚙️ Requisitos

- Python 3.10+
- Docker (si usas módulo Docker)
- Ngrok (si usas módulo Ngrok)
- Cuenta en Telegram (para tu bot)
- Dependencias listadas en `requirements.txt`

---

## 📦 Instalación

### 1. Clonar el repositorio

```
git clone https://github.com/tuusuario/Botpy.git
cd Botpy
```

### 2. Crear entorno virtual

```
python -m venv venv
source venv/bin/activate   # Linux
venv\Scripts\activate    # Windows
```

### 3. Instalar requerimientos

```
pip install python-telegram-bot==20.7
pip install python-dotenv
pip install rokuecp
pip install sklearn 
pip install pandas
pip install jproperties
pip install requests
pip install docker
```

---

## 🔐 Archivo `.env`

Debe vivir en:

```
src/.env
```

Contenido:

```
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
NGROK_API_TOKEN=TU_TOKEN_NGROK
```

---

## 🔑 Autorización de usuarios

Este archivo define quién puede usar el bot:

```
src/bot/config/allowed_users.json
```

Ejemplo:

```json
{
  "allowed_usernames": [
    "LuisVE",
    "otro_usuario"
  ]
}
```

---

## 📺 Control de Roku

Funciones disponibles:

- Encender / apagar TV
- Subir / bajar volumen
- Listar apps instaladas
- Abrir una app por ID
- Mostrar información de la TV

Implementación:

- Controlador → `system/controlador_roku.py`
- Handlers → `handlers/roku_handlers.py`

---

## 🐳 Control de Docker

El bot permite:

- Listar contenedores
- Ver estado individual
- Ejecutar comandos
- Reiniciar / detener contenedores

Implementación:

- Controlador → `system/docker_controller.py`
- Handlers → `handlers/docker_handlers.py`

---

## 🌐 Control de Ngrok

Permite consultar:

- Túneles activos
- URLs generadas
- Estado del servicio

Implementación:

- Controlador → `system/controlador_ngrok.py`
- Handlers → `handlers/ngrok_handlers.py`

---

## 🎲 Módulo Melate

Se integra la librería externa:

https://github.com/19jluis92/SorteosAnalyzed

Estructura importada:

```python
from sorteosanalyzed.brainCsv import BrainCSV
```

El bot ejecuta predicciones y análisis directamente desde el controlador.

---

## ▶️ Ejecutar el bot

En la raíz del proyecto:

```
python src/bot/main.py
```

---

## 🧩 Extender el bot

Cada módulo sigue esta estructura:

- `handlers/` → Interfaz con Telegram  
- `system/` → Lógica interna  
- `config/` → Archivos JSON y parámetros  
- `utils/` → utilidades compartidas  

Puedes agregar más módulos siguiendo este formato.

---

## 📜 Licencia

MIT License.
