from inst_virtual_lib.instrument import Instrument

class GeneradorRF(Instrument):
    
    def __init__(self, handler):
        super().__init__(handler)

        self.frecuencia = 0.0
        self.amplitud = 0.0
        
    def set_frecuencia(self, hz):
        pass
        
    def set_amplitud(self, dbm):
        pass
        
    def set_rf_output(self, estado):
        pass


class RigolDSG815(GeneradorRF):
    
    def __init__(self, handler):
        super().__init__(handler)
        
    def set_frecuencia(self, hz):
        self.write(f":SOURce:FREQuency {hz}")
        
    def set_amplitud(self, dbm):
        self.write(f":SOURce:LEVel {dbm}")
        
    def set_rf_output(self, estado):
        self.write(f":OUTPut:STATe {estado}")