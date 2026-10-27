import unittest
from unittest.mock import patch

from services.wikidata_service import _corresponde, buscar_modelo_wikidata


class WikidataTests(unittest.TestCase):
    def test_m55s_nao_e_m55(self):
        self.assertFalse(_corresponde("Samsung M55 5G", "Samsung Galaxy M55s 5G"))

    def test_correspondencia_s24_ultra(self):
        self.assertTrue(_corresponde("Samsung Galaxy S24 Ultra", "Samsung Galaxy S24 Ultra"))

    @patch("services.wikidata_service.requests.get")
    def test_identificacao_sem_especificacoes_inventadas(self, get):
        get.return_value.json.return_value = {"search": [
            {"label": "Samsung Galaxy M55s", "id": "Q11"},
            {"label": "Samsung Galaxy M55", "id": "Q22"},
        ]}
        result = buscar_modelo_wikidata("Samsung M55")
        self.assertEqual(result["identificador"], "Q22")
        self.assertFalse(result["ficha_tecnica"])


if __name__ == "__main__":
    unittest.main()
