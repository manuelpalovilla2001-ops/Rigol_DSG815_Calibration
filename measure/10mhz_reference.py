import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800

def main():
    rm = pyvisa.ResourceManager()
    resultados_ref = []

    try:
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))
        
        print("="*70)
        print("Asegurese de que su generador de referencia este seteado correctamente:")
        print("1. CH1 -> Ref Ext del Analizador de Espectro (10 MHz, +5 dBm)")
        print("2. CH2 -> 10 MHz IN del Generador DSG815 (10 MHz, 0 dBm)")
        print("3. DSG815 '10 MHz OUT' -> RF IN del Analizador de Espectro")
        print("4. Active la referencia externa en el menú de ambos equipos.")
        print("="*70)
        input("Presione ENTER cuando todas las conexiones esten listas...")

        generador.set_rf_output("ON")
        
        fc = 10e6
        analizador.set_referencelevel(0)
        analizador.set_atenuator(10)
        analizador.set_freq_center(fc)
        analizador.set_span(10e3)
        analizador.set_rbw(30e3)
        time.sleep(2)
        
        analizador.peaksearch(1)
        _, f_pico_str = analizador.get_marker(1)
        analizador.set_freq_center(float(f_pico_str))   # Acá supuestamente debería estar en 10MHz
        analizador.set_span(100)
        analizador.set_rbw(10)
        time.sleep(2)
        
        amplitudes_prueba = ["-1.5 dBm", "+1.5 dBm"]
        
        for amp in amplitudes_prueba:
            print("\n" + "-"*50)
            if amp == "-1.5 dBm":
                input(f"Disminuya la amplitud del CH2 a {amp} y presione ENTER...")
            else:
                input("Regrese el AWG CH2 a 0 dBm, luego subalo a +1.5 dBm y presione ENTER...")
            
            time.sleep(3)
            analizador.peaksearch(1)
            _, f_medida_str = analizador.get_marker(1)
            f_medida = float(f_medida_str)
                        
            print(f"Amplitud: {amp} | Frecuencia Medida: {f_medida} Hz")
            
            resultados_ref.append([amp, f_medida])

    except pyvisa.Error as e:
        print(f"Error de conexión VISA: {e}")
    finally:
        if 'generador' in locals():
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): 
            analizador.close()
        rm.close()

    if resultados_ref:
        columnas = ["Amplitud Referencia", "F", "Incertidumbre"]
        df = pd.DataFrame(resultados_ref, columns=columnas)
        df.to_csv("reporte_10mhz_reference.csv", index=False)
        print("\n--- Reporte Guardado ---")
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()