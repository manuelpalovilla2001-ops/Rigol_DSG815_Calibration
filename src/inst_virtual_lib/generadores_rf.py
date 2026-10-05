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
        
    def set_rf_output(self, state):
        pass

    def set_fm_state(self, state):
        pass
        
    def set_fm_deviation(self, hz):
        pass
        
    def set_fm_freq(self, hz):
        pass

    def set_fm_waveform(self, waveform):
        pass

    def set_am_state(self, state):
        pass
        
    def set_am_depth(self, m):
        pass
        
    def set_am_freq(self, hz):
        pass
        
    def set_mod_output(self, state):
        pass

class RigolDSG815(GeneradorRF):
    
    def __init__(self, handler):
        super().__init__(handler)
        
    def set_frecuencia(self, hz):
        self.write(f":SOURce:FREQuency {hz}")
        
    def set_amplitud(self, dbm):
        self.write(f":SOURce:LEVel {dbm}")
        
    def set_rf_output(self, state):
        self.write(f":OUTPut:STATe {state}")        # state: ON or OFF

    def set_fm_state(self, state):
        self.write(f":SOURce:FM:STATe {state}")     # state: ON or OFF

    def set_fm_deviation(self, hz):
        self.write(f":SOURce:FM:DEViation {hz}")

    def set_fm_freq(self, hz):
        self.write(f":SOURce:FM:FREQuency {hz}")

    def set_fm_waveform(self, waveform):
        self.write(f":SOURce:FM:WAVEform {waveform}")   # waveform: SINE or SQUA

    def set_am_state(self, state):
        self.write(f":SOURce:AM:STATe {state}")

    def set_am_depth(self, m):
        self.write(f":SOURce:AM:DEPTh {m}")
        
    def set_am_freq(self, hz):
        self.write(f":SOURce:AM:FREQuency {hz}")
        
    def set_mod_output(self, state):
        self.write(f":OUTPut:MODulation:STATe {state}")