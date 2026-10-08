import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    rm = pyvisa.ResourceManager()
    resultados_am = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))
        
        fc = 1e9
        fm = 1e3
        amp_c = -10.0   # dBm
        
        generador.set_frecuencia(fc)
        generador.set_amplitud(amp_c)
        generador.set_rf_output("ON")
        generador.set_am_freq(fm)
        generador.set_am_state("ON")
        generador.set_mod_output("ON")
        
        analizador.set_freq_center(fc)
        analizador.set_span(10e3)       
        analizador.set_referencelevel(0)
        analizador.set_atenuator(10)
        analizador.set_rbw(100)         
        
        indices_prueba = [30.0, 50.0, 80.0]

        N = 20
        ST = analizador.get_sweep_time

        for m_set in indices_prueba:
            generador.set_am_depth(m_set)
            time.sleep(ST)

            for medicion in range(1, N+1):
                analizador.peaksearch(1)
                p_carrier = float(analizador.get_marker(1)[0])
                
                # Banda Lateral Superior
                analizador.set_marker_freq(2, fc + fm)

                p_sideband = float(analizador.get_marker(2)[0])
                
                # (m = 2 * 10^(-DeltaP / 20))
                delta_p = p_carrier - p_sideband
                m_calculado = 2 * (10 ** (-delta_p / 20)) * 100
                
                error_m = m_calculado - m_set
                
                print(f"Set: {m_set}% | medicion:{medicion}/{N} | Delta P: {delta_p:.2f} dB | Medido: {m_calculado:.2f}%")
                resultados_am.append([m_set, medicion, p_carrier, p_sideband, delta_p, m_calculado, error_m])

    except pyvisa.Error as e:
        print(f"Error de conexión VISA: {e}")
    finally:
        if 'generador' in locals():
            generador.set_am_state("OFF")
            generador.set_mod_output("OFF")
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): analizador.close()
        rm.close()

    if resultados_am:
        columnas = ["AM Depth Setting (%)", "Measurement", "Carrier Power (dBm)", "Sideband Power (dBm)", "Delta P (dB)", "Measured AM Depth (%)", "Error (%)"]
        df = pd.DataFrame(resultados_am, columns=columnas)
        df.to_csv("test_am.csv", index=False)
        print("\n--- Reporte Guardado: Generado AM---")

if __name__ == "__main__":
    main()