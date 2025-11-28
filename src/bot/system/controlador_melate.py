from sorteosanalyzed.brainCsv import BrainCSV
import sys, os
from pathlib import Path
from jproperties import Properties

class MelateController:

    global configs

    configs = Properties()

    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parents[2]       # <-- carpeta /src
        CONFIG_FILE = BASE_DIR /"bot"/ "config" / "sorteos.properties"
        
        with open(CONFIG_FILE, 'rb') as read_prop:
            configs.load(read_prop)
        
        self.analyzer = BrainCSV(configs)

    async def get_recommended_number(self):
        recommended_number = self.analyzer.melateAnalyzedPandas()
        return f"El número recomendado para Melate es: {recommended_number}"