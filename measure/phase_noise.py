import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    frecuencias_prueba = [100000000, 1000000000]
    amp_c = 0.0        # dBm
    offset = 20000
    
    ref_level = 0      # dBm
    atenuador = 10     # dB
    span = 50000
    rbw = 1000
    N = 20

    rm = pyvisa.ResourceManager()
    resultados_pn = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*DSG?*')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*DSA?*')[0]))

        id_generador = generador.INSTR_ID.strip()
        id_analizador = analizador.INSTR_ID.strip()
        print(f"Generador: {id_generador}")
        print(f"Analizador:      {id_analizador}\n")

        generador.set_amplitud(amp_c)
        generador.set_rf_output("ON")

        analizador.set_referencelevel(ref_level)
        analizador.set_atenuator(atenuador)
        analizador.set_span(span)
        analizador.set_rbw(rbw)
        time.sleep(1)

        sweep_time = float(analizador.get_sweep_time().strip()) * 1.2
        time.sleep(sweep_time)

        for freq in frecuencias_prueba:
            print(f"\n--- F0 = {freq / 1e6:.0f} MHz ---")
            
            analizador.set_marker_noise(1, "OFF")
            analizador.write(":CALCulate:MARKer1:MODE POSition")
            time.sleep(1)

            generador.set_frecuencia(freq)
            analizador.set_freq_center(freq)
            time.sleep(sweep_time)
            
            analizador.peaksearch(1)
            time.sleep(1)
            _, f_exacta_str = analizador.get_marker(1)
            f_exacta = int(float(f_exacta_str))
            
            analizador.set_freq_center(f_exacta)
            time.sleep(sweep_time)
            
            analizador.peaksearch(1)
            time.sleep(1)
            p_carrier_str, _ = analizador.get_marker(1)
            p_carrier = float(p_carrier_str)

            analizador.set_marker_delta(1)
            time.sleep(1)
            analizador.set_marker_freq(1, offset)
            time.sleep(sweep_time)

            for n_med in range(1, N + 1):
                analizador.set_marker_noise(1, "OFF")
                time.sleep(sweep_time)
                delta_crudo_str, offset_med_str = analizador.get_marker(1)
                delta_crudo_dbc = float(delta_crudo_str.strip())
                offset_med = float(offset_med_str.strip())

                analizador.set_marker_noise(1, "ON")
                analizador.set_marker_noise(1, "NOISe")
                time.sleep(sweep_time)
                
                ruido_fase_str, _ = analizador.get_marker(1)
                ruido_fase_dbc_hz = float(ruido_fase_str)

                rbw_actual = int(analizador.query(":SENSe:BANDwidth:RESolution?"))
                vbw_actual = int(analizador.query(":SENSe:BANDwidth:VIDeo?"))
                span_actual = int(analizador.query(":SENSe:FREQuency:SPAN?"))
                att_actual = int(analizador.query(":SENSe:POWer:RF:ATTenuation?"))
                ref_lvl_actual = float(analizador.query(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel?"))

                print(f"[{n_med:02d}/{N}] F0: {freq/1e6:.0f} MHz | Delta(20kHz): {delta_crudo_dbc:.2f} dBc | Phase Noise: {ruido_fase_dbc_hz:.2f} dBc/Hz")

                resultados_pn.append([
                    id_generador,
                    id_analizador,
                    n_med,
                    amp_c,
                    freq,
                    f_exacta,
                    p_carrier,
                    offset_med,
                    delta_crudo_dbc,
                    ruido_fase_dbc_hz,
                    rbw_actual,
                    vbw_actual,
                    span_actual,
                    att_actual,
                    ref_lvl_actual
                ])

            analizador.set_marker_noise(1, "OFF")

    except pyvisa.Error as e:
        print(f"Error de conexion VISA: {e}")
    finally:
        if 'generador' in locals():
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): 
            analizador.set_marker_noise(1, "OFF")
            analizador.write(":CALCulate:MARKer1:MODE POSition")
            analizador.close()
        rm.close()

    if resultados_pn:
        columnas = [
            "Generador",
            "Instrumento Medicion",
            "N_Medicion",
            "Carrier Amplitude Set (dBm)",
            "Nominal Frequency (Hz)",
            "Measured Center Freq (Hz)",
            "Carrier Peak Power (dBm)",
            "Frequency Offset (Hz)",
            "Raw Delta Marker at 20kHz (dBc)",
            "Normalized Phase Noise at 20kHz (dBc/Hz)",
            "RBW (Hz)",
            "VBW (Hz)",
            "SPAN (Hz)",
            "Attenuator (dB)",
            "Reference Level (dBm)"
        ]
        df = pd.DataFrame(resultados_pn, columns=columnas)
        nombre_archivo = "test_phase_noise.csv"
        df.to_csv(nombre_archivo, index=False)
        print(f"\n--- Reporte Guardado: {nombre_archivo} ---")
        print(df[["N_Medicion", "Nominal Frequency (Hz)", "Raw Delta Marker at 20kHz (dBc)", "Normalized Phase Noise at 20kHz (dBc/Hz)", "RBW (Hz)", "SPAN (Hz)"]].to_string(index=False))

if __name__ == "__main__":
    main()