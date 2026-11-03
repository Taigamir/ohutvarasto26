"""Contains definition for class Varasto"""

class Varasto:
    """Create class varasto"""
    def __init__(self, tilavuus, alku_saldo = 0):
        """Init the class"""
        if tilavuus > 0.0:
            self.tilavuus = tilavuus
        else:
            self.tilavuus = 0.0
        if alku_saldo < 0.0 or alku_saldo <= tilavuus:
            self.saldo = 0
        else:
            self.saldo = tilavuus

    def paljonko_mahtuu(self):
        """calculate max capacity"""
        return self.tilavuus - self.saldo

    #comment to test new github actions

    def lisaa_varastoon(self, maara):
        """Add into class"""
        if maara < 0:
            return
        if maara <= self.paljonko_mahtuu():
            self.saldo = self.saldo + maara
        else:
            self.saldo = self.tilavuus

    def ota_varastosta(self, maara):
        """Take from class"""
        if maara < 0:
            return 0.0
        if maara > self.saldo:
            kaikki_mita_voidaan = self.saldo
            self.saldo = 0.0

            return kaikki_mita_voidaan

        self.saldo = self.saldo - maara

        return maara

    def __str__(self):
        """Format string print"""
        return f"saldo = {self.saldo}, vielä tilaa {self.paljonko_mahtuu()}"
