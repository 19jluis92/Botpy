![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![License](https://img.shields.io/badge/License-Academic%20%26%20Research%20Only-red)
![RaspberryPi](https://img.shields.io/badge/Raspberry%20Pi-Compatible-C51A4A?logo=raspberrypi)

# Lala-Bot

Bot de Telegram modular que controla **Roku TV**, **Ngrok**, **Docker**, **Melate**, y ahora incluye un **sistema avanzado de videovigilancia con cámaras TP-Link Tapo**, usando **detección inteligente de personas y animales (YOLOv8)**.

---

## 🆕 Novedades (Módulo Tapo)

* 📷 Conexión a cámaras Tapo vía **RTSP**
* 🧠 Detección por **IA (YOLOv8)**: personas, perros, gatos, etc.
* 🚫 Eliminación de falsas alarmas (objetos estáticos como autos)
* 🎯 Soporte de **ROI (Región de interés)**
* 🔕 Habilitar / deshabilitar notificaciones desde el bot
* 🧹 Limpieza automática de capturas por cámara

---

## 📁 Estructura del Proyecto

```
src/
 └── bot/
      ├── handlers/
      │     ├── roku_handlers.py
      │     ├── ngrok_handlers.py
      │     ├── docker_handlers.py
      │     ├── melate_handlers.py
      │     └── tapo_handlers.py        # 📷 NUEVO
      │
      ├── system/
      │     ├── controlador_roku.py
      │     ├── controlador_ngrok.py
      │     ├── controlador_docker.py
      │     ├── controlador_melate.py
      │     ├── controlador_tapo.py     # 📷 NUEVO
      │     ├── tapo_manager.py          # 📷 NUEVO
      │     └── tapo_object_detector.py  # 🤖 YOLO
      │
      ├── utils/
      │     ├── user_auth.py
      │     └── __init__.py
      │
      ├── config/
      │     ├── allowed_users.json
      │     ├── tapo_cameras.json        # 📷 NUEVO
      │     └── __init__.py
      │
      ├── main.py
      └── __init__.py
```

---

## ⚙️ Requisitos

* Python 3.10+
* Docker (opcional)
* Ngrok (opcional)
* Cámara(s) TP-Link Tapo con RTSP habilitado
* Raspberry Pi / Linux recomendado

---

## 📦 Instalación

```bash
pip install python-telegram-bot==20.7
pip install python-dotenv
pip install rokuecp
pip install sklearn ---- pip install scikit-learn 
pip install pandas
pip install jproperties
pip install requests
pip install docker
pip install psutil
pip install ultralytics opencv-python numpy
pip install openai
```

---

## 🔐 Archivo `.env`

Ubicación:

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

Archivo:

```
src/bot/config/allowed_users.json
```

```json
{
  "allowed_usernames": [
    "LuisVE",
    "otro_usuario"
  ]
}
```

---

## 📷 Módulo Cámaras Tapo (Videovigilancia)

### 📄 Archivo de configuración

```
src/bot/config/tapo_cameras.json
```

### 🧾 Ejemplo completo

```json
{
  "cameras": [
    {
      "name": "Entrada",
      "rtsp": "rtsp://usuario:password@IP:554/stream1",
      "area": 8000,
      "roi": [100, 50, 400, 250]
    },
    {
      "name": "Patio",
      "rtsp": "rtsp://usuario:password@IP:554/stream1",
      "area": 8000,
      "roi": null
    }
  ]
}
```

### 🔎 Campos

| Campo  | Tipo       | Descripción                      |
| ------ | ---------- | -------------------------------- |
| `name` | string     | Nombre lógico de la cámara       |
| `rtsp` | string     | URL RTSP de la cámara            |
| `area` | int        | Área mínima (legacy, opcional)   |
| `roi`  | array/null | `[x, y, w, h]` región a analizar |

---

## 🤖 Detección Inteligente

* Motor: **YOLOv8 (Ultralytics)**
* Clases comunes:

  * `person`
  * `dog`
  * `cat`
* Objetos estáticos se **bloquean automáticamente**
* No re-alerta por el mismo objeto

---

## 🎮 Comandos del Bot (Tapo)

| Comando             | Descripción                 |
| ------------------- | --------------------------- |
| `/tapo_on`          | Habilitar notificaciones    |
| `/tapo_off`         | Deshabilitar notificaciones |
| `/snapshot entrada` | Captura inmediata           |

---

## ▶️ Ejecutar el bot

```bash
python src/bot/main.py
```

---

## 🔁 Reiniciar servicio (systemd)

```bash
sudo systemctl daemon-reload
sudo systemctl restart lalabot.service
sudo systemctl status lalabot.service
```

---

## 🧩 Extender el bot

Cada módulo sigue:

* `handlers/` → Telegram
* `system/` → lógica
* `config/` → JSON
* `utils/` → helpers

---

## 📜 Licencia

📜 LICENCIA – USO ACADÉMICO / INVESTIGACIÓN (NO COMERCIAL)
Lala-Bot Academic & Research License (Non-Commercial)

Copyright (c) 2026 Luis Velázquez Escobar

Se concede permiso para usar, copiar, modificar y distribuir este software únicamente bajo las siguientes condiciones:

✅ PERMITIDO

Este software puede ser utilizado solo para:

Fines académicos

Investigación

Aprendizaje personal

Proyectos educativos

Pruebas técnicas no comerciales

🚫 PROHIBIDO

Queda estrictamente prohibido:

Uso comercial directo o indirecto

Venta del software o de derivados

Inclusión en productos o servicios pagos

Uso en sistemas de vigilancia comercial, SaaS o soluciones empresariales

Monetización mediante suscripciones, licencias, anuncios o servicios

📩 USO COMERCIAL / OTROS USOS

Cualquier uso fuera del ámbito académico o de investigación requiere autorización expresa y por escrito del autor.

Para solicitar permiso, contactar a:

📧 [jluis.ingcom@gmail.com]
📨 GitHub: https://github.com/19jluis92

⚠️ SIN GARANTÍA

Este software se proporciona “TAL CUAL”, sin garantía de ningún tipo, expresa o implícita, incluyendo pero no limitado a:

Funcionamiento continuo

Precisión de detecciones

Adecuación para un propósito específico

El autor no será responsable por daños, pérdidas o consecuencias derivadas del uso del software.

📌 OBLIGACIÓN DE ATRIBUCIÓN

Toda redistribución o modificación debe:

Mantener esta licencia

Reconocer al autor original

Incluir un enlace al repositorio original