import unittest
import pandas as pd
from services.kpis import calcular_kpis
from services.analysis_service import estimar_analise

class AuditoriaIndicadoresTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([{"data":"2026-11-12","ponto_coleta":"A","categoria":"SMARTPHONE","massa_kg":2.0,"destino":" Reuso "}])

    def test_normaliza_destino(self):
        self.assertEqual(calcular_kpis(self.df).massa_reuso_kg, 2.0)

    def test_rejeita_massa_ausente(self):
        df = self.df.copy()
        df.loc[0, "massa_kg"] = float("nan")
        with self.assertRaises(ValueError):
            calcular_kpis(df)

    def test_rejeita_coluna_ausente(self):
        with self.assertRaises(ValueError):
            calcular_kpis(self.df.drop(columns=["destino"]))

    def test_rejeita_massa_infinita_analise(self):
        with self.assertRaises(ValueError):
            estimar_analise("phone", float("inf"))

if __name__ == "__main__":
    unittest.main()
