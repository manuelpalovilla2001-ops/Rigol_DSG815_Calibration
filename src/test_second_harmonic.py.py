import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    amplitudes_prueba = [0, 10] # dBm
    frecuencias_prueba = [10e6, 100e6, 500e6, 1.5e9]

    resultados_shd = []
    rm = pyvisa.ResourceManager()

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))

        analizador.set_span(10e3)
        analizador.set_rbw(30)
        analizador.set_vbw(10)

        generador.set_rf_output("ON")

        for amp in amplitudes_prueba:
            generador.set_amplitud(amp)

            if amp == 0:
                analizador.set_referencelevel(10)
                analizador.set_atenuator(20)
            else:
                analizador.set_referencelevel(20)
                analizador.set_atenuator(30)

            for freq in frecuencias_prueba:
                print(f"\nTest para F0 = {freq/1e6} MHz")

                generador.set_frecuencia(freq)
                time.sleep(4)
                analizador.set_marker_freq(1, freq)
                
                while True:
                    p_fundamental, _ = analizador.get_marker(1)
                    if float(p_fundamental) > -50:  #Revisar piso de ruido
                        break
                    time.sleep(2)

                analizador.peaksearch(1)
                p_fundamental = float(analizador.get_marker(1)[0])

                analizador.set_freq_center(2 * freq)

                while True:
                    p_armonico, _ = analizador.get_marker(1)
                    if float(p_armonico) > -50:  #Revisar piso de ruido
                        break
                    time.sleep(2) 
                
                analizador.peaksearch(1)
                p_armonico = float(analizador.get_marker(1)[0])
                
                distorsion_dbc = p_armonico - p_fundamental
                
                print(f"Fundamental: {p_fundamental:.2f} dBm | 2do Armonico: {p_armonico:.2f} dBm")
                print(f"Distorsion: {distorsion_dbc:.2f} dBc")
                
                resultados_shd.append([amp, freq, distorsion_dbc])

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
        columnas = ["Output Amplitude (dBm)", "Output Frequency (Hz)", "Calculation Result (dBc)"]
        df = pd.DataFrame(resultados_shd, columns=columnas)
        df.to_csv("reporte_second_harmonic.csv", index=False)
        print("\n--- Reporte Guardado: reporte_second_harmonic.csv ---")

if __name__ == "__main__":
    main()





