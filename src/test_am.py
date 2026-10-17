import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    fc = 1e9
    fm = 1e3
    amp_c = -10.0   # dBm
    indices_prueba = [30.0, 50.0, 80.0]
    N = 20

    rm = pyvisa.ResourceManager()
    resultados_am = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))

        id_generador = generador.INSTR_ID.strip()
        id_analizador = analizador.INSTR_ID.strip()
        print(f"Generador: {id_generador}")
        print(f"Analizador:      {id_analizador}\n")
        
        generador.set_frecuencia(fc)
        generador.set_amplitud(amp_c)
        generador.set_rf_output("ON")
        time.sleep(1)
        generador.set_am_freq(fm)
        generador.set_am_state("ON")
        generador.set_mod_output("ON")
        time.sleep(1)

        analizador.set_freq_center(fc)
        analizador.set_span(10e3)
        analizador.set_referencelevel(0)
        analizador.set_atenuator(10)
        analizador.set_rbw(100)

        time.sleep(1)

        sweep_time = float(analizador.get_sweep_time().strip()) * 1.2
        time.sleep(sweep_time)

        for m_set in indices_prueba:
            generador.set_am_depth(m_set)
            time.sleep(sweep_time)

            print(f"\n--- Medicion con: m = {m_set} ---")

            for n_med in range(1, N + 1):
                analizador.peaksearch(1)
                time.sleep(1)
                p_carrier = float(analizador.get_marker(1)[0])
                
                # Banda Lateral Superior
                analizador.set_marker_freq(2, fc + fm)

                p_sideband = float(analizador.get_marker(2)[0])
                
                # (m = 2 * 10^(-DeltaP / 20))
                delta_p = p_carrier - p_sideband
                m_calculado = 2 * (10 ** (-delta_p / 20)) * 100
                
                error_m = m_calculado - m_set

                rbw_actual = int(analizador.query(":SENSe:BANDwidth:RESolution?"))
                vbw_actual = int(analizador.query(":SENSe:BANDwidth:VIDeo?"))
                span_actual = int(analizador.query(":SENSe:FREQuency:SPAN?"))
                att_actual = int(analizador.query(":SENSe:POWer:RF:ATTenuation?"))
                ref_lvl_actual = float(analizador.query(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel?"))
                
                print(f"Indice de mod: {m_set}% | medicion:{n_med}/{N} | Delta P: {delta_p:.2f} dB | Indice Medido: {m_calculado:.2f}%")

                resultados_am.append([
                    id_generador,
                    id_analizador,
                    n_med,
                    m_set,
                    delta_p,
                    m_calculado,
                    error_m,
                    rbw_actual,
                    vbw_actual,
                    span_actual,
                    att_actual,
                    ref_lvl_actual
                ])

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
        columnas = [
            "Generador",
            "Instrumento Medicion",
            "N_Medicion",
            "Modulation Depth Set",
            "P_carrier - P_sideband",
            "Measured Modulation Depth",
            "Error",
            "RBW (Hz)",
            "VBW (Hz)",
            "SPAN (Hz)",
            "Attenuator (dB)",
            "Reference Level (dBm)"
        ]
        df = pd.DataFrame(resultados_am, columns=columnas)
        nombre_archivo = "test_am.csv"
        df.to_csv(nombre_archivo, index=False)
        print(f"\n--- Reporte Guardado: {nombre_archivo} ---")

if __name__ == "__main__":
    main()