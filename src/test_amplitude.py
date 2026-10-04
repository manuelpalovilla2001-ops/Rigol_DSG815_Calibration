import pyvisa
import time
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDsa800, AnritsuML2487B

def main():
    frecuencias_prueba = [103000, 1030000, 50030000, 503000000, 1403000000]
    amplitud_ref = -10.0 # dBm
    
    valores_A1 = {}
    resultados = []
    rm = pyvisa.ResourceManager()

    try:
        # IMPORTANTE: Reemplazar con las direcciones USB reales
        generador = RigolDSG815(rm.open_resource(rm.list_resources('?*::DSG?*:INSTR')[0]))
        medidor = AnritsuML2487B(rm.open_resource('GPIB0::...::INSTR'))

        generador.set_amplitud(amplitud_ref) 
        generador.set_rf_output("ON")

        for freq in frecuencias_prueba:
            generador.set_frecuencia(freq)
            medidor.set_frecuencia(freq, sensor='A')
            time.sleep(5)
            potencia_A1 = medidor.get_potencia(canal=1)
            valores_A1[freq] = potencia_A1

        if 'medidor' in locals(): 
                    medidor.close()

        print("\n" + "="*60)
        input("ATENCIÓN: Desconecte el medidor de potencia.\n"
                "Conecte el Generador (RF OUT) al Analizador de Espectro (RF IN).\n"
                "Presione ENTER cuando esté listo para continuar...")
        print("="*60 + "\n")

        analizador = RigolDsa800(rm.open_resource(rm.list_resources('?*::DSA?*:INSTR')[0]))

        analizador.set_span(1e6)          # Span = 1 MHz
        analizador.set_referencelevel(0)  # Ref Level = 0 dBm
        analizador.set_atenuator(10)      # Input Attenuation = 10 dB
        analizador.set_rbw(10e3)          # RBW = 10 kHz

        error_sistema = {}

        for freq in frecuencias_prueba:
            generador.set_frecuencia(freq)
            analizador.set_freq_center(freq)            
            time.sleep(2)
            analizador.set_marker_freq(1,freq)

            while True:
                amp, _ = analizador.get_marker(1)
                if float(amp) > -50:
                    break
                time.sleep(2)

            amp_str, frecuencia_str = analizador.get_marker(1)
            potencia_A2 = float(amp_str)

            es = potencia_A2 - valores_A1[freq]
            error_sistema[freq] = es

        amplitudes_prueba = [-10.0, -80.0]
        analizador.set_span(100)      # Span = 100 Hz
        analizador.set_atenuator(10)  # Input Attenuation = 10 dB
        analizador.set_rbw(10)        # RBW = 10 Hz

        for amp_ref in amplitudes_prueba:
            generador.set_amplitud(amp_ref)

            if amp_ref == -10.0:
                analizador.set_referencelevel(0)
            else:
                analizador.set_referencelevel(-20)

            for freq in frecuencias_prueba:
                generador.set_frecuencia(freq)
                analizador.set_freq_center(freq)
                time.sleep(3)
                
                analizador.peaksearch(1)
                time.sleep(0.5)
                
                amp_str, _ = analizador.get_marker(1)
                potencia_A3 = float(amp_str)
                
                
                error_global = potencia_A3 - amp_ref
                precision_amplitud = abs(error_global - es[freq])
                                
                print(f"Frec: {freq} Hz | Ref: {amp_ref} | A3: {potencia_A3} dBm | "
                      f"Precisión: {precision_amplitud:.3f} dB")
                
                resultados.append([amp_ref, freq, potencia_A3, error_global, precision_amplitud])

    except pyvisa.Error as e:
        print(f"Error de conexion: {e}")

    finally:
        if 'generador' in locals():
            generador.set_rf_output("OFF")
            generador.close()
        rm.close()
        if 'analizador' in locals(): analizador.close()
        rm.close()

    if resultados:
        columnas = ["Reference Value (dBm)", "Output Frequency (Hz)", "Measurement Value A3", "Global Error", "Amplitude Accuracy"]
        df = pd.DataFrame(resultados, columns=columnas)
        
        nombre_archivo = "test_amplitud.csv"
        df.to_csv(nombre_archivo, index=False)
        
        print("\n--- Reporte Guardado: Generado Amplitud---")
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()