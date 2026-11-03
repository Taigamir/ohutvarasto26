"""Document to test the contents of exercise"""
import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    """Class used for testing"""
    def setUp(self):
        """Create test space"""
        self.varasto = Varasto(10)

    def test_konstruktori_luo_tyhjan_varaston(self):
        """Test funtionality of empty storage"""
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_konstruktori_asettaa_virheellisen_tilavuuden_nollaksi(self):
        """Test proper reaction on false input"""
        varasto = Varasto(-5)

        self.assertAlmostEqual(varasto.tilavuus, 0)

    def test_konstruktori_asettaa_negatiivisen_alkusaldon_nollaksi(self):
        """Test that it reacts correctly to negatice inputs"""
        varasto = Varasto(10, -1)

        self.assertAlmostEqual(varasto.saldo, 0)

    def test_konstruktori_rajoittaa_alkusaldon_tilavuuteen(self):
        """Test constructor further"""
        varasto = Varasto(10, 15)

        self.assertAlmostEqual(varasto.saldo, 10)

    def test_lisays_lisaa_saldoa(self):
        """Test enter function"""
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        """Test enter function2"""
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_lisays_lisaa_ei_vie_tilavuutta_negatiiviseksi(self):
        """Test enter function3"""
        self.varasto.lisaa_varastoon(11)

        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 0)

    def test_lisays_ei_lisaa_negatiivista_maaraa(self):
        """Test enter function4"""
        self.varasto.lisaa_varastoon(-1)

        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 10)

    def test_ottaminen_ei_ota_negatiivista_maaraa(self):
        """Test take function"""
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(-1)

        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        """Test take function2"""
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        """Test take function3"""
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_ottaminen_ei_ylita_maksimiarvoa(self):
        """Test take function4"""
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(9)

        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 10)
    #this works
    def test_tulos_printtaa_oikein(self):
        """Test prints out correctly"""
        self.varasto.lisaa_varastoon(8)

        self.assertEqual(str(self.varasto), "saldo = 8, vielä tilaa 2")
