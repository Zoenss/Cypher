import csv
import io
import math
import unittest

from services.economic_service import calcular_valor_material, calcular_valor_economico
from services.export_service import gerar_csv_analise
from services.recovery_scenario_service import simular_recuperacao


class AuditoriaConfiabilidadeTests(unittest.TestCase):
    def test_economia_rejeita_nan_e_infinito(self):
        for massa in (math.nan, math.inf, -math.inf):
            with self.subTest(massa=massa):
                with self.assertRaises(ValueError):
                    calcular_valor_material("Ouro", massa)

    def test_economia_rejeita_percentual_invalido(self):
        with self.assertRaises(ValueError):
            calcular_valor_economico([{
                "material": "Cobre", "massa_estimada_g": 10,
                "percentual_estimado": float("nan"),
            }])

    def test_csv_inclui_cenario_e_mantem_campos_anteriores(self):
        materiais = [{"material": "Cobre", "massa_estimada_g": 100, "percentual_estimado": 100}]
        cenario = simular_recuperacao(materiais, {"Cobre": 0.5}, 1)
        dados = gerar_csv_analise(
            equipamento="Teste", quantidade=1, massa_total_g=100,
            massa_media_g=100, categoria="desktop", fonte_principal="interno",
            fontes_utilizadas=["interno"], materiais=materiais,
            materiais_economicos=[{"material": "Cobre", "massa_estimada_g": 100,
                                    "preco_por_grama": 0.05, "valor_estimado": 5}],
            massa_recuperavel_g=100, percentual_recuperavel=100,
            valor_total_estimado=5, recomendacoes=[],
            cenario_recuperacao=cenario,
        )
        linhas = list(csv.DictReader(io.StringIO(dados.decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["equipamento"], "Teste")
        self.assertEqual(linhas[0]["rendimento_hipotetico_pct"], "50.0")
        self.assertEqual(linhas[0]["saldo_hipotetico_cenario_rs"], "1.5")


if __name__ == "__main__":
    unittest.main()
