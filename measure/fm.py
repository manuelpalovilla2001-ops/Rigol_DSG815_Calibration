import pyvisa
import time
import numpy as np
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    fc = 1e9
    amp_c = 0.0
    beta = 2.4048
    deltaF = [50e3, 25e3, 100e3]
    N = 20

    rm = pyvisa.ResourceManager()
    resultados = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))

        id_generador = generador.INSTR_ID.strip()
        id_analizador = analizador.INSTR_ID.strip()
        print(f"Generador: {id_generador}")
        print(f"Analizador:      {id_analizador}\n")

        generador.set_amplitud(amp_c)
        generador.set_frecuencia(fc)
        generador.set_rf_output("ON")
        time.sleep(1)

        analizador.set_referencelevel(0)
        analizador.set_atenuator(10)
        analizador.set_freq_center(fc)
        analizador.set_span(10e3)
        analizador.set_rbw(3e3)
        time.sleep(1)

        sweep_time = float(analizador.get_sweep_time().strip()) * 1.2
        time.sleep(sweep_time)

        analizador.peaksearch(1)
        time.sleep(1)
        _, f_exacta_str = analizador.get_marker(1)
        f_exacta = float(f_exacta_str)
        analizador.set_freq_center(f_exacta)

        analizador.set_span(2e3)
        analizador.set_rbw(300)
        sweep_time = float(analizador.get_sweep_time().strip()) * 1.2
        time.sleep(sweep_time)
        analizador.peaksearch(1)
        time.sleep(1)
        _, f_exacta_str = analizador.get_marker(1)
        f_exacta = float(f_exacta_str)
        analizador.set_freq_center(f_exacta)
        print(f"Frecuencia exacta de portadora: {f_exacta:.1f} Hz")

        generador.set_fm_deviation(deltaF[0])
        generador.set_fm_freq(deltaF[0] / beta)
        generador.set_fm_state("ON")
        generador.set_mod_output("ON")
        time.sleep(1)

        for desvio in deltaF:
            generador.set_fm_deviation(desvio)
            time.sleep(1)

            print(f"\n--- Medicion con: deltaF = {desvio/1e3:.1f} kHz ---")
            fm_t = desvio / beta
            fm_rango = np.linspace(fm_t * 0.95, fm_t * 1.05, 20)
            dif_list = []

            for n_med in range(1, N+1):

                analizador.set_freq_center(f_exacta)
                analizador.set_span(500)
                analizador.set_rbw(100)
                analizador.set_marker_freq(1, f_exacta)
                sweep_time = float(analizador.get_sweep_time().strip()) * 1.2
                time.sleep(sweep_time)

                potencia_minima = float('inf')
                fm_min = fm_t
                idx_min = 0

                for i, fm_test in enumerate(fm_rango):
                    generador.set_fm_freq(fm_test)
                    time.sleep(sweep_time)

                    p_str, _ = analizador.get_marker(1)
                    p_val = float(p_str)

                    if p_val < potencia_minima:
                        potencia_minima = p_val
                        fm_min = fm_test
                        idx_min = i

                if idx_min in (0, len(fm_rango) - 1):
                    print("  AVISO: el minimo cayo en el borde del barrido, el nulo real puede estar fuera de +-5 %")

                generador.set_fm_freq(fm_min)

                analizador.set_freq_center(f_exacta + fm_min)
                analizador.set_span(5e3)
                analizador.set_rbw(300)
                time.sleep(1)
                sweep_time = float(analizador.get_sweep_time().strip()) * 1.2
                time.sleep(sweep_time)
                analizador.peaksearch(1)
                time.sleep(1)
                _, f1_str = analizador.get_marker(1)
                f1 = float(f1_str)

                analizador.set_freq_center(f_exacta + 2 * fm_min)
                time.sleep(sweep_time)
                analizador.peaksearch(1)
                time.sleep(1)
                _, f2_str = analizador.get_marker(1)
                f2 = float(f2_str)

                distancia_f2_f1 = abs(f2 - f1)
                delta_f_med = beta * distancia_f2_f1
                dif_list.append(distancia_f2_f1)

                rbw_actual = int(analizador.query(":SENSe:BANDwidth:RESolution?"))
                vbw_actual = int(analizador.query(":SENSe:BANDwidth:VIDeo?"))
                span_actual = int(analizador.query(":SENSe:FREQuency:SPAN?"))
                att_actual = int(analizador.query(":SENSe:POWer:RF:ATTenuation?"))
                ref_lvl_actual = float(analizador.query(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel?"))

                print(f"deltaF: {desvio/1e3:.0f} kHz | med {n_med}/{N} | fm: {fm_min:.1f} Hz | "
                      f"|F2-F1|: {distancia_f2_f1:.1f} Hz | deltaF med: {delta_f_med/1e3:.3f} kHz")

                resultados.append([
                    id_generador,
                    id_analizador,
                    n_med,
                    desvio,
                    fm_min,
                    f1,
                    f2,
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
            generador.set_fm_state("OFF")
            generador.set_mod_output("OFF")
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
            "Delta F",
            "fm (Hz)",
            "F1",
            "F2",
            "RBW (Hz)",
            "VBW (Hz)",
            "SPAN (Hz)",
            "Attenuator (dB)",
            "Reference Level (dBm)"
        ]
        df = pd.DataFrame(resultados, columns=columnas)
        nombre_archivo = "test_fm.csv"
        df.to_csv(nombre_archivo, index=False)
        print(f"\n--- Reporte Guardado: {nombre_archivo} ---")



if __name__ == "__main__":
    main()
