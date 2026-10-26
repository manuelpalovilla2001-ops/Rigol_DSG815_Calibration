import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    amplitudes_prueba = [0, 10]  # dBm
    frecuencias_prueba = [10000000, 100000000, 500000000]

    span_inicial = 10000
    rbw = 100
    vbw = 100
    N = 20

    resultados_shd = []
    rm = pyvisa.ResourceManager()

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*DSG?*')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*DSA?*')[0]))

        id_generador = generador.INSTR_ID.strip()
        id_analizador = analizador.INSTR_ID.strip()
        print(f"Generador: {id_generador}")
        print(f"Analizador:      {id_analizador}\n")

        analizador.write(":CALCulate:MARKer1:MODE POSition")

        analizador.set_span(span_inicial)
        analizador.set_rbw(rbw)
        analizador.set_vbw(vbw)
        time.sleep(1)

        sweep_time = float(analizador.get_sweep_time()) * 1.2

        generador.set_rf_output("ON")
        time.sleep(sweep_time)

        for amp in amplitudes_prueba:
            generador.set_amplitud(amp)
            
            if amp == 0:
                analizador.set_referencelevel(10)
                analizador.set_atenuator(20)
            else:
                analizador.set_referencelevel(20)
                analizador.set_atenuator(30)
            
            time.sleep(sweep_time)

            for freq in frecuencias_prueba:
                generador.set_frecuencia(freq)
                time.sleep(sweep_time)
                
                print(f"\n--- Medicion con: Amp = {amp} dBm | F0 = {freq/1e6:.1f} MHz ---")

                for n_med in range(1, N + 1):
                    analizador.set_freq_center(freq)
                    time.sleep(sweep_time)

                    analizador.peaksearch(1)
                    time.sleep(1)
                    amp_fund_str, freq_fund_str = analizador.get_marker(1)
                    p_fundamental = float(amp_fund_str)
                    f_fundamental_med = float(freq_fund_str)

                    freq_arm = 2 * freq
                    analizador.set_freq_center(freq_arm)
                    time.sleep(sweep_time)

                    analizador.peaksearch(1)
                    time.sleep(1)
                    amp_arm_str, freq_arm_str = analizador.get_marker(1)
                    p_armonico = float(amp_arm_str)
                    f_armonico_med = float(freq_arm_str)

                    distorsion_dbc = p_armonico - p_fundamental

                    rbw_actual = int(analizador.query(":SENSe:BANDwidth:RESolution?"))
                    vbw_actual = int(analizador.query(":SENSe:BANDwidth:VIDeo?"))
                    span_actual = int(analizador.query(":SENSe:FREQuency:SPAN?"))
                    att_actual = int(analizador.query(":SENSe:POWer:RF:ATTenuation?"))
                    ref_lvl_actual = float(analizador.query(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel?"))

                    print(f"[{n_med:02d}/{N}] Fund: {p_fundamental:.2f} dBm | 2do Arm: {p_armonico:.2f} dBm | SHD: {distorsion_dbc:.2f} dBc")

                    resultados_shd.append([
                        id_generador,
                        id_analizador,
                        n_med,
                        amp,
                        freq,
                        f_fundamental_med,
                        p_fundamental,
                        freq_arm,
                        f_armonico_med,
                        p_armonico,
                        distorsion_dbc,
                        rbw_actual,
                        vbw_actual,
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

    if resultados_shd:
        columnas = [
            "Generador",
            "Instrumento Medicion",
            "N_Medicion",
            "Output Amplitude (dBm)",
            "Output Frequency (Hz)",
            "Measured Fund Freq (Hz)",
            "Fundamental Power (dBm)",
            "Expected 2nd Harm Freq (Hz)",
            "Measured 2nd Harm Freq (Hz)",
            "2nd Harmonic Power (dBm)",
            "Calculation Result (dBc)",
            "RBW (Hz)",
            "VBW (Hz)",
            "SPAN (Hz)",
            "Attenuator (dB)",
            "Reference Level (dBm)"
        ]
        df = pd.DataFrame(resultados_shd, columns=columnas)
        nombre_archivo = "reporte_second_harmonic.csv"
        df.to_csv(nombre_archivo, index=False)
        print(f"\n--- Reporte Guardado: {nombre_archivo} ---")

if __name__ == "__main__":
    main()