from inst_virtual_lib.instrument import Instrument

class MedidorPotencia(Instrument):
    
    def __init__(self, resource):
        super().__init__(resource)


class AnritsuML2487B(MedidorPotencia):
    #REVISAR
    def __init__(self, resource):
        super().__init__(resource)
        
    def get_potencia(self, canal=1):
        respuesta = self.query(f"CWO {canal}")
        
        partes = respuesta.split(",")
        val_str = partes[-1].strip()
        
        return float(val_str)