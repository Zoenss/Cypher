import sys
import types
import unittest


if "streamlit" not in sys.modules:
    fake = types.ModuleType("streamlit")
    fake.secrets = {}
    sys.modules["streamlit"] = fake

from services.tales_service import gemini_disponivel, resposta_local, responder


class TalesTests(unittest.TestCase):
    def test_orienta_peso(self):
        self.assertIn("gramas", resposta_local("Como informo o peso?"))

    def test_estimada_nao_e_cotacao(self):
        self.assertIn("estimativa", resposta_local("Qual o valor econômico?"))

    def test_fallback_local_sem_chave(self):
        self.assertFalse(gemini_disponivel())
        texto, origem = responder("Como funciona?", usar_gemini=True)
        self.assertEqual(origem, "local")
        self.assertTrue(texto)


if __name__ == "__main__":
    unittest.main()
