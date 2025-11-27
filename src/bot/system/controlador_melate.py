from sorteosanalyzed.analizador import MelateAnalyzer

class MelateController:
    def __init__(self):
        self.analyzer = MelateAnalyzer()

    async def get_recommended_number(self):
        recommended_number = self.analyzer.recommend_number()
        return f"El número recomendado para Melate es: {recommended_number}"