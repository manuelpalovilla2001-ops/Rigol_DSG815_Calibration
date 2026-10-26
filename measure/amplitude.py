import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    frecuencias_prueba = [103000, 1030000, 50030000, 503000000, 1403000000]
    amplitud_ref = -10.0  # dBm
    
    ref_level = 0         # dBm
    atenuador = 10        # dB
    rbw = 30000
    span = 100000
    N = 20

    resultados = []
    rm = pyvisa.ResourceManager()

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*DSG?*')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*DSA?*')[0]))

        id_generador = generador.INSTR_ID.strip()
        id_analizador = analizador.INSTR_ID.strip()
        print(f"Generador: {id_generador}")
        print(f"Analizador:      {id_analizador}\n")

        analizador.set_referencelevel(ref_level)
        analizador.set_atenuator(atenuador)
        analizador.set_span(span)
        analizador.set_rbw(rbw)
        time.sleep(1)

        generador.set_amplitud(amplitud_ref)
        generador.set_rf_output("ON")
        time.sleep(1)

        sweep_time = float(analizador.get_sweep_time()) * 1.2

        for freq in frecuencias_prueba:
            print(f"--- Midiendo en Frecuencia: {freq} Hz ---")
            time.sleep(sweep_time)
            
            generador.set_frecuencia(freq)
            analizador.set_freq_center(freq)
            time.sleep(sweep_time)

            analizador.peaksearch(1)
            time.sleep(sweep_time)

            _, f_pico_str = analizador.get_marker(1)
            f_pico = float(f_pico_str)
            
            analizador.set_freq_center(f_pico)
            time.sleep(sweep_time)

            for n_med in range(1, N + 1):
                time.sleep(sweep_time)
                
                intentos = 0
                while True:
                    analizador.peaksearch(1)
                    time.sleep(1)
                    amp_str, frec_med_str = analizador.get_marker(1)
                    potencia_med = float(amp_str)
                    frec_med = float(frec_med_str)
                    
                    if potencia_med > -50.0 or intentos >= 10:
                        break
                    intentos += 1
                    time.sleep(1)

                error = potencia_med - amplitud_ref

                rbw_actual = int(analizador.query(":SENSe:BANDwidth:RESolution?"))
                span_actual = int(analizador.query(":SENSe:FREQuency:SPAN?"))
                att_actual = int(analizador.query(":SENSe:POWer:RF:ATTenuation?"))
                ref_lvl_actual = float(analizador.query(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel?"))

                print(f"[{n_med:02d}/{N}] Frec: {freq} Hz | Med: {potencia_med:.2f} dBm | Error: {error:.2f} dB")

                resultados.append([
                    id_generador,
                    id_analizador,
                    n_med,
                    amplitud_ref,
                    freq,
                    frec_med,
                    potencia_med,
                    error,
                    rbw_actual,
                    span_actual,
                    att_actual,
                    ref_lvl_actual
                ])

    except pyvisa.Error as e:
        print(f"Error de conexion VISA: {e}")
    finally:
        if 'generador' in locals():
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): 
            analizador.close()
        rm.close()

    if resultados:
        columnas = [
            "Generador (UUT)",
            "Instrumento Medicion",
            "N_Medicion",
            "Reference Value (dBm)",
            "Output Frequency (Hz)",
            "Measured Frequency (Hz)",
            "Measurement Value (dBm)",
            "Error (dB)",
            "RBW (Hz)",
            "SPAN (Hz)",
            "Attenuator (dB)",
            "Reference Level (dBm)"
        ]
        df = pd.DataFrame(resultados, columns=columnas)
        
        nombre_archivo = "test_amplitud.csv"
        df.to_csv(nombre_archivo, index=False)
        
        print(f"\n--- Reporte Guardado: {nombre_archivo} ---")
        print(df[["N_Medicion", "Output Frequency (Hz)", "Measurement Value (dBm)", "Error (dB)", "RBW (Hz)", "SPAN (Hz)"]].to_string(index=False))

if __name__ == "__main__":
    main()