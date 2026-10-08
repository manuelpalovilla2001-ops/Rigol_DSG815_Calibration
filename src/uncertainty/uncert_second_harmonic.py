import numpy as np
from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_second_harmonic(p1: list, p_harmonic : list, freq : float, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    p1 = A_type_uncertainty(p1, "P1")
    p_harmonic = A_type_uncertainty(p_harmonic, "P Harmonic")

    # A + B type 
    sa_p1_med = spectral_analyzer_power_uncertainty(p1, freq, SA_config, 
                                                          DSA800_UNCERT['e_abs'],
                                                          DSA800_UNCERT['e_fr'],
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])

    sa_p2_med = spectral_analyzer_power_uncertainty(p_harmonic, 2*freq, SA_config, 
                                                          DSA800_UNCERT['e_abs'],
                                                          DSA800_UNCERT['e_fr'],    
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])

    # Uncertainty of Second Harmonic measurement
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
    
    for freq, group in measure_groups:  
        p1 = group['Output Amplitude (dBm)'].tolist()
        p_harmonic =  (group['Output Amplitude (dBm)'] + group['Calculation Result (dBc)']).tolist()
        second_harmonic = uncert_second_harmonic(p1, p_harmonic, freq, SA_config)

        real_freq.append(freq)
        measure_second_harmonic.append(second_harmonic)

    for freq, sec_harm in zip(real_freq, measure_second_harmonic):
        print(f"Second Harmonic Setting: {freq} Hz | Measured Second Harmonic: {sec_harm.val:.2f} dBc | Uncertainty: {sec_harm.uncert:.2f} dB")    
