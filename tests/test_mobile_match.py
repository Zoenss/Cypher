import unittest

from services.hybrid_product_service import _modelo_compativel, _resumo_mobile


class MobileMatchTests(unittest.TestCase):
    def test_m55_nao_aceita_m55s(self):
        self.assertFalse(_modelo_compativel("Samsung M55 5G", {"name": "Galaxy M55s 5G", "manufacturer_name": "Samsung"}))

    def test_m55_aceita_mesmo_modelo(self):
        self.assertTrue(_modelo_compativel("Samsung M55 5G", {"name": "Galaxy M55 5G", "manufacturer_name": "Samsung"}))

    def test_ultra_nao_aceita_regular(self):
        self.assertFalse(_modelo_compativel("Samsung Galaxy S24 Ultra", {"name": "Samsung Galaxy S24"}))

    def test_seleciona_correspondencia_exata_antes_da_pontuacao(self):
        resultado = _resumo_mobile({"encontrado": True, "resultados": {"devices": [
            {"name": "Galaxy M55s 5G", "manufacturer_name": "Samsung", "match_certainty": 99},
            {"name": "Galaxy M55 5G", "manufacturer_name": "Samsung", "match_certainty": 80},
        ]}}, "Samsung M55 5G")
        self.assertEqual(resultado["dados"]["name"], "Galaxy M55 5G")


if __name__ == "__main__":
    unittest.main()
