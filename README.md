
# Bot de Control Telegram + Roku TV

## Descripción
Este proyecto es un **bot de Telegram** que permite controlar una **Roku TV** conectada en la misma red local.  
El bot usa:

- `python-telegram-bot v20+` (asíncrono)
- `rokuecp` para controlar Roku vía ECP
- `dotenv` para manejar variables de entorno

## Funcionalidades
- Definir la IP de la Roku  
- Encender la TV (Home)  
- Apagar  
- Subir/Bajar volumen  
- Lanzar aplicaciones  
- Menús interactivos con botones  

## Estructura del Proyecto

```
Botpy/
└── src/
    ├── .env
    └── bot/
        ├── system/
        │   ├── __init__.py
        │   └── controlador_roku.py
        └── lala/
            ├── __init__.py
            └── main.py
```

## Requisitos

- Python 3.10+
- pip
- Telegram app
- Roku TV en la misma red local

Dependencias:

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

## Archivo `.env`

El archivo debe estar en `src/.env`:

```
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
```

## Ejecución

```
cd Botpy/src
python -m bot.lala.main
```

## Configuración de la Roku

1. Ambas deben estar en la **misma LAN**
2. Ver la IP en Roku:  
   **Settings → Network → About**
3. En el bot:  
   **Roku → Define IP**

## Notas importantes
- Las Roku **no pueden encenderse por IP** si están completamente apagadas.  
  Sólo funciona si está en modo **Fast TV Start**.
