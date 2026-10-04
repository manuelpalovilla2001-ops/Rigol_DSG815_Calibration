import pyvisa
import time
import numpy as np
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    rm = pyvisa.ResourceManager()
    resultados = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))

        fc = 1e9
        amp_c = 0.0
        beta = 2.4048

        deltaF = [50e3, 25e3, 100e3]

        generador.set_amplitud(amp_c)
        generador.set_frecuencia(fc)

        analizador.set_referencelevel(0)
        analizador.set_atenuator(10)
        analizador.set_freq_center(fc)
        analizador.set_span(10e3)
        analizador.set_rbw(3e3)
        time.sleep(2)

        generador.set_rf_output("ON")
        time.sleep(2)
        analizador.peaksearch(1)
        
        _, f_exacta_str = analizador.get_marker(1)
        f_exacta = float(f_exacta_str)
        analizador.set_freq_center(f_exacta)

        generador.set_fm_state("ON")
        generador.set_fm_freq(21e3)
        generador.set_mod_output("ON")

        for desvio in deltaF:
            generador.set_fm_deviation(desvio)
            fm_t = desvio / beta
            fm_rango = np.linspace(fm_t * 0.95, fm_t * 1.05, 20)

            analizador.set_freq_center(f_exacta)
            analizador.set_span(100)
            analizador.set_rbw(10)
            analizador.set_marker_freq(1, f_exacta)
            potencia_minima = float('inf')

            for fm_test in fm_rango:
                generador.set_fm_freq(fm_test)
                time.sleep(2)
                
                p_str, _ = analizador.get_marker(1)
                p_val = float(p_str)

                if p_val < potencia_minima:
                    potencia_minima = p_val
                    fm_min = fm_test

            generador.set_fm_freq(fm_min)

            analizador.set_freq_center(f_exacta + fm_min)
            analizador.set_span(2e3) 
            analizador.set_rbw(30)
            time.sleep(3)
            
            analizador.peaksearch(1)
            time.sleep(0.5)
            _, f1_str = analizador.get_marker(1)
            f1 = float(f1_str)

            analizador.set_freq_center(f_exacta + 2 * fm_min)
            time.sleep(3)
            
            analizador.peaksearch(1)
            time.sleep(0.5)
            _, f2_str = analizador.get_marker(1)
            f2 = float(f2_str)

            distancia_f2_f1 = abs(f2 - f1)
            delta_f_med = beta * distancia_f2_f1
            error = delta_f_med - desvio

            resultados.append([
                f"{desvio / 1e3} KHz", 
                f"{distancia_f2_f1 / 1e3:.3f} KHz", 
                f"{delta_f_med / 1e3:.3f} KHz", 
                f"{error / 1e3:.3f} KHz", 
            ])

    except pyvisa.Error as e:
        print(f"Error de conexión VISA: {e}")
    finally:
        if 'generador' in locals():
            generador.set_fm_state("OFF")
            generador.set_mod_output("OFF")
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): 
            analizador.close()
        rm.close()

    if resultados:
        columnas = ["Delta F", "|F2 - F1|", "Delta Fmed", "Error"]
        df = pd.DataFrame(resultados, columns=columnas)
        df.to_csv("test_fm.csv", index=False)
        print("\n--- Reporte Guardado: Generado FM ---")
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()