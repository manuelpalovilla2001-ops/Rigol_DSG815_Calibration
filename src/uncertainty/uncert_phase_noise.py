import numpy as np
from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_phase_noise(p1: list, pnoise : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    p1 = A_type_uncertainty(p1, "P1")
    pnoise = A_type_uncertainty(pnoise, "Pnoise")

    # A + B type 
    sa_p1_med = spectral_analyzer_power_uncertainty(p1, SA_config, 
                                                          DSA800_UNCERT['e_abs'],
                                                          0,                            # FR not used. Freq range very low.
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])   # Resolution doesnt apply. Measurment in a specific point in frequency.

    sa_p2_med = spectral_analyzer_power_uncertainty(pnoise, SA_config, 
                                                          DSA800_UNCERT['e_abs'],
                                                          0,                            # FR not used. Freq range very low.
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])   # Resolution doesnt apply. Measurment in a specific point in frequency.

    # Uncertainty of Phase Noise measurement
    pmed = sa_p1_med.val - sa_p2_med.val
    u_m_db = np.sqrt(sa_p1_med.uncert**2 + sa_p2_med.uncert**2)
    m_med = Uncertainty(pmed, u_m_db, "Phase Noise Measurement Uncertainty")

    return m_med

if __name__ == "__main__":
    df = pd.read_csv("test_phase_noise.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. Check

    measure_groups = df.groupby("F")  # TODO. Check names
    real_freq = []
    measure_phase_noise = []
    
    for freq, group in measure_groups:  
        p1 = group['Pcarrier'].tolist()
        pnoise =  group['Valor a 20 kHz'].tolist()
        phase_noise = uncert_phase_noise(p1, pnoise, SA_config)

        real_freq.append(freq)
        measure_phase_noise.append(phase_noise)

    for freq, ph_noise in zip(real_freq, measure_phase_noise):
        print(f"Phase Noise Setting: {freq} Hz | Measured Phase Noise: {ph_noise.val:.2f} dBc | Uncertainty: {ph_noise.uncert:.2f} dB")    


