from inst_virtual_lib.instrument import Instrument

class MedidorPotencia(Instrument):
    
    def __init__(self, resource):
        super().__init__(resource)


class AnritsuML2487B(MedidorPotencia):
    def __init__(self, resource):
        super().__init__(resource)
        
    def set_frecuencia(self, hz, sensor='A'):
        # El manual indica que para que el medidor de potencia cambie la frecuencia
        # se debe configurar el Cal Factor Source en FREQ
        self.write(f"SNCFSRC {sensor},FREQ")
        self.write(f"SNCFRQ {sensor},{hz}HZ")
        
    def get_potencia(self, canal=1):
        respuesta = self.query(f"CWO {canal}")
        aux = respuesta.split(",")
        val_str = aux[-1].strip()
        return float(val_str)