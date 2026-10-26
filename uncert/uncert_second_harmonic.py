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
    pmed = sa_p2_med.val - sa_p1_med.val
    u_db = np.sqrt(sa_p1_med.uncert**2 + sa_p2_med.uncert**2)

    return Uncertainty(pmed, u_db, "Second Harmonic Measurement Uncertainty")

if __name__ == "__main__":
    df = pd.read_csv("./data/test_second_harmonic.csv")
    measure_groups = df.groupby(["Output Amplitude (dBm)", "Output Frequency (Hz)"])

    check_config = measure_groups[['RBW (Hz)', 'VBW (Hz)', 'SPAN (Hz)', 'Attenuator (dB)', 'Reference Level (dBm)']].nunique(dropna=False)
    if not check_config.eq(1).all().all():
        raise ValueError("No todas las configuraciones son iguales")

    real_set = []
    measure_second_harmonic : list[Uncertainty] = []
    
    for (amp, freq), group in measure_groups:  
        rbw = group['RBW (Hz)'].iloc[0]
        vbw = group['VBW (Hz)'].iloc[0]
        span = group['SPAN (Hz)'].iloc[0] 
        ref_level = group['Reference Level (dBm)'].iloc[0]
        atte = group['Attenuator (dB)'].iloc[0]
        SA_config = SpectralAnalizerConfig(rbw=rbw, vbw=vbw, span=span, ref_level=ref_level, atte=atte)

        p1 = group['Fundamental Power (dBm)'].tolist()
        p_harmonic = group['2nd Harmonic Power (dBm)'].tolist()

        second_harmonic = uncert_second_harmonic(p1, p_harmonic, freq, SA_config)

        real_set.append((amp, freq))
        measure_second_harmonic.append(second_harmonic)

    for (amp, freq), sec_harm in zip(real_set, measure_second_harmonic):
        k = 2
        u_expanded = sec_harm.uncert * k
        print(f"Setting: {{{amp:>2} dB, {freq/1e6:>5} MHz}} | Measured Second Harmonic: {sec_harm.val:.2f} dBc | Uncertainty: {u_expanded:>5.3g} dB | K: {k} | Confianza: 95%")    



