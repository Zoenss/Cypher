import unittest
from services.analysis_service import identificar_categoria_por_nome, estimar_analise

class CategoriaSamsungTests(unittest.TestCase):
    def test_samsung_s24(self):
        self.assertEqual(identificar_categoria_por_nome("Samsung S24"), "phone")
        self.assertTrue(estimar_analise("phone", 1800)["materiais"])

    def test_samsung_galaxy_s24_ultra(self):
        self.assertEqual(identificar_categoria_por_nome("Samsung Galaxy S24 Ultra"), "phone")

    def test_samsung_tv_nao_e_celular(self):
        self.assertNotEqual(identificar_categoria_por_nome("Samsung TV 55"), "phone")

if __name__ == "__main__":
    unittest.main()
