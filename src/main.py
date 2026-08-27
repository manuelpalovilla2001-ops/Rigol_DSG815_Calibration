import pyvisa
import pandas as pd
from inst_virtual_lib import RigolDSG815, RigolDs2202, RigolDsa800

def main():
    # Defino los parámetros exactos según el manual del DSG815
    frecuencias_prueba = [103000, 1030000, 50030000, 503000000, 1403000000]
    amplitud_ref = -10.0 # dBm
    
    resultados = []

    rm = pyvisa.ResourceManager()

    analizador.set_span(100)
    analizador.set_referencelevel(-20)
    analizador.set_rbw(1)

    try:
        # IMPORTANTE: Reemplazar con las direcciones USB reales
        generador = RigolDSG815(rm.open_resource('USB0::...::INSTR'))
        analizador = RigolDsa800(rm.open_resource('USB0::...::INSTR'))
        
        generador.set_amplitud(amplitud_ref) 
        generador.set_rf_output("ON")

        print(f"\n--- Iniciando barrido a {amplitud_ref} dBm ---")
        
        for freq in frecuencias_prueba:
            generador.set_frecuencia(freq)
            analizador.set_freq_center(freq)
            
            analizador.peaksearch(1) 
            
            amplitud_str, frecuencia_str = analizador.get_marker(1)
            amplitud_medida = float(amplitud_str)
            
            error_global = amplitud_medida - amplitud_ref
            
            pasa_prueba = "Pass" if abs(error_global) <= 0.9 else "Fail"
            
            print(f"Frecuencia: {freq} Hz | Medido: {amplitud_medida} dBm | Estado: {pasa_prueba}")
            
            resultados.append([freq, amplitud_medida, error_global, "<= 0.9 dB", pasa_prueba])

    except pyvisa.Error as e:
        print(f"Error de conexión: {e}")

    finally:
        if 'generador' in locals():
            generador.set_rf_output("OFF")
            generador.close()
        if 'analizador' in locals(): analizador.close()
        rm.close()

    if resultados:
        columnas = ["Output Frequency (Hz)", "Measurement Value A3", "Global Error", "Limit", "Pass/Fail"]
        df = pd.DataFrame(resultados, columns=columnas)
        
        nombre_archivo = "amplitude_accuracy_test.csv"
        df.to_csv(nombre_archivo, index=False)
        
        print("\n--- Reporte Final Generado ---")
        print(df.to_string(index=False))