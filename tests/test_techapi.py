import sys
import types
import unittest
from unittest.mock import patch


if "streamlit" not in sys.modules:
    fake = types.ModuleType("streamlit")
    fake.cache_data = lambda **kwargs: lambda func: func
    sys.modules["streamlit"] = fake
elif not hasattr(sys.modules["streamlit"], "cache_data"):
    sys.modules["streamlit"].cache_data = lambda **kwargs: lambda func: func

from services.techapi_service import _marca, _slug, buscar_techapi


class TechAPITests(unittest.TestCase):
    def test_normalizacao(self):
        self.assertEqual(_slug("Sámšung Galaxy A16"), "samsung-galaxy-a16")
        self.assertEqual(_marca("iPhone 15"), "apple")

    def test_marca_desconhecida_nao_chama_api(self):
        with patch("services.techapi_service._listar_fichas") as listar:
            self.assertFalse(buscar_techapi("Modelo genérico")["encontrado"])
            listar.assert_not_called()

    @patch("services.techapi_service._ficha")
    @patch("services.techapi_service._listar_fichas")
    def test_ficha_nao_verificada_e_identificada(self, listar, ficha):
        listar.return_value = ["2025/galaxy-a16/samsung-galaxy-a16.json"]
        ficha.return_value = {"name": "Samsung Galaxy A16", "verified": False,
                              "weight_g": 200, "battery_mah": 5000}
        resultado = buscar_techapi("Samsung Galaxy A16")
        self.assertTrue(resultado["encontrado"])
        self.assertFalse(resultado["verificado"])
        self.assertEqual(resultado["peso"], 200)


if __name__ == "__main__":
    unittest.main()
