import numpy as np
from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSG800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_second_harmonic(p1: list, p2 : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    p1 = A_type_uncertainty(p1, "P1")
    p2 = A_type_uncertainty(p2, "P Harmonic")

    # A + B type 
    sa_p1_med = spectral_analyzer_power_uncertainty(p1, SA_config, 
                                                          DSG800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSG800_UNCERT['e_rl'],        # TODO chequear si se uso el RL de calibracion o no.
                                                          0,							# Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSG800_UNCERT['e_log'],
                                                          DSG800_UNCERT['e_log_max'],
                                                          0)                            # Resolution doesnt apply. Measurment in a specific point in frequency.

    sa_p2_med = spectral_analyzer_power_uncertainty(p2, SA_config, 
                                                          DSG800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSG800_UNCERT['e_rl'],        # TODO chequear si se uso el RL de calibracion o no.
                                                          0,							# Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSG800_UNCERT['e_log'],
                                                          DSG800_UNCERT['e_log_max'],
                                                          0)                            # Resolution doesnt apply. Measurment in a specific point in frequency.

    # Uncertainty of AM measurement
    pmed = sa_p1_med.val - sa_p2_med.val
    u_m_db = np.sqrt(sa_p1_med.uncert**2 + sa_p2_med.uncert**2)
    m_med = Uncertainty(pmed, u_m_db, "Second Harmonic Measurement Uncertainty")

    return m_med

if __name__ == "__main__":
    df = pd.read_csv("reporte_second_harmonic.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. Check

    measure_groups = df.groupby("Second Harmonic Setting (%)")  # TODO. Check names
    real_freq = []
    measure_second_harmonic = []
    
    for freq, group in df.groupby("FREQ Setting (%)"):  
        p1 = group['Output Amplitude (dBm)'].tolist()
        p2 =  (group['Output Amplitude (dBm)'] + group['Calculation Result (dBc)']).tolist()
        second_harmonic = uncert_second_harmonic(p1, p2, SA_config)

        real_freq.append(freq)
        measure_second_harmonic.append(second_harmonic)

    for freq, sec_harm in zip(real_freq, measure_second_harmonic):
        print(f"Second Harmonic Setting: {freq} Hz | Measured Second Harmonic: {sec_harm.val:.2f} dBc | Uncertainty: {sec_harm.uncert:.2f} dB")    


