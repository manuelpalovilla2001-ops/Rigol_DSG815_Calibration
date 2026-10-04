import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    rm = pyvisa.ResourceManager()
    resultados_pn = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))
        
        frecuencias_prueba = [100e6, 1e9]
        amp_c = 0.0 
        offset = 20e3

        generador.set_amplitud(amp_c)

        analizador.set_referencelevel(0)
        analizador.set_atenuator(10)
        analizador.set_span(50e3)
        analizador.set_rbw(1e3)

        generador.set_rf_output("ON")

        for freq in frecuencias_prueba: 
            generador.set_frecuencia(freq)
            analizador.set_freq_center(freq)
            time.sleep(2)
            
            analizador.peaksearch(1)
            _, f_exacta_str = analizador.get_marker(1)
            f_exacta = float(f_exacta_str)
            analizador.set_freq_center(f_exacta)
            analizador.peaksearch(1)
            time.sleep(0.5)
            
            analizador.set_marker_delta(1)
            analizador.set_marker_freq(1, offset)
            
            analizador.set_marker_noise(1, "NOISe")
            time.sleep(5)
            
            ruido_fase_str, _ = analizador.get_marker(1)
            ruido_fase_dbc_hz = float(ruido_fase_str) # Lo mide en dBc/Hz
            
            analizador.set_marker_noise(1, "OFF")
            
            resultados_pn.append([
                f"{freq / 1e6:.0f} MHz", 
                f"{ruido_fase_dbc_hz:.2f} dBc/Hz", 
            ])

    except pyvisa.Error as e:
        print(f"Error de conexión VISA: {e}")
    finally:
        if 'generador' in locals():
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): 
            try: analizador.set_marker_noise(1, "OFF") 
            except: pass
            analizador.close()
        rm.close()

    if resultados_pn:
        columnas = ["F", "Valor a 20 kHz"]
        df = pd.DataFrame(resultados_pn, columns=columnas)
        df.to_csv("test_phase_noise.csv", index=False)
        print("\n--- Reporte Guardado ---")
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()