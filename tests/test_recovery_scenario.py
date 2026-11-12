import unittest
from services.recovery_scenario_service import simular_recuperacao


class CenariosRecuperacaoTests(unittest.TestCase):
    def setUp(self):
        self.materiais = [
            {"material": "Cobre", "massa_estimada_g": 100},
            {"material": "Outros materiais", "massa_estimada_g": 20},
        ]

    def test_rendimento_parcial(self):
        resultado = simular_recuperacao(self.materiais, {"Cobre": 0.8})
        self.assertEqual(resultado["massa_recuperada_estimada_g"], 80)
        self.assertEqual(resultado["valor_bruto_potencial_rs"], 4.0)

    def test_sem_rendimento_nao_assume_recuperacao(self):
        resultado = simular_recuperacao(self.materiais, {})
        self.assertEqual(resultado["massa_recuperada_estimada_g"], 0)

    def test_custo_e_saldo(self):
        resultado = simular_recuperacao(self.materiais, {"Cobre": 0.5}, 1.0)
        self.assertEqual(resultado["saldo_hipotetico_rs"], 1.5)

    def test_rejeita_rendimento_acima_de_cem(self):
        with self.assertRaises(ValueError):
            simular_recuperacao(self.materiais, {"Cobre": 1.1})

    def test_rejeita_massa_infinita(self):
        with self.assertRaises(ValueError):
            simular_recuperacao([{"material": "Cobre", "massa_estimada_g": float("inf")}], {"Cobre": 0.8})

    def test_rejeita_custo_negativo(self):
        with self.assertRaises(ValueError):
            simular_recuperacao(self.materiais, {"Cobre": 0.8}, -1)


if __name__ == "__main__":
    unittest.main()
