import numpy as np
from uncert_lib.uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_phase_noise(p1: list, pnoise : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    p1 = A_type_uncertainty(p1, "P1")
    pnoise = A_type_uncertainty(pnoise, "Pnoise")

    # A + B type 
    sa_p1_med = spectral_analyzer_power_uncertainty(p1, 1e9, SA_config, 
                                                          DSA800_UNCERT['e_abs'],
                                                          0,                            # FR not used. Freq range very low.
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])

    sa_pnoise_med = spectral_analyzer_power_uncertainty(pnoise, 1e9, SA_config, 
                                                          DSA800_UNCERT['e_abs'],
                                                          0,                            # FR not used. Freq range very low.
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])

    # Uncertainty of Phase Noise measurement
    pmed = sa_pnoise_med.val - sa_p1_med.val
    u_m_db = np.sqrt(sa_p1_med.uncert**2 + sa_pnoise_med.uncert**2)
    m_med = Uncertainty(pmed, u_m_db, "Phase Noise Measurement Uncertainty")

    return m_med

if __name__ == "__main__":
    df = pd.read_csv("./data/test_phase_noise.csv")
    measure_groups = df.groupby("Nominal Frequency (Hz)")

    check_config = measure_groups[['RBW (Hz)', 'VBW (Hz)', 'SPAN (Hz)', 'Attenuator (dB)', 'Reference Level (dBm)']].nunique(dropna=False)
    if not check_config.eq(1).all().all():
        raise ValueError("No todas las configuraciones son iguales")

    real_freq = []
    measure_phase_noise = []
    
    for freq, group in measure_groups:  
        rbw = group['RBW (Hz)'].iloc[0]
        vbw = group['VBW (Hz)'].iloc[0]
        span = group['SPAN (Hz)'].iloc[0] 
        ref_level = group['Reference Level (dBm)'].iloc[0]
        atte = group['Attenuator (dB)'].iloc[0]
        SA_config = SpectralAnalizerConfig(rbw=rbw, vbw=vbw, span=span, ref_level=ref_level, atte=atte)

        pcarrier = group['Carrier Peak Power (dBm)'].tolist()
        pnoise =  group['Raw Delta Marker at 20kHz (dBc)'].tolist()
        pnoise = pcarrier + pnoise
        phase_noise = uncert_phase_noise(pcarrier, pnoise, SA_config)

        real_freq.append(freq)
        measure_phase_noise.append(phase_noise)

    for freq, ph_noise in zip(real_freq, measure_phase_noise):
        k = 2
        u_expanded = ph_noise.uncert * k
        print(f"Phase Noise Setting: {freq/1e6:>6} MHz | Measured Phase Noise: {ph_noise.val:>6.2f} dBc | Uncertainty: {u_expanded:>6.3g} dB | K: {k} | Confianza: 95%")    


