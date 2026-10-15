import numpy as np
from uncert_lib.uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_second_harmonic(p1: list, p_harmonic : list, freq : float, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    p1 : Uncertainty = A_type_uncertainty(p1, "P1")
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
    u_db = np.sqrt(sa_p1_med.uncert**2 + sa_p2_med.uncert**2)

    return Uncertainty(pmed, u_db, "Second Harmonic Measurement Uncertainty")

if __name__ == "__main__":
    df = pd.read_csv("./data/reporte_second_harmonic.csv")

    SA_config_amp0 = SpectralAnalizerConfig(rbw=30, vbw=10, span=10e3, ref_level=10, atte=20)
    SA_config2_amp10 = SpectralAnalizerConfig(rbw=30, vbw=10, span=10e3, ref_level=20, atte=30)
    measure_groups = df.groupby(["Output Amplitude (dBm)", "Output Frequency (Hz)"])

    real_set = []
    measure_second_harmonic : list[Uncertainty] = []
    
    for (amp, freq), group in measure_groups:  
        p1 = amp
        p_harmonic = group['Calculation Result (dBc)'].tolist()
        p_harmonic = [pdbc + amp for pdbc in p_harmonic]

        SA_config = SA_config_amp0 if amp == 0 else SA_config2_amp10
        second_harmonic = uncert_second_harmonic(p1, p_harmonic, freq, SA_config)

        real_set.append((amp, freq))
        measure_second_harmonic.append(second_harmonic)

    for (amp, freq), sec_harm in zip(real_set, measure_second_harmonic):
        k = 2
        u_expanded = sec_harm.uncert * k
        print(f"Setting: {{{amp:>2} dB, {freq/1e6:>5} MHz}} | Measured Second Harmonic: {sec_harm.val:.2f} dBc | Uncertainty: {u_expanded:.2g} dB | K: {k} | Confianza: 95%")    



